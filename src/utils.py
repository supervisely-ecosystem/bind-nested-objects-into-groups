import math
import numpy as np
from supervisely.annotation.label import Label
from supervisely.geometry.geometry import Geometry
from supervisely.geometry.point import Point
from supervisely.geometry.polyline import Polyline
from supervisely.geometry.rectangle import Rectangle
from supervisely.geometry.graph import GraphNodes
from supervisely.metric.common import safe_ratio


def get_polyline_length(polyline: Polyline):
    length = 0
    prev = (polyline.exterior[0].row, polyline.exterior[0].col)
    for point in polyline.exterior[1:]:
        row, col = point.row, point.col
        segment_length_sq = (prev[0] - row) ** 2 + (prev[1] - col) ** 2
        length += math.sqrt(segment_length_sq)
        prev = (row, col)
    return length


def get_intersection_over_first_rect(
    rect: Rectangle, other: Geometry, rect_is_first=True
):
    maybe_other_cropped = other.crop(rect)
    if len(maybe_other_cropped) == 0:
        return 0.0
    else:
        if isinstance(other, Point):
            intersection_area = 1
            other_area = 1
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
        return safe_ratio(intersection_area, first_area)


def get_geometries_intersection_over_first(geometry_1: Geometry, geometry_2: Geometry):
    if isinstance(geometry_1, GraphNodes):
        geometry_1 = geometry_1.to_bbox()
    if isinstance(geometry_2, GraphNodes):
        geometry_2 = geometry_2.to_bbox()
    if isinstance(geometry_1, Rectangle):
        return get_intersection_over_first_rect(geometry_1, geometry_2, True)
    elif isinstance(geometry_2, Rectangle):
        return get_intersection_over_first_rect(geometry_2, geometry_1, False)
    else:
        common_bbox = Rectangle.from_geometries_list((geometry_1, geometry_2))
        g1 = geometry_1.relative_crop(common_bbox)
        g2 = geometry_2.relative_crop(common_bbox)
        mask_1 = np.full(common_bbox.to_size(), False)
        for g in g1:
            g.draw(mask_1, color=True)
        mask_2 = np.full(common_bbox.to_size(), False)
        for g in g2:
            g.draw(mask_2, color=True)
        return safe_ratio((mask_1 & mask_2).sum(), mask_1.sum())


def get_labels_intersection_over_first(label_1: Label, label_2: Label, img_size=None):
    return get_geometries_intersection_over_first(label_1.geometry, label_2.geometry)
