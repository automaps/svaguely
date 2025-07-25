import math

import svgelements

from svaguely.conversion import circle_converter

eps = 0.001
loose_eps = 0.1


def test_unit_circle_conversion():
    x = y = r = 1
    a = svgelements.Circle((x, y), r)

    res = circle_converter(a)

    assert abs(res.centroid.x - x < eps)
    assert abs(res.centroid.y - y < eps)
    assert abs(res.area - (math.pi * (r**2.0))) < loose_eps, res.area


def test_unit_circle_conversion_2():
    x = y = r = 1
    a = svgelements.Circle(r)

    res = circle_converter(a)

    assert abs(res.centroid.x - x < eps)
    assert abs(res.centroid.y - y < eps)
    assert abs(res.area - (math.pi * (r**2.0))) < loose_eps, res.area
