"""
This module tests when two shapes have common edges/segments
"""

import pytest

from shapepy.bool2d.base import EmptyShape, WholeShape
from shapepy.bool2d.config import set_auto_clean
from shapepy.bool2d.primitive import Primitive


@pytest.mark.order(43)
@pytest.mark.dependency(
    depends=[
        "tests/bool2d/test_primitive.py::test_end",
        "tests/bool2d/test_contains.py::test_end",
        "tests/bool2d/test_empty_whole.py::test_end",
        "tests/bool2d/test_shape.py::test_end",
        "tests/bool2d/test_lazy.py::test_all",
        "tests/bool2d/test_bool_no_intersect.py::test_end",
        "tests/bool2d/test_bool_finite_intersect.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestTriangle:
    @pytest.mark.order(38)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(38)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTriangle::test_begin"])
    def test_or_triangles(self):
        vertices0 = [(0, 0), (1, 0), (0, 1)]
        vertices1 = [(0, 0), (0, 1), (-1, 0)]
        triangle0 = Primitive.polygon(vertices0)
        triangle1 = Primitive.polygon(vertices1)
        test = triangle0 | triangle1

        vertices = [(1, 0), (0, 1), (-1, 0)]
        good = Primitive.polygon(vertices)
        assert test == good

    @pytest.mark.order(38)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestTriangle::test_begin",
            "TestTriangle::test_or_triangles",
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

    @pytest.mark.order(38)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestTriangle::test_begin",
            "TestTriangle::test_or_triangles",
            "TestTriangle::test_and_triangles",
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

    @pytest.mark.order(38)
    @pytest.mark.dependency(
        depends=[
            "TestTriangle::test_begin",
            "TestTriangle::test_or_triangles",
            "TestTriangle::test_and_triangles",
            "TestTriangle::test_sub_triangles",
        ]
    )
    def test_end(self):
        pass


class TestEqualSquare:
    """
    Make tests of boolean operations between the same shape (a square)
    """

    @pytest.mark.order(43)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(43)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestEqualSquare::test_begin"])
    def test_or(self):
        square = Primitive.square(side=1, center=(0, 0))
        assert square.area > 0
        assert square | square == square
        assert square | (~square) is WholeShape()
        assert (~square) | square is WholeShape()
        assert (~square) | (~square) == ~square

    @pytest.mark.order(43)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=["TestEqualSquare::test_begin", "TestEqualSquare::test_or"]
    )
    def test_and(self):
        square = Primitive.square(side=1, center=(0, 0))
        assert square.area > 0
        assert square & square == square
        assert square & (~square) is EmptyShape()
        assert (~square) & square is EmptyShape()
        assert (~square) & (~square) == ~square

    @pytest.mark.order(43)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestEqualSquare::test_begin",
            "TestEqualSquare::test_and",
        ]
    )
    def test_sub(self):
        square = Primitive.square(side=1, center=(0, 0))
        assert square.area > 0
        assert square - square is EmptyShape()
        assert square - (~square) == square
        assert (~square) - square == -square
        assert (~square) - (~square) is EmptyShape()

    @pytest.mark.order(43)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestEqualSquare::test_begin",
            "TestEqualSquare::test_or",
            "TestEqualSquare::test_and",
            "TestEqualSquare::test_sub",
        ]
    )
    def test_xor(self):
        square = Primitive.square(side=1, center=(0, 0))
        assert square.area > 0
        assert square ^ square is EmptyShape()
        assert square ^ (~square) is WholeShape()
        assert (~square) ^ square is WholeShape()
        assert (~square) ^ (~square) is EmptyShape()

    @pytest.mark.order(43)
    @pytest.mark.dependency(
        depends=[
            "TestEqualSquare::test_begin",
            "TestEqualSquare::test_or",
            "TestEqualSquare::test_and",
            "TestEqualSquare::test_sub",
            "TestEqualSquare::test_xor",
        ]
    )
    def test_end(self):
        pass


class TestEqualHollowSquare:
    """
    Make tests of boolean operations between the same shape (a square)
    """

    @pytest.mark.order(43)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestEqualSquare::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(43)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestEqualHollowSquare::test_begin"])
    def test_or(self):
        big = Primitive.square(side=2, center=(0, 0))
        small = Primitive.square(side=1, center=(0, 0))
        square = big - small
        assert square.area > 0
        assert square | square == square
        assert square | (~square) is WholeShape()
        assert (~square) | square is WholeShape()
        assert (~square) | (~square) == ~square

    @pytest.mark.order(43)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestEqualHollowSquare::test_begin",
            "TestEqualHollowSquare::test_or",
        ]
    )
    def test_and(self):
        big = Primitive.square(side=2, center=(0, 0))
        small = Primitive.square(side=1, center=(0, 0))
        square = big - small
        assert square.area > 0
        assert square & square == square
        assert square & (~square) is EmptyShape()
        assert (~square) & square is EmptyShape()
        assert (~square) & (~square) == ~square

    @pytest.mark.order(43)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestEqualHollowSquare::test_begin",
            "TestEqualHollowSquare::test_and",
        ]
    )
    def test_sub(self):
        big = Primitive.square(side=2, center=(0, 0))
        small = Primitive.square(side=1, center=(0, 0))
        square = big - small
        assert square.area > 0
        assert square - square is EmptyShape()
        assert square - (~square) == square
        assert (~square) - square == -square
        assert (~square) - (~square) is EmptyShape()

    @pytest.mark.order(43)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestEqualHollowSquare::test_begin",
            "TestEqualHollowSquare::test_or",
            "TestEqualHollowSquare::test_and",
            "TestEqualHollowSquare::test_sub",
        ]
    )
    def test_xor(self):
        big = Primitive.square(side=2, center=(0, 0))
        small = Primitive.square(side=1, center=(0, 0))
        square = big - small
        assert square.area > 0
        assert square ^ square is EmptyShape()
        assert square ^ (~square) is WholeShape()
        assert (~square) ^ square is WholeShape()
        assert (~square) ^ (~square) is EmptyShape()

    @pytest.mark.order(43)
    @pytest.mark.dependency(
        depends=[
            "TestEqualHollowSquare::test_begin",
            "TestEqualHollowSquare::test_or",
            "TestEqualHollowSquare::test_and",
            "TestEqualHollowSquare::test_sub",
            "TestEqualHollowSquare::test_xor",
        ]
    )
    def test_end(self):
        pass


class TestTriangle:
    @pytest.mark.order(43)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(43)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTriangle::test_begin"])
    def test_or_triangles(self):
        vertices0 = [(0, 0), (1, 0), (0, 1)]
        vertices1 = [(0, 0), (0, 1), (-1, 0)]
        triangle0 = Primitive.polygon(vertices0)
        triangle1 = Primitive.polygon(vertices1)

        vertices = [(1, 0), (0, 1), (-1, 0)]
        good = Primitive.polygon(vertices)
        assert triangle0 + triangle1 == good

    @pytest.mark.order(43)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestTriangle::test_begin",
            "TestTriangle::test_or_triangles",
        ]
    )
    def test_and_triangles(self):
        vertices0 = [(0, 0), (2, 0), (0, 2)]
        vertices1 = [(0, 0), (1, 0), (0, 1)]
        triangle0 = Primitive.polygon(vertices0)
        triangle1 = Primitive.polygon(vertices1)

        vertices = [(0, 0), (1, 0), (0, 1)]
        good = Primitive.polygon(vertices)
        assert triangle0 * triangle1 == good

    @pytest.mark.order(43)
    @pytest.mark.skip(reason="Fails due to float precision on py3.11")
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestTriangle::test_begin",
            "TestTriangle::test_or_triangles",
            "TestTriangle::test_and_triangles",
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

    @pytest.mark.order(43)
    @pytest.mark.dependency(
        depends=[
            "TestTriangle::test_begin",
            "TestTriangle::test_or_triangles",
            "TestTriangle::test_and_triangles",
        ]
    )
    def test_end(self):
        pass


class TestDisabledClean:
    """
    Make tests of boolean operations between the same shape (a square)
    """

    @pytest.mark.order(43)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestEqualSquare::test_end",
            "TestEqualHollowSquare::test_end",
            "TestTriangle::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(43)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestDisabledClean::test_begin"])
    def test_or(self):
        big = Primitive.square(side=2, center=(0, 0))
        small = Primitive.square(side=1, center=(0, 0))
        left = Primitive.circle(radius=3, center=(-10, 0))
        right = Primitive.circle(radius=3, center=(10, 0))
        with set_auto_clean(False):
            shape = big - small | left ^ right
            assert shape | shape == shape
            assert shape | (~shape) is WholeShape()
            assert (~shape) | shape is WholeShape()
            assert (~shape) | (~shape) == ~shape

    @pytest.mark.order(43)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestDisabledClean::test_begin",
            "TestDisabledClean::test_or",
        ]
    )
    def test_and(self):
        big = Primitive.square(side=2, center=(0, 0))
        small = Primitive.square(side=1, center=(0, 0))
        left = Primitive.circle(radius=3, center=(-10, 0))
        right = Primitive.circle(radius=3, center=(10, 0))
        with set_auto_clean(False):
            shape = big - small | left ^ right
            assert shape & shape == shape
            assert shape & (~shape) is EmptyShape()
            assert (~shape) & shape is EmptyShape()
            assert (~shape) & (~shape) == ~shape

    @pytest.mark.order(43)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestDisabledClean::test_begin",
            "TestDisabledClean::test_and",
        ]
    )
    def test_sub(self):
        big = Primitive.square(side=2, center=(0, 0))
        small = Primitive.square(side=1, center=(0, 0))
        left = Primitive.circle(radius=3, center=(-10, 0))
        right = Primitive.circle(radius=3, center=(10, 0))
        with set_auto_clean(False):
            shape = big - small | left ^ right
            assert shape - shape is EmptyShape()
            assert shape - (~shape) == shape
            assert (~shape) - shape == ~shape
            assert (~shape) - (~shape) is EmptyShape()

    @pytest.mark.order(43)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestDisabledClean::test_begin",
            "TestDisabledClean::test_or",
            "TestDisabledClean::test_and",
            "TestDisabledClean::test_sub",
        ]
    )
    def test_xor(self):
        big = Primitive.square(side=2, center=(0, 0))
        small = Primitive.square(side=1, center=(0, 0))
        left = Primitive.circle(radius=3, center=(-10, 0))
        right = Primitive.circle(radius=3, center=(10, 0))
        with set_auto_clean(False):
            shape = big - small | left ^ right
            assert shape ^ shape is EmptyShape()
            assert shape ^ (~shape) is WholeShape()
            assert (~shape) ^ shape is WholeShape()
            assert (~shape) ^ (~shape) is EmptyShape()

    @pytest.mark.order(43)
    @pytest.mark.dependency(
        depends=[
            "TestDisabledClean::test_begin",
            "TestDisabledClean::test_or",
            "TestDisabledClean::test_and",
            "TestDisabledClean::test_sub",
            "TestDisabledClean::test_xor",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(43)
@pytest.mark.dependency(
    depends=[
        "TestEqualSquare::test_end",
        "TestEqualHollowSquare::test_end",
        "TestTriangle::test_end",
        "TestDisabledClean::test_end",
    ]
)
def test_end():
    pass
