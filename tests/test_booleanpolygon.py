"""
This file contains tests functions to test the module polygon.py
"""

import pytest

from compmec.shape.jordancurve import JordanPolygon
from compmec.shape.shape import SimpleShape


@pytest.mark.order(5)
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


class TestOrSimpleShape:
    @pytest.mark.order(5)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOrSimpleShape::test_begin"])
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

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestOrSimpleShape::test_begin",
            "TestOrSimpleShape::test_two_squares",
        ]
    )
    def test_end(self):
        pass


class TestAndSimpleShape:
    @pytest.mark.order(5)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestAndSimpleShape::test_begin"])
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

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestAndSimpleShape::test_begin",
            "TestAndSimpleShape::test_two_squares",
        ]
    )
    def test_end(self):
        pass


class TestMinusSimpleShape:
    @pytest.mark.order(5)
    @pytest.mark.skip(reason="Needs implementation")
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestMinusSimpleShape::test_begin"])
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

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestMinusSimpleShape::test_begin",
            "TestMinusSimpleShape::test_two_squares",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(5)
@pytest.mark.dependency(
    depends=[
        "TestOrSimpleShape::test_end",
        "TestAndSimpleShape::test_end",
        "TestMinusSimpleShape::test_end",
    ]
)
def test_end():
    pass
