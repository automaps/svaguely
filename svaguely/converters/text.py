from typing import Tuple, Dict, Any

import shapely
import svgelements
from warg import Number

__all__ = ["text_converter"]
__author__ = "Christian Heider Lindbjerg <chen(at)mapspeople.com>"


def text_converter(
    item: svgelements.Text, w: Number = 1, h: Number = 1
) -> Tuple[shapely.Point, str, Dict[str, Any]]:
    # minx, miny, maxx, maxy = item.bbox() # NO PATH AVAILABLE therefore no bbox, sorry.. Implementation for rendering needed
    #  rect = shapely.Polygon( [[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy], [minx, miny]]  )

    point = shapely.geometry.Point(
        item.x, h - item.y
    )  # TODO: COORDS ARE NOT NORMALISED BUG!

    return (
        point,
        item.text,
        {
            "size": item.font_size,
            "style": item.font_style,
            "weight": item.font_weight,
            "height": item.line_height,
        },
    )


if __name__ == "__main__":
    print(text_converter(svgelements.Text("Hello World", x=1.0, y=2.0)))
