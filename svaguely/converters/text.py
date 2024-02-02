from typing import Tuple

import shapely
import svgelements
from warg import Number

__all__ = ["text_converter"]
__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"


def text_converter(
    item: svgelements.Text, w: Number = 1, h: Number = 1
) -> Tuple[shapely.Point, str]:
    # minx, miny, maxx, maxy = item.bbox() # NO PATH AVAILABLE therefore no bbox, sorry.. Implementation for rendering needed
    #  rect = shapely.Polygon( [[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy], [minx, miny]]  )

    # TODO: Enable
    #    cy = h - item.cy # INVERT?
    point = shapely.geometry.Point(item.x, item.y)

    return point, item.text


if __name__ == "__main__":
    print(text_converter(svgelements.Text("Hello World", x=1.0, y=2.0)))
