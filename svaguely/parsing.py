# -*- coding: utf-8 -*-
import json
from itertools import count
from pathlib import Path
from typing import Mapping, Tuple

import svgelements

from .element_to_shape import *
from .metadata import METADATA_KEY

from .data_models import SvgShapelyGeometry

normalised_coords = True
if normalised_coords:
    w = h = 1
else:
    w = h = 1000


__all__ = ["flatten_groups", "parse_svg"]


def flatten_groups(geoms: Mapping) -> Mapping:
    out_dict = {}
    for k, v in geoms.items():
        if isinstance(v, Mapping):
            out_dict.update(**{f"{k}_{ki}": vi for ki, vi in flatten_groups(v).items()})
        else:
            out_dict[k] = v

    return out_dict


def parse_svg(svg_path: Path) -> Tuple:
    """
    Main function of converting. This reads the svg and parses it.
    Then converts the svgelements into classes with shapely geometries.

    :param svg_path: Path to the svg
    :return: dataclass of svg elements and dataclass of metadata
    """
    svg = svgelements.SVG.parse(
        svg_path,
        reify=True,
        ppi=svgelements.DEFAULT_PPI,
        width=w,
        height=h,
        color="black",
        transform=None,
        context=None,
    )

    groups = {}

    if len(svg) == 1:
        svg_groups = svg[0]
    else:
        svg_groups = svg

    metadata_dict = None

    for group in svg_groups:
        if isinstance(group, svgelements.Desc):  # extract metadata
            if group.id == METADATA_KEY:  # check if its our description metadata
                assert metadata_dict is None
                metadata_dict = json.loads(
                    group.values["attributes"]["desc"].replace("'", '"')
                )

        else:
            groups[group.id] = convert_elements(group)

    floorplan_for_export = flatten_groups(groups)

    return floorplan_for_export, metadata_dict


def convert_elements(group: svgelements.Group) -> Mapping:
    return_dict = {}
    name_counter = iter(count())

    for item in group:
        item_type = type(item)
        item_filled = False

        if hasattr(item, "fill"):
            if item.fill.value is not None:
                item_filled = True

        if hasattr(item, "id") and item.id:
            item_name = item.id
        else:
            item_name = f"NoName{next(name_counter)}"

        if isinstance(item, svgelements.Group):
            return_dict[item_name] = convert_elements(item)
            continue

        if hasattr(item, "values") and "class" in item.values.keys():
            item_value_class = item.values["class"]
        else:
            item_value_class = None

        if isinstance(item, svgelements.Rect):
            item_contents = rectangular_function(item)

        elif isinstance(item, svgelements.SimpleLine):
            item_contents = simpleline_function(item)

        elif isinstance(item, svgelements.Polyline):
            item_contents = polyline_function(item)

        elif isinstance(item, svgelements.Polygon):
            item_contents = polygon_function(item)
        elif isinstance(item, svgelements.Point):
            item_contents = point_function(item)
        elif isinstance(item, svgelements.Circle):
            if False:
                e = svgelements.Path(item)
                e = e.reify()
                item_contents = path_function(e)
            else:
                item_contents = circle_function(item)
        elif isinstance(item, svgelements.Ellipse):
            e = svgelements.Path(item)
            e_reified = e.reify()
            item_contents = path_function(e_reified)

        elif isinstance(item, svgelements.Path):
            item_contents = path_function(item)

        elif isinstance(item, svgelements.Text):
            continue
        else:
            print("Not supported class: {}".format(f"{item=} {type(item)}"))
            continue

        return_dict[item_name] = SvgShapelyGeometry(
            item_name, item_contents, item_value_class, item_type, item_filled
        )

    return return_dict
