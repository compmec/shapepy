"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve
"""

import pytest

from shapepy.bool2d.base import EmptyShape, WholeShape
from shapepy.bool2d.primitive import Primitive
from shapepy.bool2d.shape import ConnectedShape, DisjointShape


@pytest.mark.order(31)
@pytest.mark.dependency(
    depends=[
        "tests/bool2d/test_primitive.py::test_end",
        "tests/bool2d/test_contains.py::test_end",
        "tests/bool2d/test_empty_whole.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestTwoCenteredSquares:
    """
    Make tests when a shape is completely inside another shape

    The operation (shape - shape) may result in a connected shape
    which is tested in other file
    """

    @pytest.mark.order(31)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTwoCenteredSquares::test_begin"])
    def test_or(self):
        square1 = Primitive.square(side=1)
        square2 = Primitive.square(side=2)
        assert square1.area > 0
        assert square2.area > 0

        assert square1 | square2 == square2
        assert square2 | square1 == square2
        assert square1 | (~square2) == DisjointShape([square1, ~square2])
        assert square2 | (~square1) is WholeShape()
        assert (~square1) | square2 is WholeShape()
        assert (~square2) | square1 == DisjointShape([square1, ~square2])
        assert (~square1) | (~square2) == ~square1
        assert (~square2) | (~square1) == ~square1

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTwoCenteredSquares::test_begin"])
    def test_and(self):
        square1 = Primitive.square(side=1)
        square2 = Primitive.square(side=2)
        assert square1.area > 0
        assert square2.area > 0

        assert square1 & square2 == square1
        assert square2 & square1 == square1
        assert square1 & (~square2) is EmptyShape()
        assert square2 & (~square1) == ConnectedShape([square2, ~square1])
        assert (~square1) & square2 == ConnectedShape([square2, ~square1])
        assert (~square2) & square1 is EmptyShape()
        assert (~square1) & (~square2) == ~square2
        assert (~square2) & (~square1) == ~square2

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTwoCenteredSquares::test_begin"])
    def test_sub(self):
        square1 = Primitive.square(side=1)
        square2 = Primitive.square(side=2)
        assert square1.area > 0
        assert square2.area > 0

        assert square1 - square2 is EmptyShape()
        assert square2 - square1 == ConnectedShape([square2, ~square1])
        assert square1 - (~square2) == square1
        assert square2 - (~square1) == square1
        assert (~square1) - square2 == ~square2
        assert (~square2) - square1 == ~square2
        assert (~square1) - (~square2) == ConnectedShape([square2, ~square1])
        assert (~square2) - (~square1) is EmptyShape()

    @pytest.mark.order(31)
    @pytest.mark.skip("Needs implementation of Graph: #14")
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTwoCenteredSquares::test_begin"])
    def test_xor(self):
        square1 = Primitive.square(side=1)
        square2 = Primitive.square(side=2)
        assert square1.area > 0
        assert square2.area > 0

        assert square1 ^ square2 == ConnectedShape([square2, ~square1])
        assert square2 ^ square1 == ConnectedShape([square2, ~square1])
        assert square1 ^ (~square2) == DisjointShape([square1, ~square2])
        assert square2 ^ (~square1) == DisjointShape([square1, ~square2])
        assert (~square1) ^ square2 == DisjointShape([square1, ~square2])
        assert (~square2) ^ square1 == DisjointShape([square1, ~square2])
        assert (~square1) ^ (~square2) == ConnectedShape([square2, ~square1])
        assert (~square2) ^ (~square1) == ConnectedShape([square2, ~square1])

    @pytest.mark.order(31)
    @pytest.mark.dependency(
        depends=[
            "TestTwoCenteredSquares::test_begin",
            "TestTwoCenteredSquares::test_or",
            "TestTwoCenteredSquares::test_and",
            "TestTwoCenteredSquares::test_sub",
        ]
    )
    def test_end(self):
        pass


class TestTwoDisjointSquares:
    """
    Make tests when a shape is completely inside another shape

    The operation (shape - shape) may result in a connected shape
    which is tested in other file
    """

    @pytest.mark.order(31)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTwoDisjointSquares::test_begin"])
    def test_or(self):
        left = Primitive.square(side=2, center=(-2, 0))
        right = Primitive.square(side=2, center=(2, 0))
        assert left.area > 0
        assert right.area > 0

        assert left | right == DisjointShape([left, right])
        assert right | left == DisjointShape([left, right])
        assert left | (~right) == ~right
        assert right | (~left) == ~left
        assert (~left) | right == ~left
        assert (~right) | left == ~right
        assert (~left) | (~right) is WholeShape()
        assert (~right) | (~left) is WholeShape()

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTwoDisjointSquares::test_begin"])
    def test_and(self):
        left = Primitive.square(side=2, center=(-2, 0))
        right = Primitive.square(side=2, center=(2, 0))
        assert left.area > 0
        assert right.area > 0

        assert left & right is EmptyShape()
        assert right & left is EmptyShape()
        assert left & (~right) == left
        assert right & (~left) == right
        assert (~left) & right == right
        assert (~right) & left == left
        assert (~left) & (~right) == ConnectedShape([~left, ~right])
        assert (~right) & (~left) == ConnectedShape([~left, ~right])

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTwoDisjointSquares::test_begin"])
    def test_sub(self):
        left = Primitive.square(side=2, center=(-2, 0))
        right = Primitive.square(side=2, center=(2, 0))
        assert left.area > 0
        assert right.area > 0

        assert left - right == left
        assert right - left == right
        assert left - (~right) is EmptyShape()
        assert right - (~left) is EmptyShape()
        assert (~left) - right == ConnectedShape([~left, ~right])
        assert (~right) - left == ConnectedShape([~left, ~right])
        assert (~left) - (~right) == right
        assert (~right) - (~left) == left

    @pytest.mark.order(31)
    @pytest.mark.skip("Needs implementation of Graph: #14")
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTwoDisjointSquares::test_begin"])
    def test_xor(self):
        left = Primitive.square(side=1, center=(-2, 0))
        right = Primitive.square(side=1, center=(2, 0))
        assert left.area > 0
        assert right.area > 0

        assert left ^ right == DisjointShape([left, right])
        assert right ^ left == DisjointShape([left, right])
        assert left ^ (~right) == ConnectedShape([~left, ~right])
        assert right ^ (~left) == ConnectedShape([~left, ~right])
        assert (~left) ^ right == ConnectedShape([~left, ~right])
        assert (~right) ^ left == ConnectedShape([~left, ~right])
        assert (~left) ^ (~right) == DisjointShape([left, right])
        assert (~right) ^ (~left) == DisjointShape([left, right])

    @pytest.mark.order(31)
    @pytest.mark.dependency(
        depends=[
            "TestTwoDisjointSquares::test_begin",
            "TestTwoDisjointSquares::test_or",
            "TestTwoDisjointSquares::test_and",
            "TestTwoDisjointSquares::test_sub",
        ]
    )
    def test_end(self):
        pass


class TestTwoDisjHollowSquares:
    """
    Make tests when a shape is completely inside another shape

    The operation (shape - shape) may result in a connected shape
    which is tested in other file
    """

    @pytest.mark.order(31)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestTwoCenteredSquares::test_end",
            "TestTwoDisjointSquares::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTwoDisjHollowSquares::test_begin"])
    def test_or(self):
        left_big = Primitive.square(side=2, center=(-2, 0))
        left_sma = Primitive.square(side=1, center=(-2, 0))
        right_big = Primitive.square(side=2, center=(2, 0))
        right_sma = Primitive.square(side=1, center=(2, 0))
        left = left_big - left_sma
        right = right_big - right_sma
        assert left.area > 0
        assert right.area > 0

        assert left | right == DisjointShape([left, right])
        assert right | left == DisjointShape([left, right])
        assert left | (~right) == ~right
        assert right | (~left) == ~left
        assert (~left) | right == ~left
        assert (~right) | left == ~right
        assert (~left) | (~right) is WholeShape()
        assert (~right) | (~left) is WholeShape()

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTwoDisjHollowSquares::test_begin"])
    def test_and(self):
        left_big = Primitive.square(side=2, center=(-2, 0))
        left_sma = Primitive.square(side=1, center=(-2, 0))
        right_big = Primitive.square(side=2, center=(2, 0))
        right_sma = Primitive.square(side=1, center=(2, 0))
        left = left_big - left_sma
        right = right_big - right_sma
        assert left.area > 0
        assert right.area > 0

        assert left & right is EmptyShape()
        assert right & left is EmptyShape()
        assert left & (~right) == left
        assert right & (~left) == right
        assert (~left) & right == right
        assert (~right) & left == left
        external = ConnectedShape([~left_big, ~right_big])
        good = DisjointShape([left_sma, right_sma, external])
        assert (~left) & (~right) == good
        assert (~right) & (~left) == good

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTwoDisjHollowSquares::test_begin"])
    def test_sub(self):
        left_big = Primitive.square(side=2, center=(-2, 0))
        left_sma = Primitive.square(side=1, center=(-2, 0))
        right_big = Primitive.square(side=2, center=(2, 0))
        right_sma = Primitive.square(side=1, center=(2, 0))
        left = left_big - left_sma
        right = right_big - right_sma
        assert left.area > 0
        assert right.area > 0

        assert left - right == left
        assert right - left == right
        assert left - (~right) is EmptyShape()
        assert right - (~left) is EmptyShape()
        external = ConnectedShape([~left_big, ~right_big])
        good = DisjointShape([left_sma, right_sma, external])
        assert (~left) & (~right) == good
        assert (~right) & (~left) == good
        assert (~left) - (~right) == right
        assert (~right) - (~left) == left

    @pytest.mark.order(31)
    @pytest.mark.skip("Needs implementation of Graph: #14")
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTwoDisjHollowSquares::test_begin"])
    def test_xor(self):
        left_big = Primitive.square(side=2, center=(-2, 0))
        left_sma = Primitive.square(side=1, center=(-2, 0))
        right_big = Primitive.square(side=2, center=(2, 0))
        right_sma = Primitive.square(side=1, center=(2, 0))
        left = left_big - left_sma
        right = right_big - right_sma
        assert left.area > 0
        assert right.area > 0

        assert left ^ right == DisjointShape([left, right])
        assert right ^ left == DisjointShape([left, right])
        external = ConnectedShape([~left_big, ~right_big])
        good = DisjointShape([left_sma, right_sma, external])
        assert left ^ (~right) == good
        assert right ^ (~left) == good
        assert (~left) ^ right == good
        assert (~right) ^ left == good
        assert (~left) ^ (~right) == DisjointShape([left, right])
        assert (~right) ^ (~left) == DisjointShape([left, right])

    @pytest.mark.order(31)
    @pytest.mark.dependency(
        depends=[
            "TestTwoDisjHollowSquares::test_begin",
            "TestTwoDisjHollowSquares::test_or",
            "TestTwoDisjHollowSquares::test_and",
            "TestTwoDisjHollowSquares::test_sub",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(31)
@pytest.mark.dependency(
    depends=[
        "TestTwoCenteredSquares::test_end",
        "TestTwoDisjointSquares::test_end",
        "TestTwoDisjHollowSquares::test_end",
    ]
)
def test_end():
    pass
