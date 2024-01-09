import shapely
import svgelements
from warg import Number

__all__ = ["point_converter"]
__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"


def point_converter(
    item: svgelements.Point, w: Number = 1, h: Number = 1
) -> shapely.Point:
    cx = item.x
    cy = h - item.y

    return shapely.geometry.Point([cx, cy])
