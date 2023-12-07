# -*- coding: utf-8 -*-
from typing import Union

import numpy
import shapely
import svgelements
from shapely import affinity
from warg import Number

__all__ = ["polyline_converter"]
__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"


def polyline_converter(
    item: svgelements.Polyline, w: Number = 1, h: Number = 1, EPSILON=0.00000000001
) -> Union[shapely.Polygon, shapely.LineString]:
  polyline_points = item.points
  rotate_x = polyline_points[0].x
  rotate_y = h - polyline_points[0].y

  polyline_list_points = []
  for points in polyline_points:
    x_coord = points.x
    y_coord = h - points.y
    point = shapely.geometry.Point(x_coord, y_coord)
    polyline_list_points.append(point)

  last_point = polyline_list_points[-1]
  first_point = polyline_list_points[0]
  if first_point.equals_exact(last_point, tolerance=EPSILON):
    polyline_list_points[-1] = polyline_list_points[0]
    path_geometry = shapely.geometry.Polygon(polyline_list_points)
  else:
    path_geometry = shapely.geometry.LineString(polyline_list_points)

  angle_polyline_rad = float(item.rotation)
  angle_degrees = angle_polyline_rad * (180 / numpy.pi)
  polyline_geometry_rotate = affinity.rotate(
    path_geometry, angle_degrees, (rotate_x, rotate_y)
  )

  return polyline_geometry_rotate
