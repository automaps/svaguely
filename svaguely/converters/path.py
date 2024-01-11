import logging

from typing import Optional, Mapping, Sequence, Union, Callable, List, Iterable

import numpy
import shapely
import svgelements
from jord.shapely_utilities import (
    split_enveloping_geometry,
    overlap_groups,
    opening,
    closing,
    is_multi,
)
from shapely import unary_union
from warg import Number

__all__ = ["path_converter"]
__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"

ASSUME_SUB_PATHS_ARE_HOLES = True


def path_converter(
    item: svgelements.Path,
    w: Number = 1,
    h: Number = 1,
    snap_distance: float = 1e-7,
    step_size: float = 0.1,
) -> Optional[shapely.geometry.base.BaseGeometry]:
    sub_paths = []
    assert 0 < step_size < 1.0, f"{step_size=} was not within range [0..1.0]"
    assert snap_distance > 0
    try:
        points_along_path = []
        for segment in item:
            if isinstance(segment, svgelements.Move):
                if (
                    len(points_along_path) > 0
                ):  # This will only happen if a move was made without a close. We assume this means a new subpath is started
                    sub_paths.append(points_along_path.copy())
                    points_along_path.clear()
                    points_along_path.append(segment.point(1.0))
                else:
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
                    step = min(step, 1.0)
                    points_along_path.append(segment.point(step))

            elif isinstance(segment, svgelements.Close):
                points_along_path.append(segment.point(1.0))
                sub_paths.append(points_along_path.copy())
                points_along_path.clear()
            else:
                raise NotImplementedError(f"{segment=}")

        if len(sub_paths) == 0:
            sub_paths.append(points_along_path.copy())

    except Exception as p:
        logging.error(p)
    was_polygon = []
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
            last_point, tolerance=snap_distance
        ):  # 4
            # coordinates is minimum for a LinearRing, a in simple triangle start and end must the same
            path_points[-1] = first_point
            geoms.append(shapely.geometry.Polygon(path_points))
            was_polygon.append(True)
        elif len(path_points) == 1:
            geoms.append(shapely.geometry.Point(path_points[0]))
            was_polygon.append(False)
        elif len(path_points):
            geoms.append(shapely.geometry.LineString(path_points))
            was_polygon.append(False)
        else:
            logging.warning(f"empty path {path_points=}")

    if ASSUME_SUB_PATHS_ARE_HOLES:
        if len(geoms) > 1:
            if all(was_polygon):
                valid_geom_list = []
                for poly in geoms:
                    if (
                        not poly.is_valid
                    ):  # bowtie issue can occur. Probably some rounding in the coordinates.
                        buffer_in = poly.buffer(
                            -snap_distance, cap_style=3, join_style=2, mitre_limit=2
                        )
                        buffer_out = buffer_in.buffer(
                            snap_distance, cap_style=3, join_style=2, mitre_limit=2
                        )
                        valid_geom_list.append(buffer_out)
                    else:
                        valid_geom_list.append(poly)
                grouped = overlap_groups_contains(
                    valid_geom_list, group_test=shapely.intersects
                )
                output_geoms = []
                for group in grouped:
                    res = split_enveloping_geometry(group.values())
                    if res:
                        envelop, rest = res
                        diff = None

                        if len(rest) > 1:
                            stamped_geometries = recursive_stamping(rest)

                            diff = shapely.difference(
                                envelop, stamped_geometries
                            ).buffer(0)
                        else:
                            try:
                                rest_union = shapely.unary_union(rest).buffer(0)
                                diff = shapely.difference(envelop, rest_union).buffer(0)
                            except Exception as ex:
                                logging.error("UNION ERROR:", ex)

                        if envelop.is_valid:
                            try:
                                if diff.is_valid:
                                    output_geoms.append(diff)
                            except Exception as e:
                                logging.error("PATH ERROR:", e)
                return shapely.unary_union(output_geoms)

    if len(geoms) == 1:
        return geoms[0]

    gc = shapely.GeometryCollection(
        geoms
    )  # If its more than one geometry and its not all polygons (e.g. 1 polygon and 1 linestring), it returns a geometrycollection

    if gc.is_empty:
        logging.warning("PATH PARSING: Geometry collection was empty")
        return None

    return gc


def recursive_stamping(
    geometries: Iterable[shapely.geometry.base.BaseGeometry],
) -> shapely.geometry.base.BaseGeometry:
    """
    Stamping geometries until there is nothing to stamp
    :param geometries: List of shapely geometries
    :return: Union of shapely geometries
    """
    stamped_out_geoms = []
    if len(geometries) <= 1:
        stamped_out_geoms.extend(geometries)
    else:
        groups_of_intersecting_geometries = overlap_groups_contains(
            geometries, group_test=shapely.intersects
        )

        for group in groups_of_intersecting_geometries:
            grouped_geometries = group.values()
            envelop_and_children = split_enveloping_geometry(grouped_geometries)
            if envelop_and_children:
                envelope, rest = envelop_and_children
                if len(rest) < 1:
                    # split geometry only has an envelope, but no rest. Then just append the envelope
                    stamped_out_geoms.append(envelope)
                else:  # If the rest is multiple polygons, we need to stamp them again
                    stamped_out_geoms.append(
                        shapely.difference(envelope, recursive_stamping(rest)).buffer(0)
                    )

            else:  # There was no enveloping geometry
                stamped_out_geoms.extend(grouped_geometries)

    return shapely.unary_union(stamped_out_geoms).buffer(0)


def overlap_groups_contains(
    to_be_grouped: Union[Sequence, Mapping],
    must_be_unique: bool = False,
    group_test: Callable = shapely.intersects,
) -> Sequence[Mapping]:
    if isinstance(to_be_grouped, Mapping):
        ...
    else:
        to_be_grouped = dict(zip((i for i in range(len(to_be_grouped))), to_be_grouped))

    if must_be_unique:
        assert not any(is_multi(p) for p in to_be_grouped.values()), to_be_grouped

    s = list(unary_union(v) for v in to_be_grouped.values())

    union = closing(unary_union(s)).buffer(0)
    groups = []
    already_grouped = []

    if not is_multi(union):
        groups.append(to_be_grouped)
    else:
        for union_part in union.geoms:
            intersectors = {}
            for k, v in to_be_grouped.items():
                if group_test(v, union_part):
                    if must_be_unique:
                        assert k not in already_grouped, f"{k, already_grouped, v}"
                    intersectors[k] = v
                    already_grouped.append(k)
            groups.append(intersectors)

    return groups
