"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve 
"""

import pytest

from shapepy.primitive import Primitive
from shapepy.shape import ConnectedShape, DisjointShape, SimpleShape
from shapepy.shape.boolean import identify_shape


@pytest.mark.order(8)
@pytest.mark.dependency(
    depends=[
        "tests/test_empty_whole.py::test_end",
        "tests/test_point.py::test_end",
        "tests/test_primitive.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestSimple:
    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestSimple::test_begin",
        ]
    )
    def test_build(self):
        points = [(0, 0), (1, 0), (0, 1)]
        Primitive.polygon(points)

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestSimple::test_begin",
            "TestSimple::test_build",
        ]
    )
    def test_area(self):
        points = [(0, 0), (1, 0), (0, 1)]
        shape = Primitive.polygon(points)
        assert shape.area == 0.5

        points = [(0, 0), (0, 1), (1, 0)]
        shape = Primitive.polygon(points)
        assert shape.area == -0.5

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestSimple::test_begin",
            "TestSimple::test_build",
            "TestSimple::test_area",
        ]
    )
    def test_compare(self):
        points = [(0, 0), (1, 0), (0, 1)]
        shapea = Primitive.polygon(points)
        shapeb = Primitive.polygon(points)
        assert shapea == shapeb

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestSimple::test_begin",
            "TestSimple::test_build",
            "TestSimple::test_area",
            "TestSimple::test_compare",
        ]
    )
    def test_end(self):
        pass


class TestConnected:
    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestSimple::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestConnected::test_begin",
        ]
    )
    def test_build(self):
        points = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
        shapea = Primitive.polygon(points)
        points = [(-2, -2), (2, -2), (2, 2), (-2, 2)]
        shapeb = Primitive.polygon(points)
        ConnectedShape([shapea, shapeb])

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestConnected::test_begin",
            "TestConnected::test_build",
        ]
    )
    def test_area(self):
        points = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
        shapea = Primitive.polygon(points)
        points = [(-2, -2), (2, -2), (2, 2), (-2, 2)]
        shapeb = Primitive.polygon(points)
        shape = ConnectedShape([shapea, shapeb])
        assert shape.area == 12

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestConnected::test_begin",
            "TestConnected::test_build",
            "TestConnected::test_area",
        ]
    )
    def test_compare(self):
        pointsa = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
        pointsb = [(-2, -2), (2, -2), (2, 2), (-2, 2)]
        shapea = Primitive.polygon(pointsa)
        shapeb = Primitive.polygon(pointsb)
        shape0 = ConnectedShape([shapea, shapeb])
        shapea = Primitive.polygon(pointsa)
        shapeb = Primitive.polygon(pointsb)
        shape1 = ConnectedShape([shapea, shapeb])
        assert shape0 == shape1

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestConnected::test_begin",
            "TestConnected::test_build",
            "TestConnected::test_area",
            "TestConnected::test_compare",
        ]
    )
    def test_end(self):
        pass


class TestDisjoint:
    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestSimple::test_end",
            "TestConnected::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestDisjoint::test_begin",
        ]
    )
    def test_build(self):
        points = [(-3, -1), (3, -1), (3, 1), (-3, 1)]
        shapea = Primitive.polygon(points)
        points = [(1, -2), (3, -2), (3, 2), (1, 2)]
        shapeb = Primitive.polygon(points)
        DisjointShape([shapea, shapeb])

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestDisjoint::test_begin",
            "TestDisjoint::test_build",
        ]
    )
    def test_area(self):
        points = [(-3, -2), (-1, -2), (-1, 2), (-3, 2)]
        shapea = Primitive.polygon(points)
        points = [(1, -2), (3, -2), (3, 2), (1, 2)]
        shapeb = Primitive.polygon(points)
        shape = DisjointShape([shapea, shapeb])
        assert shape.area == 16

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestDisjoint::test_begin",
            "TestDisjoint::test_build",
            "TestDisjoint::test_area",
        ]
    )
    def test_end(self):
        pass


class TestIdentifyShape:
    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestSimple::test_end",
            "TestConnected::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestIdentifyShape::test_begin",
        ]
    )
    def test_simple(self):
        square = Primitive.square()
        test = identify_shape([square])
        assert isinstance(test, SimpleShape)
        assert test == square

        square = ~Primitive.square()
        test = identify_shape([square])
        assert isinstance(test, SimpleShape)
        assert test == square

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestIdentifyShape::test_simple",
        ]
    )
    def test_connected(self):
        big_square = Primitive.square(4)
        sma_square = Primitive.square(2)
        good = ConnectedShape([big_square, ~sma_square])
        test = identify_shape([big_square, ~sma_square])
        assert isinstance(test, ConnectedShape)
        assert test == good

        left_square = Primitive.square(2, (-10, 0))
        righ_square = Primitive.square(2, (10, 0))
        good = ConnectedShape([~left_square, ~righ_square])
        test = identify_shape([~left_square, ~righ_square])
        assert isinstance(test, ConnectedShape)
        assert test == good

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestIdentifyShape::test_simple",
            "TestIdentifyShape::test_connected",
        ]
    )
    def test_disjoint(self):
        left_square = Primitive.square(2, (-10, 0))
        righ_square = Primitive.square(2, (10, 0))
        good = DisjointShape([left_square, righ_square])
        test = identify_shape([left_square, righ_square])
        assert isinstance(test, DisjointShape)
        assert test == good

        square0 = Primitive.square(20)
        square1 = Primitive.square(16)
        square2 = Primitive.square(12)
        square3 = Primitive.square(8)
        consha0 = ConnectedShape([square0, ~square1])
        consha1 = ConnectedShape([square2, ~square3])
        good = DisjointShape([consha0, consha1])
        test = identify_shape([square0, ~square1, square2, ~square3])
        assert isinstance(test, DisjointShape)
        assert test == good

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestIdentifyShape::test_begin",
            "TestIdentifyShape::test_simple",
            "TestIdentifyShape::test_connected",
            "TestIdentifyShape::test_disjoint",
        ]
    )
    def test_end(self):
        pass


class TestOthers:
    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
            "TestSimple::test_end",
        ]
    )
    def test_print_simple(self):
        points = [(0, 0), (1, 0), (0, 1)]
        shape = Primitive.polygon(points)
        str(shape)
        repr(shape)

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
            "TestConnected::test_end",
        ]
    )
    def test_print_connected(self):
        big_square = Primitive.square(4)
        sma_square = Primitive.square(2)
        shape = ConnectedShape([big_square, ~sma_square])
        str(shape)
        repr(shape)

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
            "TestDisjoint::test_end",
        ]
    )
    def test_print_disjoint(self):
        left_square = Primitive.square(2, (-4, 0))
        righ_square = Primitive.square(2, (4, 0))
        shape = DisjointShape([left_square, righ_square])
        str(shape)
        repr(shape)

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
            "TestSimple::test_end",
        ]
    )
    def test_compare(self):
        shapea = Primitive.regular_polygon(3)
        shapeb = Primitive.regular_polygon(4)
        assert shapea != shapeb

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
            "TestOthers::test_print_simple",
            "TestOthers::test_print_connected",
            "TestOthers::test_print_disjoint",
            "TestOthers::test_compare",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(8)
@pytest.mark.dependency(
    depends=[
        "TestSimple::test_end",
        "TestConnected::test_end",
        "TestDisjoint::test_end",
        "TestIdentifyShape::test_end",
        "TestOthers::test_end",
    ]
)
def test_end():
    pass
