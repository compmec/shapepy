"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve 
"""

import pytest

from compmec.shape.jordancurve import JordanCurve
from compmec.shape.primitive import Primitive
from compmec.shape.shape import EmptyShape, SimpleShape, WholeShape


@pytest.mark.order(8)
@pytest.mark.dependency(
    depends=[
        "tests/test_polygon.py::test_end",
        "tests/test_jordan_polygon.py::test_end",
        "tests/test_jordan_curve.py::test_end",
        "tests/test_primitive.py::test_end",
        "tests/test_calculus.py::test_end",
        "tests/test_contains.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestEmptyWhole:
    """
    Test relative to special cases, a empty shape and whole domain
    """

    @pytest.mark.order(8)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(8)
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

    @pytest.mark.order(8)
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

    @pytest.mark.order(8)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_xor(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty ^ empty is empty
        assert empty ^ whole is whole
        assert whole ^ empty is whole
        assert whole ^ whole is empty

    @pytest.mark.order(8)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_sub(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty - empty is empty
        assert empty - whole is empty
        assert whole - empty is whole
        assert whole - whole is empty

    @pytest.mark.order(8)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_bool(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert bool(empty) is False
        assert bool(whole) is True

    @pytest.mark.order(8)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_float(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert float(empty) == float(0)
        assert float(whole) == float("inf")

    @pytest.mark.order(8)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_invert(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert ~empty is whole
        assert ~whole is empty
        assert ~(~empty) is empty
        assert ~(~whole) is whole

    @pytest.mark.order(8)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_copy(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty.copy() is empty
        assert whole.copy() is whole

    @pytest.mark.order(8)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_begin"])
    def test_boolean_simple(self):
        empty = EmptyShape()
        whole = WholeShape()
        points = [(0, 0), (1, 0), (0, 1)]
        shape = Primitive.polygon(points)
        assert float(shape) > 0

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

    @pytest.mark.order(8)
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
            "TestEmptyWhole::test_boolean_simple",
        ]
    )
    def test_end(self):
        pass


class TestOrSimpleShape:
    @pytest.mark.order(8)
    @pytest.mark.dependency(depends=["TestEmptyWhole::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(8)
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

    @pytest.mark.order(8)
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

        test_shape = square0 | square1
        assert test_shape == good_shape

    @pytest.mark.order(8)
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
    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestEmptyWhole::test_end",
            "TestOrSimpleShape::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(8)
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

    @pytest.mark.order(8)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=["TestAndSimpleShape::test_begin", "TestAndSimpleShape::test_disjoint"]
    )
    def test_two_squares(self):
        square0 = Primitive.regular_polygon(nsides=4, radius=2, center=(-1, 0))
        square1 = Primitive.regular_polygon(nsides=4, radius=2, center=(1, 0))

        test = square0 & square1
        good = Primitive.regular_polygon(nsides=4, radius=1, center=(0, 0))
        assert test == good

    @pytest.mark.order(8)
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
    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestEmptyWhole::test_end",
            "TestOrSimpleShape::test_end",
            "TestAndSimpleShape::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(8)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestSubSimpleShape::test_begin"])
    def test_two_squares(self):
        square0 = Primitive.regular_polygon(nsides=4, radius=2, center=(-1, 0))
        square1 = Primitive.regular_polygon(nsides=4, radius=2, center=(1, 0))

        left_points = [(0, 1), (-1, 2), (-3, 0), (-1, -2), (0, -1), (-1, 0)]
        left_jordanpoly = JordanCurve.from_vertices(left_points)
        left_shape = SimpleShape(left_jordanpoly)
        right_points = [(0, 1), (1, 0), (0, -1), (1, -2), (3, 0), (1, 2)]
        right_jordanpoly = JordanCurve.from_vertices(right_points)
        right_shape = SimpleShape(right_jordanpoly)

        assert square0 - square1 == left_shape
        assert square1 - square0 == right_shape

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestSubSimpleShape::test_begin",
            "TestSubSimpleShape::test_two_squares",
        ]
    )
    def test_end(self):
        pass


class TestEqualSides:
    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestEmptyWhole::test_end",
            "TestOrSimpleShape::test_end",
            "TestAndSimpleShape::test_end",
            "TestSubSimpleShape::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(8)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestEqualSides::test_begin"])
    def test_or_triangles(self):
        vertices0 = [(0, 0), (1, 0), (0, 1)]
        vertices1 = [(0, 0), (0, 1), (-1, 0)]
        triangle0 = Primitive.polygon(vertices0)
        triangle1 = Primitive.polygon(vertices1)
        test = triangle0 | triangle1

        vertices = [(1, 0), (0, 1), (-1, 0)]
        good = Primitive.polygon(vertices)
        assert test == good

    @pytest.mark.order(8)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestEqualSides::test_begin",
            "TestEqualSides::test_or_triangles",
        ]
    )
    def test_and_triangles(self):
        vertices0 = [(0, 0), (2, 0), (0, 2)]
        vertices1 = [(0, 0), (1, 0), (0, 1)]
        triangle0 = Primitive.polygon(vertices0)
        triangle1 = Primitive.polygon(vertices1)
        test = triangle0 & triangle1

        vertices = [(0, 0), (1, 0), (0, 1)]
        good = Primitive.polygon(vertices)
        assert test == good

    @pytest.mark.order(8)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestEqualSides::test_begin",
            "TestEqualSides::test_or_triangles",
            "TestEqualSides::test_and_triangles",
        ]
    )
    def test_sub_triangles(self):
        vertices0 = [(0, 0), (2, 0), (0, 2)]
        vertices1 = [(0, 0), (1, 0), (0, 1)]
        triangle0 = Primitive.polygon(vertices0)
        triangle1 = Primitive.polygon(vertices1)
        test = triangle0 - triangle1

        vertices = [(1, 0), (2, 0), (0, 2), (0, 1)]
        good = Primitive.polygon(vertices)

        assert test == good

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestEqualSides::test_begin",
            "TestEqualSides::test_or_triangles",
            "TestEqualSides::test_and_triangles",
            "TestEqualSides::test_sub_triangles",
        ]
    )
    def test_end(self):
        pass


class TestOthers:
    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOrSimpleShape::test_end",
            "TestAndSimpleShape::test_end",
            "TestSubSimpleShape::test_end",
            "TestEqualSides::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
        ]
    )
    def test_print(self):
        points = [(0, 0), (1, 0), (0, 1)]
        jordancurve = JordanCurve.from_vertices(points)
        shape = SimpleShape(jordancurve)
        str(shape)
        repr(shape)

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
        ]
    )
    def test_compare(self):
        shapea = Primitive.regular_polygon(3)
        shapeb = Primitive.regular_polygon(4)
        assert shapea != shapeb
        with pytest.raises(ValueError):
            shapea != 0

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
            "TestOthers::test_print",
            "TestOthers::test_compare",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(8)
@pytest.mark.dependency(
    depends=[
        "TestOrSimpleShape::test_end",
        "TestAndSimpleShape::test_end",
        "TestSubSimpleShape::test_end",
        "TestEqualSides::test_end",
        "TestOthers::test_end",
    ]
)
def test_end():
    pass
