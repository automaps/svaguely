import logging
from typing import Optional, Sequence

import numpy
import shapely
import svgelements
from jord.shapely_utilities import (
    clean_shape,
    closing,
    overlap_groups,
    split_enveloping_geometry,
)
from warg import Number

__all__ = ["path_converter"]
__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"

ASSUME_SUB_PATHS_ARE_HOLES = True

logger = logging.getLogger(__name__)


def path_converter(
    item: svgelements.Path,
    *,
    w: Number = 1,
    h: Number = 1,
    snap_distance: float = 1e-7,
    step_size: float = 0.1,
) -> Optional[shapely.geometry.base.BaseGeometry]:
    sub_paths = []  # TODO: REWRITE TO USE .as_subpaths() instead

    assert h == w, "w and h must be the same"

    assert 0 < step_size < 1.0, f"{step_size=} was not within range [0..1.0]"
    assert snap_distance >= 0
    try:
        points_along_path = []
        for segment in item:
            if isinstance(segment, svgelements.Move):
                if (
                    len(points_along_path) > 0
                ):  # This will only happen if a move was made without a close. We assume this means a new subpath
                    # is started
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

        if len(points_along_path) > 0 or len(sub_paths) == 0:
            sub_paths.append(points_along_path.copy())
            points_along_path.clear()

    except Exception as p:
        logger.error(p)

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
            logger.warning(f"empty path {path_points=}")

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

                grouped = overlap_groups(valid_geom_list)

                output_geoms = []
                for group in grouped:
                    res = split_enveloping_geometry(group.values())
                    if res:
                        envelop, rest = res
                        diff = None

                        if len(rest) > 1:
                            stamped_geometries = recursive_stamping(rest)

                            diff = clean_shape(
                                shapely.difference(envelop, stamped_geometries)
                            )

                        elif len(rest) == 0:
                            diff = envelop
                        else:
                            try:
                                rest_union = clean_shape(shapely.unary_union(rest))
                                diff = clean_shape(
                                    shapely.difference(envelop, rest_union)
                                )
                            except Exception as ex:
                                logger.error("UNION ERROR:", ex)

                        if envelop.is_valid:
                            try:
                                if diff.is_valid:
                                    output_geoms.append(diff)
                            except Exception as e:
                                logger.error("PATH ERROR:", e)
                        else:
                            logger.warning("PATH PARSING: Envelope was not valid")

                    else:  # FALL BACK... TODO: FIGURE OUT A PROPER SOLUTION!, RIGHT NOW JUST ADD ALL GEOMS
                        output_geoms.extend(group.values())

                return closing(
                    shapely.unary_union(output_geoms), distance=snap_distance
                )

    if len(geoms) == 1:
        return geoms[0]

    gc = shapely.GeometryCollection(
        geoms
    )  # If its more than one geometry and its not all polygons (e.g. 1 polygon and 1 linestring),
    # it returns a geometrycollection

    if gc.is_empty:
        logger.warning("PATH PARSING: Geometry collection was empty")

        return None

    return gc


def recursive_stamping(
    geometries: Sequence[shapely.geometry.base.BaseGeometry],
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
        groups_of_intersecting_geometries = overlap_groups(geometries)

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
                        clean_shape(
                            shapely.difference(envelope, recursive_stamping(rest))
                        )
                    )

            else:  # There was no enveloping geometry
                stamped_out_geoms.extend(grouped_geometries)

    return clean_shape(shapely.unary_union(stamped_out_geoms))
