from dataclasses import dataclass
from typing import Callable, Any

METADATA_KEY = "SVG_METADATA"


@dataclass
class ConvertMetaParam:
    name: str
    value: Any
    default_value: Any
    str_to_type: Callable


def add_metadata(metadata_dict, path_to_svg) -> str:
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
        print("CANT FIND NECESSARY ENDING STRING")

    return svg_as_text_string
