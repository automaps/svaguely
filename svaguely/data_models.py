from dataclasses import dataclass
from typing import Any, Callable, Optional, Mapping

from shapely.geometry.base import BaseGeometry

__all__ = ["SvgShapelyGeometry", "SvgMetadata"]
__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"


@dataclass
class SvgShapelyGeometry:
    name: str
    geometry: BaseGeometry
    item_value_class: str
    item_type: str
    item_filled: bool
    extras: Optional[Mapping[str, Any]] = None
    item_fill_colour: str = None


@dataclass
class SvgMetadata:
    name: str
    value: Any
    default_value: Any
    str_to_type: Callable
