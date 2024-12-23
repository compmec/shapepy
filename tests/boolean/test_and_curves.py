"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve
"""

import pytest

from shapepy.analytic import Trignomial
from shapepy.boolean import BoolOr
from shapepy.curve import JordanPolygon
from shapepy.curve.piecewise import JordanPiecewise
from shapepy.point import Point2D


@pytest.mark.order(32)
@pytest.mark.dependency(
    depends=[
        "tests/boolean/test_empty_whole.py::test_end",
        "tests/boolean/test_point.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(32)
@pytest.mark.timeout(2)
@pytest.mark.dependency(
    depends=[
        "test_begin",
    ]
)
def test_adjacent_triangles():
    vertices = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    square = JordanPolygon(vertices)
    xfunc = Trignomial([1, 0, 1])
    yfunc = Trignomial([0, 1, 0])
    circle = JordanPiecewise([(xfunc, yfunc)])

    inters = square & circle
    points = [Point2D(-1, 1), Point2D(1, 1)]
    assert inters == BoolOr(points)


@pytest.mark.order(32)
@pytest.mark.timeout(2)
@pytest.mark.dependency(
    depends=[
        "test_begin",
    ]
)
def test_polygon_circle():
    vertices = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    square = JordanPolygon(vertices)
    xfunc = Trignomial([1, 0, 1])
    yfunc = Trignomial([0, 1, 0])
    circle = JordanPiecewise([(xfunc, yfunc)])

    inters = square & circle
    points = [Point2D(-1, 1), Point2D(1, 1)]
    assert inters == BoolOr(points)


@pytest.mark.order(32)
@pytest.mark.dependency(
    depends=[
        "test_polygon_circle",
    ]
)
def test_end():
    pass
