"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve
"""

import pytest

from shapepy.primitive import Primitive
from shapepy.shape import SimpleShape
from shapepy.shape.boolean import close_shape


@pytest.mark.order(32)
@pytest.mark.dependency(
    depends=[
        "tests/test_point.py::test_end",
        "tests/test_primitive.py::test_end",
        "tests/test_shape.py::test_end",
        "tests/boolean/test_empty_whole.py::test_end",
        "tests/boolean/test_nobound_intersect.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestIntersectionSimple:
    """
    Tests between two simple shapes such they have a finite
    number of intersection points
    """

    @pytest.mark.order(32)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(32)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestIntersectionSimple::test_begin"])
    def test_or_two_rombos(self):
        square0 = Primitive.regular_polygon(nsides=4, radius=2, center=(-1, 0))
        square1 = Primitive.regular_polygon(nsides=4, radius=2, center=(1, 0))

        good_points = [(0, 1), (-1, 2), (-3, 0), (-1, -2)]
        good_points += [(0, -1), (1, -2), (3, 0), (1, 2)]
        good_shape = Primitive.polygon(good_points)

        test_shape = close_shape(square0 | square1)
        assert test_shape == good_shape

    @pytest.mark.order(32)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestIntersectionSimple::test_begin"])
    def test_and_two_rombos(self):
        square0 = Primitive.regular_polygon(nsides=4, radius=2, center=(-1, 0))
        square1 = Primitive.regular_polygon(nsides=4, radius=2, center=(1, 0))

        test = close_shape(square0 & square1)
        good = Primitive.regular_polygon(nsides=4, radius=1, center=(0, 0))
        assert test == good

    @pytest.mark.order(32)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestIntersectionSimple::test_begin",
            "TestIntersectionSimple::test_and_two_rombos",
        ]
    )
    def test_sub_two_rombos(self):
        square0 = Primitive.regular_polygon(nsides=4, radius=2, center=(-1, 0))
        square1 = Primitive.regular_polygon(nsides=4, radius=2, center=(1, 0))

        left_points = [(0, 1), (-1, 2), (-3, 0), (-1, -2), (0, -1), (-1, 0)]
        left_shape = Primitive.polygon(left_points)
        right_points = [(0, 1), (1, 0), (0, -1), (1, -2), (3, 0), (1, 2)]
        right_shape = Primitive.polygon(right_points)

        assert close_shape(square0 - square1) == left_shape
        assert close_shape(square1 - square0) == right_shape

    @pytest.mark.order(32)
    @pytest.mark.dependency(
        depends=[
            "TestIntersectionSimple::test_begin",
            "TestIntersectionSimple::test_or_two_rombos",
            "TestIntersectionSimple::test_and_two_rombos",
            "TestIntersectionSimple::test_sub_two_rombos",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(32)
@pytest.mark.dependency(
    depends=[
        "TestIntersectionSimple::test_end",
    ]
)
def test_end():
    pass
