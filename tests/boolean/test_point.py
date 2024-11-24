"""
Tests related to verify the boolean operations between shapes that do
not intersect teach other.
"""

import pytest

from shapepy.core import Empty, Whole
from shapepy.point import Point2D
from shapepy.primitive import Primitive
from shapepy.shape import ConnectedShape, DisjointShape


@pytest.mark.order(32)
@pytest.mark.dependency(
    depends=[
        "tests/test_empty_whole.py::test_end",
        "tests/test_point.py::test_end",
        "tests/boolean/test_empty_whole.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(32)
@pytest.mark.timeout(40)
@pytest.mark.dependency(depends=["test_begin"])
def test_not():
    point = Point2D((0, 0))
    assert ~point != point
    assert ~(~point) == point


@pytest.mark.order(32)
@pytest.mark.timeout(40)
@pytest.mark.dependency(depends=["test_begin"])
def test_or():
    pointa = Point2D((0, 0))
    pointb = Point2D((1, 1))
    assert pointa | pointa == pointa
    assert pointb | pointb == pointb
    assert pointa | pointb == pointb | pointa


@pytest.mark.order(32)
@pytest.mark.timeout(40)
@pytest.mark.dependency(depends=["test_begin"])
def test_and():
    pointa = Point2D((0, 0))
    pointb = Point2D((1, 1))
    assert pointa & pointa == pointa
    assert pointb & pointb == pointb
    assert pointa & pointb is Empty()
    assert pointb & pointa is Empty()


@pytest.mark.order(32)
@pytest.mark.timeout(40)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_or",
        "test_or",
        "test_and",
    ]
)
def test_sub():
    pointa = Point2D((0, 0))
    pointb = Point2D((1, 1))
    assert pointa & pointa == pointa
    assert pointb & pointb == pointb
    assert pointa & pointb is Empty()
    assert pointb & pointa is Empty()


@pytest.mark.order(32)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_or",
        "test_and",
    ]
)
def test_xor():
    pointa = Point2D((0, 0))
    pointb = Point2D((1, 1))
    assert pointa ^ pointa is Empty()
    assert pointb ^ pointb is Empty()
    assert pointa ^ pointb == pointa | pointb
    assert pointb ^ pointa == pointa | pointb


@pytest.mark.order(32)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_not",
        "test_or",
        "test_and",
        "test_sub",
    ]
)
def test_end():
    pass
