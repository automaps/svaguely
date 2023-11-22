# -*- coding: utf-8 -*-
from typing import Union

import numpy
import shapely
import svgelements
from shapely import affinity

normalised_coords = True
if normalised_coords:
    w = h = 1
else:
    w = h = 1000

__all__ = [
    "rectangular_function",
    "simpleline_function",
    "polyline_function",
    "polygon_function",
    "path_function",
    "circle_function",
]

EPSILON = 0.00000000001


def rectangular_function(item: svgelements.Rect) -> shapely.Polygon:
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


def simpleline_function(item: svgelements.SimpleLine) -> shapely.LineString:
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


def polyline_function(
    item: svgelements.Polyline,
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


def polygon_function(item: svgelements.Polygon) -> shapely.Polygon:
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


def point_function(item: svgelements.Point) -> shapely.Point:
    cx = item.x
    cy = h - item.y

    return shapely.geometry.Point([cx, cy])


def circle_function(item: svgelements.Circle) -> shapely.Polygon:
    cx = item.cx
    cy = h - item.cy
    r = item.implicit_r
    circle_polygon = shapely.geometry.Point([cx, cy]).buffer(distance=r)
    circle_coords = circle_polygon.exterior.coords
    circle_linestr = shapely.geometry.LineString(circle_coords)
    polygonize_circ = shapely.geometry.Polygon(circle_linestr)

    return polygonize_circ


def path_function(item: svgelements.Path) -> shapely.geometry.base.BaseGeometry:
    try:
        point_along_path = []
        for segment in item:
            if isinstance(segment, svgelements.Move):
                point_along_path.append(segment.point(0))
            elif isinstance(segment, svgelements.Line):
                point_along_path.append(segment.point(1))
            elif isinstance(
                segment,
                (svgelements.Arc, svgelements.CubicBezier, svgelements.QuadraticBezier),
            ):
                for step in numpy.arange(0.1, 1.1, 0.1):
                    point_along_path.append(segment.point(step))

            elif isinstance(segment, svgelements.Close):
                point_along_path.append(segment.point(1))
            else:
                raise NotImplementedError(f"{segment=}")
    except Exception as p:
        print(p)
        return

    path_points = []
    for point in point_along_path:
        x_coord = point.x
        y_coord = h - point.y
        point = shapely.geometry.Point(x_coord, y_coord)
        path_points.append(point)

    last_point = path_points[-1]
    first_point = path_points[0]

    if len(path_points) >= 4 and first_point.equals_exact(
        last_point, tolerance=EPSILON
    ):  # 4
        # coordinates is minimum for a LinearRing, a in simple triangle start and end must the same
        path_points[-1] = path_points[0]
        path_geometry = shapely.geometry.Polygon(path_points)
        return path_geometry
    elif len(path_points) == 1:
        path_geometry = shapely.geometry.Point(path_points[0])
        return path_geometry
    elif len(path_points):
        path_geometry = shapely.geometry.LineString(path_points)
        return path_geometry
    else:  # TODO: Handle geometriCollection and MultiGeoms
        print(f"empty path {path_points=}")
