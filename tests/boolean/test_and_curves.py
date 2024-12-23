"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve
"""

import numpy as np
import pytest

from shapepy.analytic import Trignomial
from shapepy.boolean import BoolOr
from shapepy.curve import JordanPolygon
from shapepy.curve.intersect import IntersectPoints
from shapepy.curve.piecewise import JordanPiecewise
from shapepy.point import Point2D
from shapepy.primitive import Primitive


@pytest.mark.order(33)
@pytest.mark.dependency(
    depends=[
        "tests/boolean/test_empty_whole.py::test_end",
        "tests/boolean/test_point.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestPolygonAndPolygon:
    @pytest.mark.order(33)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(33)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestPolygonAndPolygon::test_begin"])
    def test_equal_square(self):
        curve = Primitive.square(2).jordan
        good = BoolOr(curve.vertices)
        test = IntersectPoints.curve_and_curve(curve, curve)

        assert BoolOr(test) == good

    @pytest.mark.order(33)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestPolygonAndPolygon::test_equal_square"]
    )
    def test_regular(self):
        for nsides in range(3, 9):
            shape = Primitive.regular_polygon(nsides)
            vertices = tuple(shape.jordan.vertices)
            good = BoolOr(vertices)
            curvea = JordanPolygon(vertices)
            for j in range(nsides):
                newverts = np.roll(vertices, j, axis=0)
                curveb = JordanPolygon(newverts)
                test = BoolOr(IntersectPoints.curve_and_curve(curvea, curveb))
                assert test == good

    @pytest.mark.order(33)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestPolygonAndPolygon::test_begin",
            "TestPolygonAndPolygon::test_equal_square",
            "TestPolygonAndPolygon::test_regular",
        ]
    )
    def test_end(self):
        pass


class TestPolygonAndTrignomial:
    @pytest.mark.order(33)
    @pytest.mark.dependency(
        depends=["test_begin", "TestPolygonAndPolygon::test_end"]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(33)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestPolygonAndTrignomial::test_begin"])
    def test_square_circle(self):
        vertices = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        square = JordanPolygon(vertices)
        xfunc = Trignomial([1, 0, 1])
        yfunc = Trignomial([0, 1, 0])
        circle = JordanPiecewise([(xfunc, yfunc)])

        inters = IntersectPoints.curve_and_curve(square, circle)
        points = [Point2D(-1, 1), Point2D(1, 1)]
        assert BoolOr(inters) == BoolOr(points)

    @pytest.mark.order(33)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestPolygonAndTrignomial::test_begin",
            "TestPolygonAndTrignomial::test_square_circle",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(33)
@pytest.mark.dependency(
    depends=[
        "TestPolygonAndPolygon::test_end",
        "TestPolygonAndTrignomial::test_end",
    ]
)
def test_end():
    pass
