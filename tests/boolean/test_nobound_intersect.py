"""
Tests related to verify the boolean operations between shapes that do
not intersect teach other.
"""

import pytest

from shapepy.core import Empty, Whole
from shapepy.primitive import Primitive
from shapepy.shape import ConnectedShape, DisjointShape


@pytest.mark.order(31)
@pytest.mark.dependency(
    depends=[
        "tests/test_empty_whole.py::test_end",
        "tests/test_point.py::test_end",
        "tests/test_boolean.py::test_end",
        "tests/test_primitive.py::test_end",
        "tests/test_shape.py::test_end",
        "tests/boolean/test_empty_whole.py::test_end",
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
        square_sma = Primitive.square(side=2)
        square_big = Primitive.square(side=4)

        assert square_sma | square_big == square_big
        assert square_big | square_sma == square_big
        assert square_sma | (~square_big) == DisjointShape(
            [square_sma, ~square_big]
        )
        assert square_big | (~square_sma) is Whole()
        assert (~square_sma) | square_big is Whole()
        assert (~square_big) | square_sma == DisjointShape(
            [square_sma, ~square_big]
        )
        assert (~square_sma) | (~square_big) == ~square_sma
        assert (~square_big) | (~square_sma) == ~square_sma

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTwoCenteredSquares::test_begin"])
    def test_and(self):
        square_sma = Primitive.square(side=2)
        square_big = Primitive.square(side=4)

        assert square_sma & square_big == square_sma
        assert square_big & square_sma == square_sma
        assert square_sma & (~square_big) is Empty()
        assert square_big & (~square_sma) == ConnectedShape(
            [square_big, ~square_sma]
        )
        assert (~square_sma) & square_big == ConnectedShape(
            [square_big, ~square_sma]
        )
        assert (~square_big) & square_sma is Empty()
        assert (~square_sma) & (~square_big) == ~square_big
        assert (~square_big) & (~square_sma) == ~square_big

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestTwoCenteredSquares::test_begin",
            "TestTwoCenteredSquares::test_or",
            "TestTwoCenteredSquares::test_and",
        ]
    )
    def test_sub(self):
        square_sma = Primitive.square(side=2)
        square_big = Primitive.square(side=4)

        assert square_sma - square_big is Empty()
        assert square_big - square_sma == ConnectedShape(
            [square_big, ~square_sma]
        )
        assert square_sma - (~square_big) == square_sma
        assert square_big - (~square_sma) == square_sma
        assert (~square_sma) - square_big == ~square_big
        assert (~square_big) - square_sma == ~square_big
        assert (~square_sma) - (~square_big) == ConnectedShape(
            [square_big, ~square_sma]
        )
        assert (~square_big) - (~square_sma) is Empty()

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestTwoCenteredSquares::test_begin",
            "TestTwoCenteredSquares::test_or",
            "TestTwoCenteredSquares::test_and",
        ]
    )
    def test_xor(self):
        square_sma = Primitive.square(side=2)
        square_big = Primitive.square(side=4)

        assert square_sma ^ square_big == ConnectedShape(
            [square_big, ~square_sma]
        )
        assert square_big ^ square_sma == ConnectedShape(
            [square_big, ~square_sma]
        )
        assert square_sma ^ (~square_big) == DisjointShape(
            [square_sma, ~square_big]
        )
        assert square_big ^ (~square_sma) == DisjointShape(
            [square_sma, ~square_big]
        )
        assert (~square_sma) ^ square_big == DisjointShape(
            [square_sma, ~square_big]
        )
        assert (~square_big) ^ square_sma == DisjointShape(
            [square_sma, ~square_big]
        )
        assert (~square_sma) ^ (~square_big) == ConnectedShape(
            [square_big, ~square_sma]
        )
        assert (~square_big) ^ (~square_sma) == ConnectedShape(
            [square_big, ~square_sma]
        )

    @pytest.mark.order(31)
    @pytest.mark.dependency(
        depends=[
            "TestTwoCenteredSquares::test_begin",
            "TestTwoCenteredSquares::test_or",
            "TestTwoCenteredSquares::test_and",
            "TestTwoCenteredSquares::test_sub",
            "TestTwoCenteredSquares::test_xor",
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
            "TestTwoCenteredSquares::test_end",
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

        assert left | right == DisjointShape([left, right])
        assert right | left == DisjointShape([left, right])
        assert left | (~right) == ~right
        assert right | (~left) == ~left
        assert (~left) | right == ~left
        assert (~right) | left == ~right
        assert (~left) | (~right) is Whole()
        assert (~right) | (~left) is Whole()

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTwoDisjointSquares::test_begin"])
    def test_and(self):
        left = Primitive.square(side=2, center=(-2, 0))
        right = Primitive.square(side=2, center=(2, 0))

        assert left & right is Empty()
        assert right & left is Empty()
        assert left & (~right) == left
        assert right & (~left) == right
        assert (~left) & right == right
        assert (~right) & left == left
        assert (~left) & (~right) == ConnectedShape([~left, ~right])
        assert (~right) & (~left) == ConnectedShape([~left, ~right])

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestTwoDisjointSquares::test_begin",
            "TestTwoDisjointSquares::test_or",
            "TestTwoDisjointSquares::test_and",
        ]
    )
    def test_sub(self):
        left = Primitive.square(side=2, center=(-2, 0))
        right = Primitive.square(side=2, center=(2, 0))

        assert left - right == left
        assert right - left == right
        assert left - (~right) is Empty()
        assert right - (~left) is Empty()
        assert (~left) - right == ConnectedShape([~left, ~right])
        assert (~right) - left == ConnectedShape([~left, ~right])
        assert (~left) - (~right) == right
        assert (~right) - (~left) == left

    @pytest.mark.order(31)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestTwoDisjointSquares::test_begin",
            "TestTwoDisjointSquares::test_or",
            "TestTwoDisjointSquares::test_and",
        ]
    )
    def test_xor(self):
        left = Primitive.square(side=1, center=(-2, 0))
        right = Primitive.square(side=1, center=(2, 0))

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
            "TestTwoDisjointSquares::test_xor",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(31)
@pytest.mark.dependency(
    depends=[
        "TestTwoCenteredSquares::test_end",
        "TestTwoDisjointSquares::test_end",
    ]
)
def test_end():
    pass
