import json
from pathlib import Path
from typing import Mapping, Tuple

import svgelements

from . import convert_elements
from .metadata import METADATA_KEY

normalised_coords = True
if normalised_coords:
    w = h = 1
else:
    w = h = 1000


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
