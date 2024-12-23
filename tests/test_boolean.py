"""
This file tests the shapepy.boolean part, which contains
the `BoolNot`, `BoolOr` and `BoolAnd` objects
"""

import pytest

from shapepy.boolean import BoolAnd, BoolNot, BoolOr
from shapepy.core import Empty, Whole
from shapepy.operations import Simplify
from shapepy.point import Point2D


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "tests/test_empty_whole.py::test_end",
        "tests/test_point.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin"])
def test_flatten():
    pointa = Point2D((0, 0))
    pointb = Point2D((1, 2))
    assert Simplify.flatten(pointa) == pointa
    invpta = BoolNot(pointa)
    assert Simplify.flatten(invpta) == invpta

    union = BoolOr([BoolOr([pointa, pointb]), pointa])
    assert Simplify.flatten(union) == BoolOr([pointa, pointa, pointb])
    inter = BoolAnd([BoolAnd([pointa, pointb]), pointa])
    assert Simplify.flatten(inter) == BoolAnd([pointa, pointa, pointb])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin", "test_flatten"])
def test_expand():
    pointa = Point2D((0, 0))
    assert Simplify.expand(pointa) == pointa

    pointb = Point2D((1, 1))
    invpointa = BoolNot(pointa)
    invpointb = BoolNot(pointb)

    test = BoolNot(BoolOr([pointa, pointb]))
    good = BoolAnd([invpointa, invpointb])
    assert Simplify.expand(test) == good

    union0 = BoolOr([pointa, pointa])
    union1 = BoolOr([pointa, pointa])
    union2 = BoolOr([pointa, pointa])
    inters = BoolAnd([union0, union1, union2])
    inters = Simplify.expand(inters)


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin", "test_expand"])
def test_compare():
    pointa = Point2D((0, 0))
    pointb = Point2D((0, 0))
    invpointa = BoolNot(pointa)
    invpointb = BoolNot(pointb)

    assert ~invpointa is pointa
    assert ~invpointb is pointb
    assert pointa == pointb
    assert invpointa == invpointb


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin", "test_expand", "test_compare"])
def test_general():
    pointa = Point2D((0, 0))
    invpointa = BoolNot(pointa)
    pointb = Point2D((1, 1))
    invpointb = BoolNot(pointb)

    union = BoolOr([pointa, pointb])
    inter = BoolAnd([pointa, pointb])
    assert ~invpointa == pointa
    assert ~union == BoolAnd([invpointa, invpointb])
    assert ~inter == BoolOr([invpointa, invpointb])

    objecta = BoolOr([pointa, pointb])
    objectb = BoolOr([pointa, pointb])
    object = BoolAnd([objecta, objectb])
    Simplify.expand(object)

    object = BoolNot(object)
    Simplify.expand(object)


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin", "test_expand", "test_compare"])
def test_boolean():
    point = Point2D((0, 0))
    assert ~BoolNot(point) == point


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin", "test_expand", "test_compare"])
def test_simplify():
    empty, whole = Empty(), Whole()

    point = Point2D((0, 0))
    assert Simplify.simplify(BoolOr([point, point])) == point
    assert Simplify.simplify(BoolOr([point, BoolNot(point)])) is whole
    assert Simplify.simplify(BoolAnd([point, point])) == point
    assert Simplify.simplify(BoolAnd([point, BoolNot(point)])) is empty


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin"])
def test_print():
    point = Point2D((0, 0))
    invpoint = BoolNot(point)
    str(invpoint)
    repr(invpoint)

    union = BoolOr([point, point])
    str(union)
    repr(union)

    inter = BoolAnd([point, point])
    str(inter)
    repr(inter)


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_expand",
        "test_compare",
        "test_general",
        "test_simplify",
        "test_print",
    ]
)
def test_end():
    pass
