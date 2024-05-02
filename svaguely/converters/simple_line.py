import numpy
import shapely
import svgelements
from shapely import affinity
from warg import Number

__all__ = ["simpleline_converter"]

__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"


def simpleline_converter(
    item: svgelements.SimpleLine, *, w: Number = 1, h: Number = 1
) -> shapely.LineString:
    line_x1 = item.implicit_x1
    line_y1 = h - item.implicit_y1
    line_x2 = item.implicit_x2
    line_y2 = h - item.implicit_y2
    vertice1 = shapely.geometry.Point(line_x1, line_y1)
    vertice2 = shapely.geometry.Point(line_x2, line_y2)
    vertice_list = [vertice1, vertice2]
    linestring = shapely.geometry.LineString(vertice_list)

    angle_simpleline_rad = float(item.rotation)
    angle_degrees = angle_simpleline_rad * (180 / numpy.pi)
    linestring_rotate = affinity.rotate(linestring, angle_degrees, (line_x1, line_y1))
    return linestring_rotate
