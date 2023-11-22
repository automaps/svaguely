# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Callable, Any

from shapely.geometry.base import BaseGeometry

__all__ = ["SvgShapelyGeometry", "ConvertMetaParam"]


@dataclass
class SvgShapelyGeometry:
    name: str
    geometry: BaseGeometry
    item_value_class: str
    item_type: str
    item_filled: bool


@dataclass
class ConvertMetaParam:
    name: str
    value: Any
    default_value: Any
    str_to_type: Callable
