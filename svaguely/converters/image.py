from typing import Tuple

import shapely
import svgelements
from warg import Number

__all__ = ["image_converter"]
__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"


def image_converter(
    item: svgelements.Image, w: Number = 1, h: Number = 1
) -> Tuple[shapely.Polygon, bytes]:
    # TODO: Enable
    #    cy = h - item.cy # INVERT?
    point = shapely.geometry.Point(item.x, item.y)

    minx, miny, maxx, maxy = item.bbox()
    rect = shapely.Polygon(
        [[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy], [minx, miny]]
    )

    return rect, item.data


if __name__ == "__main__":
    print(image_converter(svgelements.Image()))
