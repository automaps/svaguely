# -*- coding: utf-8 -*-
import logging
from itertools import count
from typing import Dict

import svgelements

from .converters import (
    circle_converter,
    point_converter,
    path_converter,
    polyline_converter,
    polygon_converter,
    rectangle_converter,
    simpleline_converter,
)
from .data_models import SvgShapelyGeometry


def convert_elements(group: svgelements.Group) -> Dict[str, SvgShapelyGeometry]:
    return_dict = {}
    name_counter = iter(count())

    for item in group:
        item_type = type(item)
        item_filled = False
        item_fill_colour = None

        if hasattr(item, "fill"):
            if item.fill.value is not None:
                item_filled = True
            if item.fill.hex:
                item_fill_colour = item.fill.hex

        if hasattr(item, "id") and item.id:
            shape_name = item.id
        else:
            shape_name = f"NoName{next(name_counter)}"

        if isinstance(item, svgelements.Group):
            return_dict[shape_name] = convert_elements(item)
            continue

        if hasattr(item, "values") and "class" in item.values.keys():
            item_value_class = item.values["class"]
        else:
            item_value_class = None

        if isinstance(item, svgelements.Rect):
            shape_geometry = rectangle_converter(item)

        elif isinstance(item, svgelements.SimpleLine):
            shape_geometry = simpleline_converter(item)

        elif isinstance(item, svgelements.Polyline):
            shape_geometry = polyline_converter(item)

        elif isinstance(item, svgelements.Polygon):
            shape_geometry = polygon_converter(item)
        elif isinstance(item, svgelements.Point):
            shape_geometry = point_converter(item)
        elif isinstance(item, svgelements.Circle):
            if False:
                e = svgelements.Path(item)
                e = e.reify()
                shape_geometry = path_converter(e)
            else:
                shape_geometry = circle_converter(item)
        elif isinstance(item, (svgelements.Ellipse, svgelements.Curve)):
            e = svgelements.Path(item)
            e_reified = e.reify()
            shape_geometry = path_converter(e_reified)

        elif isinstance(item, svgelements.Path):
            shape_geometry = path_converter(item)

        elif isinstance(item, svgelements.Text):
            logging.warning(f"Text is not a supported class: {f'{item=} {type(item)}'}")
            continue  # TODO: Handle text
        else:
            logging.warning(f"Not supported class: {f'{item=} {type(item)}'}")
            continue

        return_dict[shape_name] = SvgShapelyGeometry(
            shape_name,
            shape_geometry,
            item_value_class,
            item_type,
            item_filled,
            item_fill_colour,
        )

    return return_dict
