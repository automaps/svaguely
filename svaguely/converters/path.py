# -*- coding: utf-8 -*-
import logging

import numpy
import shapely
import svgelements
from jord.shapely_utilities import split_enveloping_geometry, overlap_groups
from warg import Number

__all__ = ["path_converter"]
__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"

ASSUME_SUB_PATHS_ARE_HOLES = True


def path_converter(
    item: svgelements.Path,
    w: Number = 1,
    h: Number = 1,
    EPSILON: float = 1e-11,
    step_size: float = 0.1,
) -> shapely.GeometryCollection:
    sub_paths = []

    try:
        points_along_path = []
        for segment in item:
            if isinstance(segment, svgelements.Move):
                points_along_path.append(segment.point(0.0))

            elif isinstance(segment, svgelements.Line):
                points_along_path.append(segment.point(1.0))

            elif isinstance(
                segment,
                (svgelements.Arc, svgelements.CubicBezier, svgelements.QuadraticBezier),
            ):
                for step in numpy.arange(
                    step_size, 1.0 + step_size, step_size, dtype=float
                ):
                    points_along_path.append(segment.point(step))

            elif isinstance(segment, svgelements.Close):
                points_along_path.append(segment.point(1.0))
                sub_paths.append(points_along_path.copy())
                points_along_path.clear()

            else:
                raise NotImplementedError(f"{segment=}")

    except Exception as p:
        logging.error(p)

    geoms = []
    for sp in sub_paths:
        path_points = []
        for point in sp:
            x_coord = point.x
            y_coord = h - point.y
            path_points.append(shapely.geometry.Point(x_coord, y_coord))

        last_point = path_points[-1]
        first_point = path_points[0]

        if len(path_points) >= 4 and first_point.equals_exact(
            last_point, tolerance=EPSILON
        ):  # 4
            # coordinates is minimum for a LinearRing, a in simple triangle start and end must the same
            path_points[-1] = path_points[0]
            geoms.append(shapely.geometry.Polygon(path_points))
        elif len(path_points) == 1:
            geoms.append(shapely.geometry.Point(path_points[0]))
        elif len(path_points):
            geoms.append(shapely.geometry.LineString(path_points))
        else:
            logging.warning(f"empty path {path_points=}")

    if ASSUME_SUB_PATHS_ARE_HOLES:
        if len(geoms) > 1:
            grouped = overlap_groups(geoms)
            if grouped > 1:
                print("bla then we have to do sth!")
            res = split_enveloping_geometry(geoms)
            if res:
                envelop, rest = res
                new_rest_list = []
                for poly in rest:
                    valid_poly = shapely.make_valid(poly)
                    new_rest_list.append(valid_poly)
                try:
                    rest_union = shapely.unary_union(new_rest_list).buffer(0)
                except Exception as ex:
                    print("UNION ERROR:", ex)
                if envelop.is_valid:
                        try:
                            diff = shapely.difference(
                                envelop, rest_union
                            ).buffer(0)
                            if diff.is_valid:
                                return diff
                        except Exception as e:
                            print("PATH ERROR:", e)

    return shapely.GeometryCollection(geoms)
