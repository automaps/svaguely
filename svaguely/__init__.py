import logging
from itertools import count
from typing import Dict, Optional

import svgelements
from warg import Number

from .conversion import (
    circle_converter,
    image_converter,
    path_converter,
    point_converter,
    polygon_converter,
    polyline_converter,
    rectangle_converter,
    simpleline_converter,
    text_converter,
)
from .data_models import SvgShapelyGeometry

from pathlib import Path
import toml


from .conversion import *
from .data_models import *
from .metadata import *
from .parsing import *

__project__ = "Svaguely"
__doc__ = """\
Svaguely is a Python package for converting svg elements into shapely geometries
"""
__author__ = None
__version__ = "0.0.2"

PROJECT_NAME = __project__
PROJECT_YEAR = 2023
PROJECT_ORGANISATION = "MapsPeople"

# SET PROJECT_VERSION and PROJECT_AUTHOR
pyproject_toml_file = Path(__file__).parent.parent.parent / "pyproject.toml"
if pyproject_toml_file.exists() and pyproject_toml_file.is_file():
    data = toml.load(pyproject_toml_file)
    PROJECT_VERSION = data["tool"]["poetry"]["version"]
    PROJECT_AUTHOR = ", ".join(data["tool"]["poetry"]["authors"])

    __author__ = PROJECT_AUTHOR


logger = logging.getLogger(__name__)


__all__ = ["convert_elements"]


def convert_elements(
    element: svgelements.Group,
    *,
    w: Optional[Number] = 1,
    h: Optional[Number] = 1,
    name_seperator: str = "|",
) -> Dict[str, SvgShapelyGeometry]:
    return_dict = {}
    name_counter = iter(count())

    if not isinstance(element, svgelements.Group):
        element = [element]

    for item in element:
        item_type = type(item)
        item_filled = False
        item_fill_colour = None
        extras = {}

        if hasattr(item, "fill"):
            if item.fill.value is not None:
                item_filled = True

            if item.fill.hex:
                item_fill_colour = item.fill.hex

        if False:
            shape_name = f"{element.id}{name_seperator}"
        else:
            shape_name = ""

        if hasattr(item, "id") and item.id:
            shape_name += f"{item.id}"
        else:
            shape_name += f"NoName{next(name_counter)}"

        if isinstance(item, svgelements.Group):
            return_dict[shape_name] = convert_elements(item, w=w, h=h)
            continue

        if hasattr(item, "values") and "class" in item.values.keys():
            item_value_class = item.values["class"]
        else:
            item_value_class = None

        if isinstance(item, svgelements.Rect):
            shape_geometry = rectangle_converter(item, w=w, h=h)

        elif isinstance(item, svgelements.SimpleLine):
            shape_geometry = simpleline_converter(item, w=w, h=h)

        elif isinstance(item, svgelements.Polyline):
            shape_geometry = polyline_converter(item, w=w, h=h)

        elif isinstance(item, svgelements.Polygon):
            shape_geometry = polygon_converter(item, w=w, h=h)

        elif isinstance(item, svgelements.Point):
            shape_geometry = point_converter(item, w=w, h=h)

        elif isinstance(item, svgelements.Circle):
            if False:
                e = svgelements.Path(item)
                e = e.reify()
                shape_geometry = path_converter(e, w=w, h=h)
            else:
                shape_geometry = circle_converter(item, w=w, h=h)

        elif isinstance(item, (svgelements.Ellipse, svgelements.Curve)):
            e = svgelements.Path(item)
            e_reified = e.reify()
            shape_geometry = path_converter(e_reified, w=w, h=h)

        elif isinstance(item, svgelements.Path):
            shape_geometry = path_converter(item, w=w, h=h)

        elif isinstance(item, svgelements.Text):
            # Text objects. The lack of a font engine makes this class more of a parsed stub class.
            shape_geometry, text_content, font_meta_data = text_converter(
                item, w=w, h=h
            )
            extras["text"] = text_content
            extras["font"] = font_meta_data

        elif isinstance(item, svgelements.Pattern):
            ...  # Pattern objects. These are parsed they are not currently assigned.

        elif isinstance(item, svgelements.Image):
            shape_geometry, image_content = image_converter(item, w=w, h=h)
            ...  # Image creates SVGImage objects which will load Images if Pillow is installed with a call to .load(). Correct parsing of x, y, width, height and viewbox.
            extras["image"] = image_content
        elif isinstance(item, svgelements.Use):
            for ith, e in enumerate(item):
                return_dict[f"{shape_name}_{ith}"] = convert_elements(e, w=w, h=h)
            continue
        else:
            """Nested SVG objects. (Caveats see Non-Supported)."""

            if True:
                logger.warning(
                    f"Not supported class: {f'{item.string_xml()} {type(item)}'}"
                )
            continue

        return_dict[shape_name] = SvgShapelyGeometry(
            shape_name,
            shape_geometry,
            item_value_class,
            item_type,
            item_filled,
            extras,
            item_fill_colour,
        )

    return return_dict
