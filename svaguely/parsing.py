# -*- coding: utf-8 -*-
import io
import json
import os
from itertools import count
from pathlib import Path
from typing import Union, Optional, Any

import svgelements

from .conversion import convert_elements
from .data_models import SvgShapelyGeometry
from .metadata import METADATA_KEY

__all__ = ["parse_svg"]
__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"


def parse_svg(
    svg_filestream: Union[Path, str, bytes]
) -> tuple[dict[Any, dict[str, SvgShapelyGeometry]], Optional[Any]]:
  """
  Main function of converting. This reads the svg and parses it.
  Then converts the svgelements into classes with shapely geometries.

  :param svg_filestream: Path to the svg
  :return: dataclass of svg elements and dataclass of metadata
  """

  w = h = 1
  name_counter = iter(count())

  if isinstance(svg_filestream, bytes):
    svg_filestream = io.BytesIO(svg_filestream)

  elif not os.path.isfile(svg_filestream):
    svg_filestream = io.StringIO(svg_filestream)

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

    else:

      if hasattr(element, "id") and element.id:
        element_s = element.id
      else:
        element_s = f"NoName{next(name_counter)}"

      shape_elements[element_s] = convert_elements(element)

  return shape_elements, metadata_dict
