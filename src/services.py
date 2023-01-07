from typing import List
import supervisely as sly
import src.utils as utils
import src.globals as g


def _get_relations(parents, childs, threshold):
    relations = {}
    is_child = set()
    for ch_idx, ch_el in enumerate(childs):
        for par_idx, par_el in enumerate(parents):
            if ch_idx in is_child:
                break
            score = utils.get_labels_intersection_over_first(ch_el, par_el)
            if score >= threshold:
                is_child.add(ch_idx)
                if par_idx in relations:
                    if not ch_idx in relations[par_idx]:
                        relations[par_idx].append(ch_idx)
                else:
                    relations[par_idx] = [ch_idx]
    return relations


def _add_tag_to_label(label: sly.Label, tag: sly.Tag):
    if (
        len(tag.meta.applicable_classes) == 0
        or label.obj_class.name in tag.meta.applicable_classes
    ):
        if label.tags.has_key(tag.key()):
            existing = label.tags.get_all(tag.key())
            label = label.clone(tags=label.tags.difference(existing))
        label = label.add_tag(tag)
    return label


def _get_parents_idxs(labels: List[sly.Label]):
    parents_idxs = []
    for i, label in enumerate(labels):
        obj_name = label.obj_class.name
        if obj_name in g.parents_names:
            parents_idxs.append(i)
    return parents_idxs


def _get_childs_idxs(labels: List[sly.Label]):
    childs_idxs = []
    for i, label in enumerate(labels):
        obj_name = label.obj_class.name
        if label.binding_key is None and obj_name in g.childs_names:
            childs_idxs.append(i)
    return childs_idxs


def _get_updated_labels(
    labels: List[sly.Label], parents_idxs: List[int], tag_no_child: sly.Tag
):
    first = []
    last = []
    for i, label in enumerate(labels):
        if label.binding_key == str(label.to_json()["id"]):
            last.append(label)
        else:
            if tag_no_child is not None and i in parents_idxs:
                label = _add_tag_to_label(label, tag_no_child)
            first.append(label)
    return [*first, *last]


def bind_nested_objects_on_image(image_id: int, tag_no_child: sly.Tag = None):
    ann_json = g.api.annotation.download_json(image_id)
    ann = sly.Annotation.from_json(ann_json, g.project_meta)

    parents_idxs = _get_parents_idxs(ann.labels)
    childs_idxs = _get_childs_idxs(ann.labels)

    relations = _get_relations(
        [ann.labels[i] for i in parents_idxs],
        [ann.labels[i] for i in childs_idxs],
        g.threshold,
    )

    for parent_idx, childs_idxs in relations.items():
        key = str(ann.labels[parents_idxs[parent_idx]].to_json()["id"])
        ann.labels[parents_idxs[parent_idx]].binding_key = key
        for idx in childs_idxs:
            ann.labels[childs_idxs[idx]].binding_key = key

    updated_labels = _get_updated_labels(ann.labels, parents_idxs, tag_no_child)
    for label in ann.labels:
        ann = ann.delete_label(label)
    ann = ann.add_labels(updated_labels)
    g.api.annotation.upload_ann(image_id, ann)
