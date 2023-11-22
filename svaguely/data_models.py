# -*- coding: utf-8 -*-
from dataclasses import dataclass

from shapely.geometry.base import BaseGeometry


@dataclass
class SvgShapelyGeometry:
    name: str
    geometry: BaseGeometry
    item_value_class: str
    item_type: type
    item_fill: bool
