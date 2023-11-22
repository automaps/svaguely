# -*- coding: utf-8 -*-
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Any, Mapping

METADATA_KEY = "SVG_METADATA"

__all__ = ["add_metadata_desc_tag"]


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
