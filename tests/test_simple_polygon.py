"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve 
"""

import pytest

from compmec.shape.jordancurve import JordanPolygon
from compmec.shape.primitive import Primitive
from compmec.shape.shape import EmptyShape, SimpleShape, WholeShape


@pytest.mark.order(6)
@pytest.mark.dependency(
    depends=[
        "tests/test_polygon.py::test_end",
        "tests/test_jordan_polygon.py::test_end",
        "tests/test_jordan_curve.py::test_end",
        "tests/test_primitive.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestEmptyWhole:
    """
    Test relative to special cases, a empty shape and whole domain
    """

    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_contains(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty in empty
        assert empty in whole
        assert whole not in empty
        assert whole in whole

    @pytest.mark.order(6)
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

    @pytest.mark.order(6)
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

    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_xor(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty ^ empty is empty
        assert empty ^ whole is whole
        assert whole ^ empty is whole
        assert whole ^ whole is empty

    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_sub(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty - empty is empty
        assert empty - whole is empty
        assert whole - empty is whole
        assert whole - whole is empty

    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_bool(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert bool(empty) is False
        assert bool(whole) is True

    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_float(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert float(empty) == float(0)
        assert float(whole) == float("inf")

    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_invert(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert ~empty is whole
        assert ~whole is empty
        assert ~(~empty) is empty
        assert ~(~whole) is whole

    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_copy(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty.copy() is empty
        assert whole.copy() is whole

    @pytest.mark.order(6)
    @pytest.mark.dependency(
        depends=[
            "TestEmptyWhole::test_begin",
            "TestEmptyWhole::test_contains",
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
    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(6)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestContainsPoint::test_begin"])
    def test_point_in_square(self):
        vertices = [(-2, -2), (2, -2), (2, 2), (-2, 2)]
        square = JordanPolygon(vertices)
        square = SimpleShape(square)
        assert float(square) > 0

        for xval in range(-2, 3):
            for yval in range(-2, 3):
                assert (xval, yval) in square

    @pytest.mark.order(6)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestContainsPoint::test_begin"])
    def test_point_out_square(self):
        vertices = [(-2, -2), (2, -2), (2, 2), (-2, 2)]
        square = JordanPolygon(vertices)
        square = SimpleShape(square)
        assert float(square) > 0

        for xval in range(-4, 5):
            for yval in range(-4, 5):
                if -2 <= xval and xval <= 2 and -2 <= yval and yval <= 2:
                    continue
                assert (xval, yval) not in square

    @pytest.mark.order(6)
    @pytest.mark.dependency(
        depends=[
            "TestContainsPoint::test_begin",
            "TestContainsPoint::test_point_in_square",
            "TestContainsPoint::test_point_out_square",
        ]
    )
    def test_end(self):
        pass


class TestContainsJordan:
    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["TestContainsPoint::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(6)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestContainsJordan::test_begin"])
    def test_square_in_square(self):
        small_vertices = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        big_vertices = [(-2, -2), (2, -2), (2, 2), (-2, 2)]
        small_jordan = JordanPolygon(small_vertices)
        big_jordan = JordanPolygon(big_vertices)
        small_square = SimpleShape(small_jordan)
        big_square = SimpleShape(big_jordan)

        assert float(small_square) > 0
        assert float(big_square) > 0
        assert small_jordan in big_square
        assert big_jordan not in small_square

    @pytest.mark.order(6)
    @pytest.mark.dependency(
        depends=[
            "TestContainsJordan::test_begin",
            "TestContainsJordan::test_square_in_square",
        ]
    )
    def test_end(self):
        pass


class TestContainsShape:
    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["TestContainsJordan::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(6)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestContainsShape::test_begin"])
    def test_empty_whole(self):
        empty = EmptyShape()
        whole = WholeShape()
        points = [(0, 0), (1, 0), (0, 1)]
        shape = Primitive.polygon(points)
        assert float(shape) > 0

        # contains
        assert shape in whole
        assert shape not in empty
        assert whole not in shape
        assert empty in shape

        # OR
        assert shape | empty == shape
        assert shape | whole is whole
        assert empty | shape == shape
        assert whole | shape is whole

        # AND
        assert shape & empty is empty
        assert shape & whole == shape
        assert empty & shape is empty
        assert whole & shape == shape

        # XOR
        assert shape ^ empty == shape
        # assert shape ^ whole == ~shape
        assert empty ^ shape == shape
        # assert whole ^ shape == ~shape

        # SUB
        assert shape - empty == shape
        assert shape - whole is empty
        assert empty - shape is empty
        # assert whole - shape == ~shape

    @pytest.mark.order(6)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestContainsShape::test_begin"])
    def test_square_in_square(self):
        small_vertices = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        big_vertices = [(-2, -2), (2, -2), (2, 2), (-2, 2)]
        small_square = Primitive.polygon(small_vertices)
        big_square = Primitive.polygon(big_vertices)

        assert float(small_square) > 0
        assert float(big_square) > 0
        assert small_square in small_square
        assert small_square in big_square
        assert big_square in big_square
        assert big_square not in small_square

    @pytest.mark.order(6)
    @pytest.mark.dependency(
        depends=[
            "TestContainsShape::test_begin",
            "TestContainsShape::test_empty_whole",
            "TestContainsShape::test_square_in_square",
        ]
    )
    def test_end(self):
        pass


class TestOrSimpleShape:
    @pytest.mark.order(6)
    @pytest.mark.dependency(
        depends=["TestEmptyWhole::test_end", "TestContainsShape::test_end"]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(6)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestOrSimpleShape::test_begin"])
    def test_inside_each(self):
        small_square = Primitive.square(side=1, center=(0, 0))
        big_square = Primitive.square(side=2, center=(0, 0))

        assert float(small_square) > 0
        assert float(big_square) > 0

        assert small_square | small_square == small_square
        assert small_square | big_square == big_square
        assert big_square | small_square == big_square
        assert big_square | big_square == big_square

    @pytest.mark.order(6)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=["TestOrSimpleShape::test_begin", "TestOrSimpleShape::test_inside_each"]
    )
    def test_two_squares(self):
        square0 = Primitive.regular_polygon(nsides=4, radius=2, center=(-1, 0))
        square1 = Primitive.regular_polygon(nsides=4, radius=2, center=(1, 0))

        assert float(square0) > 0
        assert float(square1) > 0

        good_points = [(0, 1), (-1, 2), (-3, 0), (-1, -2)]
        good_points += [(0, -1), (1, -2), (3, 0), (1, 2)]
        good_shape = Primitive.polygon(good_points)

        assert square0 | square1 == good_shape

    @pytest.mark.order(6)
    @pytest.mark.dependency(
        depends=[
            "TestOrSimpleShape::test_begin",
            "TestOrSimpleShape::test_inside_each",
            "TestOrSimpleShape::test_two_squares",
        ]
    )
    def test_end(self):
        pass


class TestAndSimpleShape:
    @pytest.mark.order(6)
    @pytest.mark.dependency(
        depends=["TestEmptyWhole::test_end", "TestContainsShape::test_end"]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(6)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestAndSimpleShape::test_begin"])
    def test_disjoint(self):
        square0 = Primitive.square(side=2, center=(-2, 0))
        square1 = Primitive.square(side=2, center=(2, 0))

        assert float(square0) > 0
        assert float(square1) > 0

        assert square0 & square0 == square0
        assert square1 & square1 == square1
        assert square0 & square1 is EmptyShape()
        assert square1 & square0 is EmptyShape()

    @pytest.mark.order(6)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=["TestAndSimpleShape::test_begin", "TestAndSimpleShape::test_disjoint"]
    )
    def test_two_squares(self):
        square0 = Primitive.regular_polygon(nsides=4, radius=2, center=(-1, 0))
        square1 = Primitive.regular_polygon(nsides=4, radius=2, center=(1, 0))
        good_shape = Primitive.regular_polygon(nsides=4, radius=1, center=(0, 0))

        assert square0 & square1 == good_shape

    @pytest.mark.order(6)
    @pytest.mark.dependency(
        depends=[
            "TestAndSimpleShape::test_begin",
            "TestAndSimpleShape::test_disjoint",
            "TestAndSimpleShape::test_two_squares",
        ]
    )
    def test_end(self):
        pass


class TestSubSimpleShape:
    @pytest.mark.order(6)
    @pytest.mark.dependency(
        depends=[
            "TestEmptyWhole::test_end",
            "TestOrSimpleShape::test_end",
            "TestAndSimpleShape::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(6)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestSubSimpleShape::test_begin"])
    def test_two_squares(self):
        square0 = Primitive.regular_polygon(nsides=4, radius=2, center=(-1, 0))
        square1 = Primitive.regular_polygon(nsides=4, radius=2, center=(1, 0))

        left_points = [(0, 1), (-1, 2), (-3, 0), (-1, -2), (0, -1), (-1, 0)]
        left_jordanpoly = JordanPolygon(left_points)
        left_shape = SimpleShape(left_jordanpoly)
        right_points = [(0, 1), (1, 0), (0, -1), (1, -2), (3, 0), (1, 2)]
        right_jordanpoly = JordanPolygon(right_points)
        right_shape = SimpleShape(right_jordanpoly)

        assert square0 - square1 == left_shape
        assert square1 - square0 == right_shape

    @pytest.mark.order(6)
    @pytest.mark.dependency(
        depends=[
            "TestSubSimpleShape::test_begin",
            "TestSubSimpleShape::test_two_squares",
        ]
    )
    def test_end(self):
        pass


class TestOthers:
    @pytest.mark.order(6)
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

    @pytest.mark.order(6)
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
        points = [(0, 0), (1, 0), (1, 1), (0, 1)]
        jordancurve = JordanPolygon(points)
        shapeb = SimpleShape(jordancurve)
        assert shapea != shapeb
        with pytest.raises(ValueError):
            shapea != 0


@pytest.mark.order(6)
@pytest.mark.dependency(
    depends=[
        "TestOrSimpleShape::test_end",
        "TestAndSimpleShape::test_end",
        "TestSubSimpleShape::test_end",
    ]
)
def test_end():
    pass
