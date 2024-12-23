"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve 
"""

import pytest

from shapepy.core import Empty, Whole
from shapepy.curve.polygon import PolygonClosedCurve
from shapepy.point import Point2D
from shapepy.primitive import Primitive
from shapepy.shape import ConnectedShape, DisjointShape, SimpleShape
from shapepy.shape.simple import identify_shape


@pytest.mark.order(9)
@pytest.mark.dependency(
    depends=[
        "tests/test_empty_whole.py::test_end",
        "tests/test_point.py::test_end",
        "tests/test_primitive.py::test_end",
        "tests/test_shape.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestSingleton:
    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestSingleton::test_begin",
        ]
    )
    def test_move(self):
        empty = Empty()
        whole = Whole()
        assert empty.move((0, 0)) is empty
        assert empty.move((1, 2)) is empty
        assert whole.move((0, 0)) is whole
        assert whole.move((1, 2)) is whole

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestSingleton::test_begin",
        ]
    )
    def test_rotate(self):
        empty = Empty()
        whole = Whole()
        assert empty.rotate(0) is empty
        assert empty.rotate(90 / 360) is empty
        assert whole.rotate(0) is whole
        assert whole.rotate(90 / 360) is whole

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestSingleton::test_begin",
        ]
    )
    def test_scale(self):
        empty = Empty()
        whole = Whole()
        assert empty.scale(1, 1) is empty
        assert empty.scale(3, 2) is empty
        assert empty.scale(4, 8) is empty
        assert whole.scale(1, 1) is whole
        assert whole.scale(3, 4) is whole
        assert whole.scale(2, 5) is whole

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestSingleton::test_begin",
            "TestSingleton::test_move",
            "TestSingleton::test_rotate",
            "TestSingleton::test_scale",
        ]
    )
    def test_end(self):
        pass


class TestPoint:
    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestPoint::test_begin",
        ]
    )
    def test_move(self):
        point = Point2D((0, 0))
        assert point.move((0, 0)) == (0, 0)
        assert point.move((1, 2)) == (1, 2)
        assert point.move((0, 0)) == (0, 0)

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestPoint::test_begin",
        ]
    )
    def test_rotate(self):
        point = Point2D((0, 0))
        assert point.rotate(0) == (0, 0)
        
        point = Point2D((1, 0))
        assert point.rotate(0) == (1, 0)
        assert point.rotate(90 / 360) == (0, 1)
        assert point.rotate(180 / 360) == (-1, 0)
        assert point.rotate(270 / 360) == (0, -1)
        assert point.rotate(1) == (1, 0)

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestPoint::test_begin",
        ]
    )
    def test_scale(self):
        point = Point2D((0, 0))
        assert point.scale(0, 0) == (0, 0)

        point = Point2D((1, 3))
        assert point.scale(1, 1) == (1, 3)
        assert point.scale(3, 5) == (3, 15)

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestPoint::test_begin",
            "TestPoint::test_move",
            "TestPoint::test_rotate",
            "TestPoint::test_scale",
        ]
    )
    def test_end(self):
        pass


class TestPolygonCurve:
    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestPoint::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestPolygonCurve::test_begin",
        ]
    )
    def test_move(self):
        old_vertices = [(0, 0), (1, 0), (0, 1)]
        new_vertices = [(1, 2), (2, 2), (1, 3)]
        base_curve = PolygonClosedCurve(old_vertices)
        good_curve = PolygonClosedCurve(new_vertices)
        test_curve = base_curve.move((1, 2))
        assert test_curve == good_curve

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestPolygonCurve::test_begin",
        ]
    )
    def test_rotate(self):
        old_vertices = [(0, 0), (1, 0), (0, 1)]
        new_vertices = [(0, 0), (0, 1), (-1, 0)]
        base_curve = PolygonClosedCurve(old_vertices)
        good_curve = PolygonClosedCurve(new_vertices)
        test_curve = base_curve.rotate(0.25)
        assert test_curve == good_curve

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestPolygonCurve::test_begin",
        ]
    )
    def test_scale(self):
        old_vertices = [(0, 0), (1, 0), (0, 1)]
        new_vertices = [(0, 0), (4, 0), (0, 3)]
        base_curve = PolygonClosedCurve(old_vertices)
        good_curve = PolygonClosedCurve(new_vertices)
        test_curve = base_curve.scale(4, 3)
        assert test_curve == good_curve

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestPolygonCurve::test_begin",
            "TestPolygonCurve::test_move",
            "TestPolygonCurve::test_rotate",
            "TestPolygonCurve::test_scale",
        ]
    )
    def test_end(self):
        pass


class TestSimple:
    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestSimple::test_begin",
        ]
    )
    def test_end(self):
        pass


class TestConnected:
    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestSimple::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestConnected::test_begin",
        ]
    )
    def test_move(self):
        big_square = Primitive.square(4, (0, 0))
        sma_square = Primitive.square(2, (0, 0))
        con_shape = ConnectedShape([big_square, ~sma_square])
        test_shape = con_shape.move((1, 2))

        big_square = Primitive.square(4, (1, -2))
        sma_square = Primitive.square(2, (1, -2))
        good_shape = ConnectedShape([big_square, ~sma_square])

        assert test_shape == good_shape

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestConnected::test_begin",
        ]
    )
    def test_rotate(self):
        big_square = Primitive.square(4, (1, 2))
        sma_square = Primitive.square(2, (1, 2))
        con_shape = ConnectedShape([big_square, ~sma_square])
        test_shape = con_shape.rotate(180 / 360)

        big_square = Primitive.square(4, (-1, -2))
        sma_square = Primitive.square(2, (-1, -2))
        good_shape = ConnectedShape([big_square, ~sma_square])

        assert test_shape == good_shape

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestConnected::test_begin",
        ]
    )
    def test_scale(self):
        big_square = Primitive.square(4, (0, 0))
        sma_square = Primitive.square(2, (0, 0))
        con_shape = ConnectedShape([big_square, ~sma_square])
        test_shape = con_shape.scale(2, 2)

        big_square = Primitive.square(8, (0, 0))
        sma_square = Primitive.square(4, (0, 0))
        good_shape = ConnectedShape([big_square, ~sma_square])

        assert test_shape == good_shape

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestConnected::test_begin",
            "TestConnected::test_move",
            "TestConnected::test_rotate",
            "TestConnected::test_scale",
        ]
    )
    def test_end(self):
        pass


class TestDisjoint:
    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestSimple::test_end",
            "TestConnected::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestDisjoint::test_begin",
        ]
    )
    def test_move(self):
        lef_square = Primitive.square(2, (-4, 0))
        rig_square = Primitive.square(2, (4, 0))
        disj_shape = DisjointShape([lef_square, rig_square])
        test_shape = disj_shape.move((1, 2))

        lef_square = Primitive.square(2, (-3, 2))
        rig_square = Primitive.square(2, (5, 2))
        good_shape = DisjointShape([lef_square, rig_square])

        assert test_shape == good_shape

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestDisjoint::test_begin",
        ]
    )
    def test_rotate(self):
        lef_square = Primitive.square(2, (-4, 0))
        rig_square = Primitive.square(2, (4, 0))
        disj_shape = DisjointShape([lef_square, rig_square])
        test_shape = disj_shape.rotate(0.25)

        top_square = Primitive.square(2, (0, 4))
        bot_square = Primitive.square(2, (0, -4))
        good_shape = DisjointShape([top_square, bot_square])

        assert test_shape == good_shape

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestDisjoint::test_begin",
        ]
    )
    def test_scale(self):
        lef_square = Primitive.square(2, (-4, 0))
        rig_square = Primitive.square(2, (4, 0))
        disj_shape = DisjointShape([lef_square, rig_square])
        test_shape = disj_shape.scale(2, 2)

        lef_square = Primitive.square(4, (-8, 0))
        rig_square = Primitive.square(4, (8, 0))
        good_shape = DisjointShape([lef_square, rig_square])

        assert test_shape == good_shape

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestDisjoint::test_begin",
            "TestDisjoint::test_move",
            "TestDisjoint::test_rotate",
            "TestDisjoint::test_scale",
        ]
    )
    def test_end(self):
        pass


class TestBoolNot:
    @pytest.mark.order(9)
    @pytest.mark.dependency(depends=["test_begin", "TestPoint::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestBoolNot::test_begin",
        ]
    )
    def test_move(self):
        point = Point2D(0, 0)
        vector = Point2D(1, 2)
        assert (~point).move(vector) == ~vector

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestBoolNot::test_begin",
        ]
    )
    def test_rotate(self):
        pointa = Point2D(2, 3)
        pointb = Point2D(-3, 2)
        assert (~pointa).rotate(0.25) == ~pointb

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestBoolNot::test_begin",
        ]
    )
    def test_scale(self):
        pointa = Point2D(2, 3)
        pointb = Point2D(6, 15)
        assert (~pointa).scale(3, 5) == ~pointb

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestBoolNot::test_begin",
            "TestBoolNot::test_move",
            "TestBoolNot::test_rotate",
            "TestBoolNot::test_scale",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(9)
@pytest.mark.dependency(
    depends=[
        "TestSingleton::test_end",
        "TestPoint::test_end",
        "TestPolygonCurve::test_end",
        "TestSimple::test_end",
        "TestConnected::test_end",
        "TestDisjoint::test_end",
        "TestBoolNot::test_end",
    ]
)
def test_end():
    pass
