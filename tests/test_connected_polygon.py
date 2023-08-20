"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve 
"""

import pytest

from compmec.shape.jordancurve import JordanPolygon
from compmec.shape.primitive import Primitive
from compmec.shape.shape import EmptyShape, SimpleShape, WholeShape


@pytest.mark.order(7)
@pytest.mark.dependency(
    depends=[
        # "tests/test_polygon.py::test_end",
        # "tests/test_jordan_polygon.py::test_end",
        # "tests/test_primitive.py::test_end",
        # "tests/test_simple_polygon.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestEmptyWhole:
    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(7)
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

        vertices = [(0, 0), (0, 1), (1, 0)]
        shape = Primitive.polygon(vertices)
        assert float(shape) < 0
        assert shape | empty == shape
        assert shape | whole is whole

    @pytest.mark.order(7)
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

        vertices = [(0, 0), (0, 1), (1, 0)]
        shape = Primitive.polygon(vertices)
        assert float(shape) < 0
        assert shape & empty is empty
        assert shape & whole == shape

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_xor(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty ^ empty is empty
        assert empty ^ whole is whole
        assert whole ^ empty is whole
        assert whole ^ whole is empty

        vertices = [(0, 0), (0, 1), (1, 0)]
        shape = Primitive.polygon(vertices)
        assert float(shape) < 0
        assert shape ^ empty == shape
        assert shape ^ whole == ~shape

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_sub(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty - empty is empty
        assert empty - whole is empty
        assert whole - empty is whole
        assert whole - whole is empty

        vertices = [(0, 0), (0, 1), (1, 0)]
        shape = Primitive.polygon(vertices)
        assert float(shape) < 0
        assert shape - empty == shape
        assert shape - whole is empty
        assert empty - shape is empty
        assert whole - shape == ~shape

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_bool(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert bool(empty) is False
        assert bool(whole) is True

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_float(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert float(empty) == float(0)
        assert float(whole) == float("inf")

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_invert(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert ~empty is whole
        assert ~whole is empty
        assert ~(~empty) is empty
        assert ~(~whole) is whole

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_copy(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty.copy() is empty
        assert whole.copy() is whole

    @pytest.mark.order(7)
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


class TestContainsPoint:
    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["test_begin", "TestEmptyWhole::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestContainsPoint::test_begin"])
    def test_point_in_square(self):
        square = ~Primitive.square(side=4)
        assert float(square) < 0
        for xval in range(-1, 2):
            for yval in range(-1, 2):
                assert (xval, yval) not in square

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestContainsPoint::test_begin"])
    def test_point_out_square(self):
        square = ~Primitive.square(side=4)
        assert float(square) < 0
        for xval in range(-4, 5):
            for yval in range(-4, 5):
                if -2 <= xval and xval <= 2 and -2 <= yval and yval <= 2:
                    continue
                assert (xval, yval) in square

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestContainsPoint::test_begin"])
    def test_other(self):
        square = ~Primitive.square()
        assert float(square) < 0
        assert (-10, -10) in square

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestContainsPoint::test_begin",
            "TestContainsPoint::test_point_in_square",
            "TestContainsPoint::test_point_in_square",
            "TestContainsPoint::test_other",
        ]
    )
    def test_end(self):
        pass


class TestContainsJordan:
    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestContainsPoint::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestContainsJordan::test_begin"])
    def test_square_in_square(self):
        small_square = Primitive.square(side=2)
        big_square = Primitive.square(side=4)

        assert small_square.jordancurve in big_square
        assert big_square.jordancurve not in small_square
        assert small_square.jordancurve not in (~big_square)
        assert big_square.jordancurve in (~small_square)

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestContainsJordan::test_begin",
            "TestContainsJordan::test_square_in_square",
        ]
    )
    def test_end(self):
        pass


class TestContainsShape:
    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestContainsJordan::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestContainsShape::test_begin"])
    def test_square_in_square(self):
        small_square = Primitive.square(side=2)
        big_square = Primitive.square(side=4)

        assert small_square in small_square
        assert small_square in big_square
        assert big_square in big_square
        assert big_square not in small_square

        assert (~small_square) not in big_square
        assert small_square not in (~big_square)
        assert (~big_square) not in small_square
        assert big_square not in (~small_square)
        assert (~small_square) not in (~big_square)
        assert (~big_square) in (~small_square)

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestContainsShape::test_begin",
            "TestContainsShape::test_square_in_square",
        ]
    )
    def test_end(self):
        pass


class TestOrSimpleShape:
    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=["TestEmptyWhole::test_end", "TestContainsShape::test_end"]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestOrSimpleShape::test_begin"])
    def test_inside_each(self):
        small_square = Primitive.square(side=2)
        big_square = Primitive.square(side=4)
        assert float(small_square) > 0
        assert float(big_square) > 0

        assert small_square | small_square == small_square
        assert small_square | big_square == big_square
        assert big_square | small_square == big_square
        assert big_square | big_square == big_square

        assert small_square | (~small_square) == WholeShape()
        assert big_square | (~big_square) == WholeShape()
        assert (~small_square) | small_square == WholeShape()
        assert (~big_square) | big_square == WholeShape()

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestOrSimpleShape::test_begin"])
    def test_complementar(self):
        square = Primitive.square()
        assert square | (~square) is WholeShape()

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=["TestOrSimpleShape::test_begin", "TestOrSimpleShape::test_inside_each"]
    )
    def test_squares_ab(self):
        square0 = Primitive.regular_polygon(nsides=4, radius=2, center=(-1, 0))
        square1 = Primitive.regular_polygon(nsides=4, radius=2, center=(1, 0))
        good_points = [(0, 1), (-1, 2), (-3, 0), (-1, -2)]
        good_points += [(0, -1), (1, -2), (3, 0), (1, 2)]
        good_shape = Primitive.polygon(good_points)
        assert square0 | square1 == good_shape

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=["TestOrSimpleShape::test_begin", "TestOrSimpleShape::test_squares_ab"]
    )
    def test_squares_anotb(self):
        square0 = Primitive.regular_polygon(nsides=4, radius=2, center=(-1, 0))
        square1 = ~Primitive.regular_polygon(nsides=4, radius=2, center=(1, 0))
        good_points = [(0, 1), (1, 2), (3, 0), (1, -2), (0, -1), (1, 0)]
        good_shape = Primitive.polygon(good_points)
        assert square0 | square1 == good_shape

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=["TestOrSimpleShape::test_begin", "TestOrSimpleShape::test_squares_ab"]
    )
    def test_squares_notab(self):
        square0 = ~Primitive.regular_polygon(nsides=4, radius=2, center=(-1, 0))
        square1 = Primitive.regular_polygon(nsides=4, radius=2, center=(1, 0))
        good_points = [(0, 1), (-1, 0), (0, -1), (-1, -2), (-3, 0), (-1, 2)]
        good_shape = Primitive.polygon(good_points)
        assert square0 | square1 == good_shape

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestOrSimpleShape::test_begin",
            "TestOrSimpleShape::test_squares_ab",
            "TestOrSimpleShape::test_squares_anotb",
            "TestOrSimpleShape::test_squares_notab",
        ]
    )
    def test_squares_notanotb(self):
        square0 = ~Primitive.regular_polygon(nsides=4, radius=2, center=(-1, 0))
        square1 = ~Primitive.regular_polygon(nsides=4, radius=2, center=(1, 0))
        good_points = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        good_shape = Primitive.polygon(good_points)
        union = square0 | square1
        print("union = ")
        print(union)
        print("good shape = ")
        print(good_shape)
        assert union == good_shape

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestOrSimpleShape::test_begin",
            "TestOrSimpleShape::test_inside_each",
            "TestOrSimpleShape::test_complementar",
            "TestOrSimpleShape::test_squares_ab",
            "TestOrSimpleShape::test_squares_anotb",
            "TestOrSimpleShape::test_squares_notab",
            "TestOrSimpleShape::test_squares_notanotb",
        ]
    )
    def test_end(self):
        pass


class TestAndSimpleShape:
    @pytest.mark.order(7)
    @pytest.mark.skip()
    @pytest.mark.dependency(
        depends=["TestEmptyWhole::test_end", "TestContainsShape::test_end"]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestAndSimpleShape::test_begin"])
    def test_disjoint(self):
        vertices0 = [(-2, -1), (-1, -1), (-1, 1), (-2, 1)]
        vertices1 = [(1, -1), (2, -1), (2, 1), (1, 1)]
        square0 = JordanPolygon(vertices0)
        square0 = SimpleShape(square0)
        square1 = JordanPolygon(vertices1)
        square1 = SimpleShape(square1)

        good_shape = EmptyShape()

        assert square0 & square0 == square0
        assert square1 & square1 == square1
        assert square0 & square1 is good_shape
        assert square1 & square0 is good_shape

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestAndSimpleShape::test_begin"])
    def test_complementar(self):
        vertices = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        jordan = JordanPolygon(vertices)
        square = SimpleShape(jordan)
        assert square & (~square) is EmptyShape()

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=["TestAndSimpleShape::test_begin", "TestAndSimpleShape::test_disjoint"]
    )
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

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestAndSimpleShape::test_begin",
            "TestAndSimpleShape::test_disjoint",
            "TestAndSimpleShape::test_complementar",
            "TestAndSimpleShape::test_two_squares",
        ]
    )
    def test_end(self):
        pass


class TestSubSimpleShape:
    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestEmptyWhole::test_end",
            "TestOrSimpleShape::test_end",
            "TestAndSimpleShape::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestSubSimpleShape::test_begin"])
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

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestSubSimpleShape::test_begin",
            "TestSubSimpleShape::test_two_squares",
        ]
    )
    def test_end(self):
        pass


class TestOthers:
    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestOrSimpleShape::test_end",
            "TestAndSimpleShape::test_end",
            "TestSubSimpleShape::test_end",
        ]
    )
    def test_print(self):
        points = [(0, 0), (1, 0), (0, 1)]
        jordancurve = JordanPolygon(points)
        shape = SimpleShape(jordancurve)
        str(shape)
        repr(shape)

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestOrSimpleShape::test_end",
            "TestAndSimpleShape::test_end",
            "TestSubSimpleShape::test_end",
        ]
    )
    def test_compare(self):
        points = [(0, 0), (1, 0), (0, 1)]
        jordancurve = JordanPolygon(points)
        shapea = SimpleShape(jordancurve)
        points = [(0, 0), (0, 1), (1, 0)]
        jordancurve = JordanPolygon(points)
        shapeb = SimpleShape(jordancurve)
        assert shapea != shapeb
        with pytest.raises(ValueError):
            shapea != 0


@pytest.mark.order(7)
@pytest.mark.dependency(
    depends=[
        "TestOrSimpleShape::test_end",
        "TestAndSimpleShape::test_end",
        "TestSubSimpleShape::test_end",
    ]
)
def test_end():
    pass
