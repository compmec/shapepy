"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction as frac

import pytest

from shapepy.point import Point2D


@pytest.mark.order(2)
@pytest.mark.dependency()
def test_begin():
    pass


@pytest.mark.order(2)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_creation():
    Point2D(0, 0)
    Point2D(1, 1)
    Point2D(0.0, 0.0)
    zero = frac(0)
    Point2D(zero, zero)

    Point2D((0, 0))
    point = (0, 0)
    Point2D(point)
    point = [0, 0]
    Point2D(point)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin", "test_creation"])
def test_error_creation():
    with pytest.raises(TypeError):
        Point2D("1a", 1.0)
    with pytest.raises(TypeError):
        Point2D(1, "asd")
    with pytest.raises(TypeError):
        Point2D(1, None)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation",
        "test_error_creation",
    ]
)
def test_indexable():
    point = Point2D(0, 0)
    assert point[0] == 0
    assert point[1] == 0

    point = Point2D(1, 2)
    assert point[0] == 1
    assert point[1] == 2


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation",
        "test_error_creation",
    ]
)
def test_compare():
    point = Point2D(0, 0)
    assert point == (0, 0)
    assert point != (1, 0)

    point = Point2D(1, 2)
    assert point == (1, 2)
    assert point != (1, 1)

    pointa = Point2D(1, 2)
    pointb = Point2D(1, 2)
    assert id(pointa) != id(pointb)
    assert pointa == pointb


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation",
        "test_indexable",
        "test_compare",
    ]
)
def test_addsub():
    pointa = Point2D(0, 0)
    pointb = Point2D(1, 1)
    assert pointa + pointb == pointb
    assert pointa - pointb == -pointb
    assert pointb + pointa == pointb
    assert pointb - pointa == pointb

    pointa = Point2D(3, 4)
    pointb = Point2D(12, 5)
    aplusb = Point2D(15, 9)
    aminusb = Point2D(-9, -1)
    assert pointa + pointb == aplusb
    assert pointa - pointb == aminusb
    assert pointb + pointa == aplusb
    assert pointb - pointa == -aminusb

    assert pointa + (12, 5) == aplusb
    assert pointa - (12, 5) == aminusb

    assert pointa != (12, 5)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation",
        "test_indexable",
        "test_compare",
    ]
)
def test_inner():
    pointa = Point2D(0, 0)
    pointb = Point2D(0, 0)
    assert pointa.inner(pointb) == 0
    assert pointb.inner(pointa) == 0

    pointa = Point2D(1, 0)
    pointb = Point2D(0, 1)
    assert pointa.inner(pointb) == 0
    assert pointb.inner(pointa) == 0

    pointa = Point2D(1, 1)
    pointb = Point2D(1, 1)
    assert pointa.inner(pointb) == 2
    assert pointb.inner(pointa) == 2


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation",
        "test_inner",
    ]
)
def test_norm():
    point = Point2D(0, 0)
    assert point.norm2() == 0
    assert abs(point) == 0
    point = Point2D(1, 0)
    assert point.norm2() == 1
    assert abs(point) == 1
    point = Point2D(3, 4)
    assert point.norm2() == 25
    assert abs(point) == 5
    point = Point2D(5, 12)
    assert point.norm2() == 169
    assert abs(point) == 13

    point = Point2D(frac(3, 5), frac(4, 5))
    assert point.norm2() == 1
    assert abs(point) == 1
    point = Point2D(frac(5, 13), frac(12, 13))
    assert point.norm2() == 1
    assert abs(point) == 1

    point = Point2D(0.0, 0.0)
    assert point.norm2() == 0.0
    assert abs(point) == 0.0
    point = Point2D(1.0, 0.0)
    assert point.norm2() == 1.0
    assert abs(point) == 1.0
    point = Point2D(3.0, 4.0)
    assert point.norm2() == 25.0
    assert abs(point) == 5
    point = Point2D(5.0, 12.0)
    assert point.norm2() == 169.0
    assert abs(point) == 13


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin", "test_creation"])
def test_cross():
    pointa = Point2D(0, 0)
    pointb = Point2D(0, 0)
    assert pointa.cross(pointb) == 0
    assert pointb.cross(pointa) == 0

    pointa = Point2D(1, 0)
    pointb = Point2D(0, 1)
    assert pointa.cross(pointb) == 1
    assert pointb.cross(pointa) == -1

    pointa = Point2D(1, 1)
    pointb = Point2D(1, 1)
    assert pointa.cross(pointb) == 0
    assert pointb.cross(pointa) == 0


@pytest.mark.order(2)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation",
    ]
)
def test_print():
    point = Point2D(0, 0)
    str(point)
    repr(point)


@pytest.mark.order(2)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation",
        "test_error_creation",
        "test_indexable",
        "test_compare",
        "test_addsub",
        "test_inner",
        "test_norm",
        "test_cross",
        "test_print",
    ]
)
def test_end():
    pass
