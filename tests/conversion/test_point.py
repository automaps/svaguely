import svgelements

from svaguely.conversion import point_converter

eps = 0.001
loose_eps = 0.1


def test_unit_point_conversion():
    x = y = 1
    a = svgelements.Point(x, y)

    res = point_converter(a)

    assert abs(res.centroid.x - x < eps)
    assert abs(res.centroid.y - y < eps)
