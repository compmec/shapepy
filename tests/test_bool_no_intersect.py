"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve 
"""

import pytest

from compmec.shape.primitive import Primitive
from compmec.shape.shape import ConnectedShape, DisjointShape, EmptyShape


@pytest.mark.order(9)
@pytest.mark.dependency(
    depends=[
        "tests/test_polygon.py::test_end",
        "tests/test_jordan_polygon.py::test_end",
        "tests/test_jordan_curve.py::test_end",
        "tests/test_primitive.py::test_end",
        "tests/test_contains.py::test_end",
        "tests/test_empty_whole.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestEqualSimpleShape:
    """
    Make tests of boolean operations between the same shape
    """

    @pytest.mark.order(9)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(9)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestEqualSimpleShape::test_begin"])
    def test_or_square(self):
        square = Primitive.square(side=1, center=(0, 0))
        assert float(square) > 0
        assert square | square == square

    @pytest.mark.order(9)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestEqualSimpleShape::test_begin"])
    def test_and_square(self):
        square = Primitive.square(side=1, center=(0, 0))
        assert float(square) > 0
        assert square & square == square

    @pytest.mark.order(9)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestEqualSimpleShape::test_begin",
            "TestEqualSimpleShape::test_and_square",
        ]
    )
    def test_sub_square(self):
        square = Primitive.square(side=1, center=(0, 0))
        assert float(square) > 0
        assert square - square is EmptyShape()

    @pytest.mark.order(9)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestEqualSimpleShape::test_begin",
            "TestEqualSimpleShape::test_and_square",
            "TestEqualSimpleShape::test_sub_square",
        ]
    )
    def test_xor_square(self):
        square = Primitive.square(side=1, center=(0, 0))
        assert float(square) > 0
        assert square ^ square is EmptyShape()

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestEqualSimpleShape::test_begin",
            "TestEqualSimpleShape::test_or_square",
            "TestEqualSimpleShape::test_and_square",
            "TestEqualSimpleShape::test_sub_square",
            "TestEqualSimpleShape::test_xor_square",
        ]
    )
    def test_end(self):
        pass


class TestCompleteInside:
    """
    Make tests when a shape is completely inside another shape

    The operation (shape - shape) may result in a connected shape
    which is tested in other file
    """

    @pytest.mark.order(9)
    @pytest.mark.dependency(depends=["test_begin", "TestEqualSimpleShape::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(9)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestCompleteInside::test_begin"])
    def test_or_squares(self):
        small_square = Primitive.square(side=1, center=(0, 0))
        big_square = Primitive.square(side=2, center=(0, 0))

        assert float(small_square) > 0
        assert float(big_square) > 0

        assert small_square | small_square == small_square
        assert small_square | big_square == big_square
        assert big_square | small_square == big_square
        assert big_square | big_square == big_square

        assert (~small_square) | small_square is Primitive.whole
        assert small_square | (~small_square) is Primitive.whole
        assert (~small_square) | big_square is Primitive.whole
        assert big_square | (~small_square) is Primitive.whole
        assert (~big_square) | big_square is Primitive.whole
        assert big_square | (~big_square) is Primitive.whole
        good = DisjointShape([small_square, ~big_square])
        assert small_square | (~big_square) == good
        assert (~big_square) | small_square == good

        assert (~small_square) | (~small_square) == ~small_square
        assert (~small_square) | (~big_square) == ~small_square
        assert (~big_square) | (~small_square) == ~small_square
        assert (~big_square) | (~big_square) == ~big_square

    @pytest.mark.order(9)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestCompleteInside::test_begin"])
    def test_and_squares(self):
        small_square = Primitive.square(side=1, center=(0, 0))
        big_square = Primitive.square(side=2, center=(0, 0))

        assert float(small_square) > 0
        assert float(big_square) > 0

        assert small_square & small_square == small_square
        assert small_square & big_square == small_square
        assert big_square & small_square == small_square
        assert big_square & big_square == big_square

        assert (~small_square) & small_square is Primitive.empty
        assert small_square & (~small_square) is Primitive.empty
        good = ConnectedShape([big_square, ~small_square])
        assert (~small_square) & big_square == good
        assert big_square & (~small_square) == good
        assert (~big_square) & big_square is Primitive.empty
        assert big_square & (~big_square) is Primitive.empty
        assert small_square & (~big_square) is Primitive.empty
        assert (~big_square) & small_square is Primitive.empty

        assert (~small_square) & (~small_square) == ~small_square
        assert (~small_square) & (~big_square) == ~big_square
        assert (~big_square) & (~small_square) == ~big_square
        assert (~big_square) & (~big_square) == ~big_square

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestCompleteInside::test_begin",
            "TestCompleteInside::test_or_squares",
            "TestCompleteInside::test_and_squares",
        ]
    )
    def test_end(self):
        pass


class TestDisjoint:
    """
    Make tests when a shape is completely inside another shape

    The operation (shape - shape) may result in a connected shape
    which is tested in other file
    """

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestEqualSimpleShape::test_end",
            "TestCompleteInside::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(9)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestDisjoint::test_begin"])
    def test_or_squares(self):
        square0 = Primitive.square(side=2, center=(-2, 0))
        square1 = Primitive.square(side=2, center=(2, 0))

        union = DisjointShape([square0, square1])

        assert float(square0) > 0
        assert float(square1) > 0

        assert square0 | square0 == square0
        assert square1 | square1 == square1
        assert square0 | square1 == union
        assert square1 | square0 == union

    @pytest.mark.order(9)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestDisjoint::test_begin"])
    def test_and_squares(self):
        square0 = Primitive.square(side=2, center=(-2, 0))
        square1 = Primitive.square(side=2, center=(2, 0))

        assert float(square0) > 0
        assert float(square1) > 0

        assert square0 & square0 == square0
        assert square1 & square1 == square1
        assert square0 & square1 is EmptyShape()
        assert square1 & square0 is EmptyShape()

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestDisjoint::test_begin",
            "TestDisjoint::test_or_squares",
            "TestDisjoint::test_and_squares",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(9)
@pytest.mark.dependency(
    depends=[
        "TestEqualSimpleShape::test_end",
        "TestCompleteInside::test_end",
        "TestDisjoint::test_end",
    ]
)
def test_end():
    pass
