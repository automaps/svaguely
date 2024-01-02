from pathlib import Path
from typing import Mapping

__all__ = ["add_metadata_desc_tag", "METADATA_KEY"]

__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"

METADATA_KEY = "SVG_METADATA"


def add_metadata_desc_tag(metadata_dict: Mapping, path_to_svg: Path) -> str:
    metadata_complete_insert_str = (
        f'<desc id="{METADATA_KEY}" desc="{str(metadata_dict)}" />'
    )

    svg_as_text_string = path_to_svg.read_text()

    if "\n</svg>" in svg_as_text_string:
        svg_metadata_string = svg_as_text_string.replace(
            "\n</svg>", f"\n{metadata_complete_insert_str}\n</svg>"
        )
    elif "</svg>" in svg_as_text_string:
        svg_metadata_string = svg_as_text_string.replace(
            "</svg>", f"{metadata_complete_insert_str}</svg>"
        )
    else:
        raise Exception("CANT FIND NECESSARY ENDING STRING")

    return svg_metadata_string
