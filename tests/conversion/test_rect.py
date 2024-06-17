import math

import svgelements
from svaguely.conversion import circle_converter, point_converter, rectangle_converter

eps = 0.001
loose_eps = 0.1


def test_unit_rect_conversion():
    x = y = 1
    a = svgelements.Rect(x / 2.0, y / 2.0, x, y)

    res = rectangle_converter(a)

    assert abs(res.centroid.x - x < eps)
    assert abs(res.centroid.y - y < eps)
    assert abs(res.area - (x * y)) < eps, res.area
