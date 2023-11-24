# -*- coding: utf-8 -*-
import io
import json
import os
from pathlib import Path
from typing import Mapping, Tuple, Union, Dict, Optional

import svgelements

from .conversion import convert_elements
from .data_models import SvgShapelyGeometry
from .metadata import METADATA_KEY

__all__ = ["parse_svg"]


def parse_svg(
    svg_filestream: Union[Path, str, bytes]
) -> Tuple[Dict[str, SvgShapelyGeometry], Optional[Mapping[str, str]]]:
    """
    Main function of converting. This reads the svg and parses it.
    Then converts the svgelements into classes with shapely geometries.

    :param svg_filestream: Path to the svg
    :return: dataclass of svg elements and dataclass of metadata
    """

    w = h = 1

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

    if len(svg) == 1:
        svg_groups = svg[0]
    else:
        svg_groups = svg

    metadata_dict = None

    groups = {}
    for group in svg_groups:
        if isinstance(group, svgelements.Desc):  # extract metadata
            if group.id == METADATA_KEY:  # check if its our description metadata
                assert metadata_dict is None
                metadata_dict = json.loads(
                    group.values["attributes"]["desc"].replace("'", '"')
                )

        else:
            groups[group.id] = convert_elements(group)

    return groups, metadata_dict
