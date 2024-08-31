from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional

from shapely.geometry.base import BaseGeometry

__all__ = ["SvgElement", "SvgMetadata"]
__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"

@dataclass
class SvgElement:
  element_id: str

  element_type: type

  geometry: BaseGeometry

  element_name: Optional[str]

  color: Optional[str] = None
  fill_color: Optional[str] = None
  stroke_color: Optional[str] = None
  stroke_width: Optional[float] = None

  extras: Optional[Mapping[str, Any]] = None

  @property
  def has_filled(self) -> bool:
    return self.fill_color is not None

  @property
  def has_stroke(self) -> bool:
    return self.stroke_color is not None and self.stroke_width != 0

@dataclass
class SvgMetadata:
  name: str
  value: Any
  default_value: Any
  str_to_type: Callable
