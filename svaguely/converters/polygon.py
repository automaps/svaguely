# -*- coding: utf-8 -*-
import numpy
import shapely
import svgelements
from shapely import affinity
from warg import Number

__all__ = ["polygon_converter"]


def polygon_converter(
    item: svgelements.Polygon, w: Number = 1, h: Number = 1
) -> shapely.Polygon:
    area_points = item.points
    rotate_x = area_points[0].x
    rotate_y = h - area_points[0].y

    area_list_points = []
    for points in area_points:
        x_coord = points.x
        y_coord = h - points.y
        point = shapely.geometry.Point(x_coord, y_coord)
        area_list_points.append(point)
    Area_linestring = shapely.geometry.LineString(area_list_points)

    angle_polygon_rad = float(item.rotation)
    angle_degrees = angle_polygon_rad * (180 / numpy.pi)
    area_polygon_rotate = affinity.rotate(
        Area_linestring, angle_degrees, (rotate_x, rotate_y)
    )

    area_polygon = shapely.geometry.Polygon(area_polygon_rotate)
    return area_polygon
