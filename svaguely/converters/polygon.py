import numpy
import shapely
import svgelements
from shapely import affinity
from warg import Number

__all__ = ["polygon_converter"]

__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"


def polygon_converter(
    item: svgelements.Polygon, w: Number = 1, h: Number = 1
) -> shapely.geometry.base.BaseGeometry:
    area_points = item.points
    rotate_x = area_points[0].x
    rotate_y = h - area_points[0].y

    area_list_points = []
    for points in area_points:
        x_coord = points.x
        y_coord = h - points.y
        point = shapely.geometry.Point(x_coord, y_coord)
        area_list_points.append(point)

    if len(area_list_points) < 4:
        area_list_points.append(area_list_points[0])

    area_linestring = shapely.LinearRing(area_list_points)

    angle_polygon_rad = float(item.rotation)
    angle_degrees = angle_polygon_rad * (180 / numpy.pi)
    rotated_geom = affinity.rotate(area_linestring, angle_degrees, (rotate_x, rotate_y))

    if not rotated_geom.is_valid:
        rotated_geom = rotated_geom.buffer(0)

    if rotated_geom.is_ring:
        out_geom = shapely.geometry.Polygon(rotated_geom)
    else:
        out_geom = shapely.unary_union(rotated_geom)

    return out_geom
