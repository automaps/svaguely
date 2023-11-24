# -*- coding: utf-8 -*-

import shapely
import svgelements
from warg import Number

__all__ = ["circle_converter"]


def circle_converter(
    item: svgelements.Circle, w: Number = 1, h: Number = 1
) -> shapely.Polygon:
    cx = item.cx
    cy = h - item.cy
    r = item.implicit_r
    circle_polygon = shapely.geometry.Point([cx, cy]).buffer(distance=r)
    circle_coords = circle_polygon.exterior.coords
    circle_linestr = shapely.geometry.LineString(circle_coords)
    polygonize_circ = shapely.geometry.Polygon(circle_linestr)

    return polygonize_circ
