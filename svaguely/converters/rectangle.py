# -*- coding: utf-8 -*-
import numpy
import shapely
import svgelements
from shapely import affinity
from warg import Number

__all__ = ["rectangle_converter"]
__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"


def rectangle_converter(
    item: svgelements.Rect, w: Number = 1, h: Number = 1
) -> shapely.Polygon:
  centroid_x = item.implicit_x
  centroid_y = h - item.implicit_y
  width = item.implicit_width
  height = item.implicit_height
  x_min = centroid_x
  x_max = centroid_x + width
  y_min = centroid_y
  y_max = centroid_y - height
  corner_tl = shapely.geometry.Point(x_min, y_max)
  corner_tr = shapely.geometry.Point(x_max, y_max)
  corner_br = shapely.geometry.Point(x_max, y_min)
  corner_bl = shapely.geometry.Point(x_min, y_min)
  Points_list = [corner_tl, corner_tr, corner_br, corner_bl, corner_tl]
  linestring_rect = shapely.geometry.LineString(Points_list)

  angle_rectangle_rad = float(item.rotation)
  angle_degrees = -1 * (angle_rectangle_rad * (180 / numpy.pi))
  linestring_rect_rotate = affinity.rotate(
    linestring_rect, angle_degrees, (centroid_x, centroid_y)
  )
  polygonize_rect = shapely.geometry.Polygon(linestring_rect_rotate)
  return polygonize_rect
