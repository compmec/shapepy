"""
This file tests the shapepy.boolean part, which contains
the `Inverse`, `Union` and `Intersection` objects
"""

import pytest

from shapepy.boolean import (
    Intersection,
    Inverse,
    Union,
    expand,
    flatten,
    simplify,
)
from shapepy.core import Empty, Whole
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
    assert flatten(pointa) == pointa
    invpta = Inverse(pointa)
    assert flatten(invpta) == invpta

    union = Union([Union([pointa, pointb]), pointa])
    assert flatten(union) == Union([pointa, pointa, pointb])
    inter = Intersection([Intersection([pointa, pointb]), pointa])
    assert flatten(inter) == Intersection([pointa, pointa, pointb])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin", "test_flatten"])
def test_expand():
    pointa = Point2D((0, 0))
    assert expand(pointa) == pointa

    pointb = Point2D((0, 0))
    invpointa = Inverse(pointa)
    invpointb = Inverse(pointb)

    test = Inverse(Union([pointa, pointb]))
    good = Intersection([invpointa, invpointb])
    assert test == good

    union0 = Union([pointa, pointa])
    union1 = Union([pointa, pointa])
    union2 = Union([pointa, pointa])
    inters = Intersection([union0, union1, union2])
    inters = expand(inters)


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin", "test_expand"])
def test_compare():
    pointa = Point2D((0, 0))
    pointb = Point2D((0, 0))
    invpointa = Inverse(pointa)
    invpointb = Inverse(pointb)

    assert ~invpointa is pointa
    assert ~invpointb is pointb
    assert pointa == pointb
    assert invpointa == invpointb


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin", "test_expand", "test_compare"])
def test_general():
    pointa = Point2D((0, 0))
    invpointa = Inverse(pointa)
    pointb = Point2D((0, 0))
    invpointb = Inverse(pointb)

    union = Union([pointa, pointb])
    inter = Intersection([pointa, pointb])
    assert ~invpointa == pointa
    assert ~union == Intersection([invpointa, invpointb])
    assert ~inter == Union([invpointa, invpointb])

    objecta = Union([pointa, pointb])
    objectb = Union([pointa, pointb])
    object = Intersection([objecta, objectb])
    temp = expand(object)

    object = Inverse(object)
    temp = expand(object)


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin", "test_expand", "test_compare"])
def test_boolean():
    point = Point2D((0, 0))
    assert ~Inverse(point) == point


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin", "test_expand", "test_compare"])
def test_simplify():
    empty, whole = Empty(), Whole()

    point = Point2D((0, 0))
    assert simplify(Union([point, point])) == point
    assert simplify(Union([point, Inverse(point)])) is whole
    assert simplify(Intersection([point, point])) == point
    assert simplify(Intersection([point, Inverse(point)])) is empty


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin"])
def test_print():
    point = Point2D((0, 0))
    invpoint = Inverse(point)
    str(invpoint)
    repr(invpoint)

    union = Union([point, point])
    str(union)
    repr(union)

    inter = Intersection([point, point])
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
