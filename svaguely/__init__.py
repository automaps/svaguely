import io
import json
import logging
import os
from itertools import count
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import svgelements
from warg import Number

from .conversion import *
from .data_models import *
from .metadata import *

__project__ = "Svaguely"
__doc__ = """\
Svaguely is a Python package for converting svg elements into shapely geometries
"""

__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"
__version__ = "0.0.3"

PROJECT_NAME = __project__
PROJECT_AUTHOR = __author__
PROJECT_YEAR = 2023
PROJECT_ORGANISATION = "MapsPeople"
PROJECT_VERSION = __version__

logger = logging.getLogger(__name__)

__all__ = ["convert_elements", "parse_svg"]


def convert_elements(
    elements: svgelements.Group,
    *,
    w: Optional[Number] = 1,
    h: Optional[Number] = 1,
    name_seperator: str = "|",
) -> Dict[str, SvgElement]:
    """

    :param elements:
    :param w:
    :param h:
    :param name_seperator:
    :return:
    """
    return_dict = {}
    name_counter = iter(count())

    if not isinstance(elements, svgelements.Group):
        elements = [elements]

    for element in elements:
        element_type = type(element)
        element_filled = False
        element_fill_color = None
        element_stroke_width = None
        element_stroke_color = None
        element_color = None
        element_name = None

        extras = {}

        element_id = element.id

        if hasattr(element, "color") and element.color:
            element_color = element.color

        if hasattr(element, "fill") and element.fill.hex:
            element_fill_color = element.fill.hex

        if hasattr(element, "stroke") and element.stroke.hex:
            element_stroke_color = element.stroke.hex

        if hasattr(element, "stroke_width") and element.stroke_width:
            element_stroke_width = element.stroke_width

        if hasattr(element, "values"):
            for key, value in element.values.items():
                if "label" in key:
                    element_name = value
                elif "data-name" in key:
                    element_name = value

            extras.update(element.values)

        element_unique_id = element_unique_id_base = (
            f"{element_id}{name_seperator}{element_name}"
        )
        while element_unique_id in return_dict:
            element_unique_id = (
                f"{element_unique_id_base}{name_seperator}{next(name_counter)}"
            )

        if isinstance(element, svgelements.Group):
            return_dict[element_unique_id] = convert_elements(
                element, w=w, h=h, name_seperator=name_seperator
            )
            continue

        if isinstance(element, svgelements.Rect):
            shape_geometry = rectangle_converter(element, w=w, h=h)

        elif isinstance(element, svgelements.SimpleLine):
            shape_geometry = simpleline_converter(element, w=w, h=h)

        elif isinstance(element, svgelements.Polyline):
            shape_geometry = polyline_converter(element, w=w, h=h)

        elif isinstance(element, svgelements.Polygon):
            shape_geometry = polygon_converter(element, w=w, h=h)

        elif isinstance(element, svgelements.Point):
            shape_geometry = point_converter(element, w=w, h=h)

        elif isinstance(element, svgelements.Circle):
            if False:
                e = svgelements.Path(element)
                e = e.reify()
                shape_geometry = path_converter(e, w=w, h=h)
            else:
                shape_geometry = circle_converter(element, w=w, h=h)

        elif isinstance(element, (svgelements.Ellipse, svgelements.Curve)):
            e = svgelements.Path(element)
            e_reified = e.reify()
            shape_geometry = path_converter(e_reified, w=w, h=h)

        elif isinstance(element, svgelements.Path):
            shape_geometry = path_converter(element, w=w, h=h)

        elif isinstance(element, svgelements.Text):
            # Text objects. The lack of a font engine makes this class more of a parsed stub class.
            shape_geometry, text_content, font_meta_data = text_converter(
                element, w=w, h=h
            )
            extras["text"] = text_content
            extras["font"] = font_meta_data

        elif isinstance(element, svgelements.Pattern):
            ...  # Pattern objects. These are parsed they are not currently assigned.

        elif isinstance(element, svgelements.Image):
            shape_geometry, image_content = image_converter(element, w=w, h=h)
            ...  # Image creates SVGImage objects which will load Images if Pillow is installed with a call to
            # .load(). Correct parsing of x, y, width, height and viewbox.
            extras["image"] = image_content
        elif isinstance(element, svgelements.Use):
            for ith, e in enumerate(element):
                return_dict[f"{element_name}_{ith}"] = convert_elements(e, w=w, h=h)
            continue

        elif isinstance(element, svgelements.Desc) and False:  # extract metadata
            if element.id == METADATA_KEY:  # check if its our description metadata
                assert metadata_dict is None
                metadata_dict = json.loads(
                    element.values["attributes"]["desc"].replace("'", '"')
                )

        elif isinstance(element, svgelements.Title) and False:
            ...  # TODO implement
        else:
            """Nested SVG objects. (Caveats see Non-Supported)."""

            if True:
                logger.warning(
                    f"Not supported class: {f'{element.string_xml()} {type(element)}'}"
                )
            continue

        return_dict[element_unique_id] = SvgElement(
            element_id=element_id,
            element_name=element_name,
            geometry=shape_geometry,
            element_type=element_type,
            extras=extras,
            color=element_color,
            fill_color=element_fill_color,
            stroke_color=element_stroke_color,
            stroke_width=element_stroke_width,
        )

    return return_dict


def parse_svg(
    svg_filestream: Union[Path, str, bytes],
    output_space: Optional[Union[Number, Tuple[Number, Number]]] = None,
    name_seperator: str = "|",
) -> Tuple[Dict[Any, Dict[str, SvgElement]], Optional[Any]]:
    """
    Main function of converting. This reads the svg and parses it.
    Then converts the svgelements into classes with shapely geometries.

    :param output_space:
    :param svg_filestream: Path to the svg
    :return: dataclass of svg elements and dataclass of metadata
    """

    if output_space:
        if isinstance(output_space, (float, int)):
            w = h = output_space
        else:
            w, h = output_space
    else:
        w = h = 1

    name_counter = iter(count())

    if isinstance(svg_filestream, bytes):
        svg_filestream = io.BytesIO(svg_filestream)

    elif not os.path.isfile(svg_filestream):
        svg_filestream = io.StringIO(str(svg_filestream))

    svg = svgelements.SVG.parse(
        svg_filestream,
        reify=True,
        ppi=svgelements.DEFAULT_PPI,
        width=w,
        height=h,
        color="black",
        transform=None,
        context=None,
    )

    metadata_dict = None

    shape_elements = {}
    for element in svg:
        if isinstance(element, svgelements.Desc):  # extract metadata
            if element.id == METADATA_KEY:  # check if its our description metadata
                assert metadata_dict is None
                metadata_dict = json.loads(
                    element.values["attributes"]["desc"].replace("'", '"')
                )

        elif isinstance(element, svgelements.Title):
            ...  # TODO implement

        else:
            element_id = element.id
            element_unique_id = str(element_id)
            while element_unique_id in shape_elements:
                element_unique_id = f"{element_id}{name_seperator}{next(name_counter)}"

            shape_elements[element_unique_id] = convert_elements(
                element, w=w, h=h, name_seperator=name_seperator
            )

    return shape_elements, metadata_dict
