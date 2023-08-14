"""
This file contains tests functions to test the module polygon.py
"""

import pytest

from compmec.shape.jordancurve import JordanPolygon
from compmec.shape.shape import EmptyShape, SimpleShape, WholeShape


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


class TestEmptyWhole:
    @pytest.mark.order(5)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(5)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_or(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty | empty is empty
        assert empty | whole is whole
        assert whole | empty is whole
        assert whole | whole is whole

        assert empty + empty is empty
        assert empty + whole is whole
        assert whole + empty is whole
        assert whole + whole is whole

    @pytest.mark.order(5)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_and(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty & empty is empty
        assert empty & whole is empty
        assert whole & empty is empty
        assert whole & whole is whole

        assert empty * empty is empty
        assert empty * whole is empty
        assert whole * empty is empty
        assert whole * whole is whole

    @pytest.mark.order(5)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_xor(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty ^ empty is empty
        assert empty ^ whole is whole
        assert whole ^ empty is whole
        assert whole ^ whole is empty

    @pytest.mark.order(5)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_sub(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty - empty is empty
        assert empty - whole is empty
        assert whole - empty is whole
        assert whole - whole is empty

    @pytest.mark.order(5)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_bool(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert bool(empty) is False
        assert bool(whole) is True

    @pytest.mark.order(5)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_float(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert float(empty) == float(0)
        assert float(whole) == float("inf")

    @pytest.mark.order(5)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_invert(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert ~empty is whole
        assert ~whole is empty
        assert ~(~empty) is empty
        assert ~(~whole) is whole

    @pytest.mark.order(5)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_copy(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty.copy() is empty
        assert whole.copy() is whole

    @pytest.mark.order(5)
    @pytest.mark.dependency(
        depends=[
            "TestEmptyWhole::test_begin",
            "TestEmptyWhole::test_or",
            "TestEmptyWhole::test_and",
            "TestEmptyWhole::test_xor",
            "TestEmptyWhole::test_sub",
            "TestEmptyWhole::test_bool",
            "TestEmptyWhole::test_float",
            "TestEmptyWhole::test_invert",
            "TestEmptyWhole::test_copy",
        ]
    )
    def test_end(self):
        pass


class TestOrSimpleShape:
    @pytest.mark.order(5)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(5)
    @pytest.mark.timeout(40)
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
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(5)
    @pytest.mark.timeout(40)
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
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(5)
    @pytest.mark.timeout(40)
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
