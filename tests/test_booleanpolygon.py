"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction

import numpy as np
import pytest

from compmec import nurbs
from compmec.shape import Point2D
from compmec.shape.jordancurve import JordanCurve, JordanPolygon
from compmec.shape.shape import SimpleShape


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "tests/test_polygon.py::test_end",
        "tests/test_jordanpolygon.py::test_end",
        "tests/test_jordancurve.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestOrSimpleShapeJordanPoly:
    @pytest.mark.order(4)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOrSimpleShapeJordanPoly::test_begin"])
    def test_two_squares(self):
        vertices0 = [(1, 0), (-1, 2), (-3, 0), (-1, -2)]
        square0 = JordanPolygon(vertices0)
        square0 = SimpleShape(square0)
        vertices1 = [(-1, 0), (1, -2), (3, 0), (1, 2)]
        square1 = JordanPolygon(vertices1)
        square1 = SimpleShape(square1)

        good_points = [
            (0, 1),
            (-1, 2),
            (-3, 0),
            (-1, -2),
            (0, -1),
            (1, -2),
            (3, 0),
            (1, 2),
        ]
        good_jordanpoly = JordanPolygon(good_points)
        good_shape = SimpleShape(good_jordanpoly)

        assert square0 | square1 == good_shape

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestOrSimpleShapeJordanPoly::test_begin",
            "TestOrSimpleShapeJordanPoly::test_two_squares",
        ]
    )
    def test_end(self):
        pass


class TestAndSimpleShapeJordanPoly:
    @pytest.mark.order(4)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestAndSimpleShapeJordanPoly::test_begin"])
    def test_two_squares(self):
        vertices0 = [(1, 0), (-1, 2), (-3, 0), (-1, -2)]
        square0 = JordanPolygon(vertices0)
        square0 = SimpleShape(square0)
        vertices1 = [(-1, 0), (1, -2), (3, 0), (1, 2)]
        square1 = JordanPolygon(vertices1)
        square1 = SimpleShape(square1)

        good_points = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        good_jordanpoly = JordanPolygon(good_points)
        good_shape = SimpleShape(good_jordanpoly)

        assert square0 & square1 == good_shape

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestAndSimpleShapeJordanPoly::test_begin",
            "TestAndSimpleShapeJordanPoly::test_two_squares",
        ]
    )
    def test_end(self):
        pass


class TestMinusSimpleShapeJordanPoly:
    @pytest.mark.order(4)
    @pytest.mark.skip(reason="Needs implementation")
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestMinusSimpleShapeJordanPoly::test_begin"])
    def test_two_squares(self):
        vertices0 = [(1, 0), (-1, 2), (-3, 0), (-1, -2)]
        square0 = JordanPolygon(vertices0)
        square0 = SimpleShape(square0)
        vertices1 = [(-1, 0), (1, -2), (3, 0), (1, 2)]
        square1 = JordanPolygon(vertices1)
        square1 = SimpleShape(square1)

        left_points = [(0, 1), (-1, 2), (-3, 0), (-1, -2), (0, -1), (-1, 0)]
        left_jordanpoly = JordanPolygon(left_points)
        left_shape = SimpleShape(left_jordanpoly)
        right_points = [(0, 1), (1, 0), (0, -1), (1, -2), (3, 0), (1, 2)]
        right_jordanpoly = JordanPolygon(right_points)
        right_shape = SimpleShape(right_jordanpoly)

        assert square0 - square1 == left_shape
        assert square1 - square0 == right_shape

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestMinusSimpleShapeJordanPoly::test_begin",
            "TestMinusSimpleShapeJordanPoly::test_two_squares",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "TestOrSimpleShapeJordanPoly::test_end",
        "TestAndSimpleShapeJordanPoly::test_end",
        "TestMinusSimpleShapeJordanPoly::test_end",
    ]
)
def test_end():
    pass
