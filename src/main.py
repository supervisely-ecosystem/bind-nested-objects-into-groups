import math
import os
import json
from dotenv import load_dotenv
import src.config as config
import supervisely as sly
from supervisely.annotation.label import Label
from supervisely.geometry.point import Point
from supervisely.geometry.polyline import Polyline
from supervisely.metric.matching import *
import numpy as np
import cv2 as cv


def get_polyline_length(polyline: Polyline):
    length_sq = 0
    prev = (polyline.exterior[0].row, polyline.exterior[0].col)
    for point in polyline.exterior[1:]:
        row, col = point.row, point.col
        length_sq += (prev[0] - row) ** 2 + (prev[1] - col) ** 2
        prev = (row, col)
    return math.sqrt(length_sq)


def get_intersection_over_first_rect(
    rect: Rectangle, other: Geometry, rect_is_first=True
):
    maybe_other_cropped = other.crop(rect)
    if len(maybe_other_cropped) == 0:
        return 0.0
    else:
        if isinstance(other, Point):
            if rect_is_first:
                rect.area
            else:
                return 1.0
        if isinstance(other, Polyline):
            intersection_area = sum(
                get_polyline_length(part) for part in maybe_other_cropped
            )
            other_area = get_polyline_length(other)
        else:
            intersection_area = sum(f.area for f in maybe_other_cropped)
            other_area = other.area
        if intersection_area == 0:
            return 0.0
        if rect_is_first:
            first_area = rect.area
        else:
            first_area = other_area
        return intersection_area / first_area


def get_geometries_intersection_over_first(geometry_1: Geometry, geometry_2: Geometry):
    if isinstance(geometry_1, Rectangle):
        return get_intersection_over_first_rect(geometry_1, geometry_2, True)
    elif isinstance(geometry_2, Rectangle):
        return get_intersection_over_first_rect(geometry_2, geometry_1, False)
    else:
        common_bbox = Rectangle.from_geometries_list((geometry_1, geometry_2))
        g1 = geometry_1.relative_crop(common_bbox)[0]
        g2 = geometry_2.relative_crop(common_bbox)[0]
        mask_1 = np.full(common_bbox.to_size(), False)
        g1.draw(mask_1, color=True)
        mask_2 = np.full(common_bbox.to_size(), False)
        g2.draw(mask_2, color=True)
        return safe_ratio((mask_1 & mask_2).sum(), mask_1.sum())


def get_labels_intersection_over_first(label_1: Label, label_2: Label, img_size=None):
    return get_geometries_intersection_over_first(label_1.geometry, label_2.geometry)


def get_relations(parents, childs, threshold):
    relations = {}
    parents_n = len(parents)
    childs_n = len(childs)
    relations_map = []
    for _ in range(parents_n):
        relations_map.append([0] * childs_n)

    is_child = set()
    scored_idx_pairs = []
    for ch_idx, ch_el in enumerate(childs):
        for par_idx, par_el in enumerate(parents):
            if ch_idx in is_child:
                break
            pair_with_score = IndexPairWithScore(
                idx_1=ch_idx,
                idx_2=par_idx,
                score=get_labels_intersection_over_first(ch_el, par_el),
            )
            if pair_with_score.score >= threshold:
                scored_idx_pairs.append(pair_with_score)
                is_child.add(ch_idx)

    for (idx_1, idx_2, score) in scored_idx_pairs:
        relations_map[idx_2][idx_1] = score

    print("relations_map: ")
    print("\t" + ", ".join(str(i) for i in range(len(childs))))
    for i, row in enumerate(relations_map):
        print(i, "\t:", ", ".join([str(x) for x in row]))

    for parent_idx in range(parents_n):
        for child_idx in range(childs_n):
            score = relations_map[parent_idx][child_idx]
            if score < threshold:
                continue
            if parent_idx in relations:
                s = set(relations[parent_idx])
                s.add(child_idx)
                relations[parent_idx] = list(s)
            else:
                relations[parent_idx] = [child_idx]
    return relations


def bind_nested_objects_on_image(
    api: sly.Api, project_meta: sly.ProjectMeta, image_id: int
):

    ann_json = api.annotation.download_json(image_id)
    ann = sly.Annotation.from_json(ann_json, project_meta)

    parents = []
    childs = []
    skipped = []
    for id, label in enumerate(ann.labels):
        if label.binding_key is None:
            if label.obj_class.name in config.PARENT_NAMES:
                parents.append(id)
            elif label.obj_class.name in config.CHILD_NAMES:
                childs.append(id)
            else:
                skipped.append(id)
        else:
            skipped.append(id)

    print("labels:")
    print("parents: ", [ann.labels[i].obj_class.name for i in parents])
    print("childs: ", [ann.labels[i].obj_class.name for i in childs])
    print("skipped: ", [ann.labels[i].obj_class.name for i in skipped])

    relations = get_relations(
        [ann.labels[i] for i in parents],
        [ann.labels[i] for i in childs],
        config.THRESHOLD,
    )
    print(json.dumps(relations, indent=2))
    print()

    for parent_idx, childs_idxs in relations.items():
        key = str(ann.labels[parents[parent_idx]].to_json()["id"])
        ann.labels[parents[parent_idx]].binding_key = key
        for idx in childs_idxs:
            ann.labels[childs[idx]].binding_key = key

    updated_labels = [
        *[ann.labels[idx] for idx in skipped],
        *[ann.labels[idx] for idx in childs],
        *[ann.labels[idx] for idx in parents],
    ]

    for label in ann.labels:
        ann = ann.delete_label(label)
    ann = ann.add_labels(updated_labels)
    api.annotation.upload_ann(image_id, ann)


def clear_bindings_on_image(api: sly.Api, project_meta: sly.ProjectMeta, image_id: int):
    ann_json = api.annotation.download_json(image_id)
    ann = sly.Annotation.from_json(ann_json, project_meta)
    for i in range(len(ann.labels)):
        ann.labels[i].binding_key = None
    api.annotation.upload_ann(image_id, ann)


if __name__ == "__main__":
    if sly.is_development():
        load_dotenv("local.env")
        load_dotenv(os.path.expanduser("~/supervisely.env"))
    api = sly.Api()
    project_id = sly.env.project_id()
    project_meta_json = api.project.get_meta(project_id)
    project_meta = sly.ProjectMeta.from_json(project_meta_json)

    # image_id = config.IMAGE_ID
    # bind_nested_objects_on_image(api, project_meta, image_id)

    datasets = api.dataset.get_list(project_id)
    for dataset in datasets:
        images = api.image.get_list(dataset.id)
        for image in images:
            print("image id: ", image.id)
            bind_nested_objects_on_image(api, project_meta, image.id)
