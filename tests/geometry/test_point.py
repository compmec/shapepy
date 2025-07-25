"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction as frac

import pytest

from shapepy.geometry.point import Point2D


@pytest.mark.order(11)
@pytest.mark.dependency(
    depends=[
        "tests/scalar/test_reals.py::test_all",
        "tests/scalar/test_polynomial.py::test_all",
        "tests/scalar/test_bezier.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(11)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_creation():
    Point2D(0, 0)
    Point2D(1, 1)
    Point2D(0.0, 0.0)
    zero = frac(0)
    Point2D(zero, zero)

    with pytest.raises(TypeError):
        Point2D((0, 0))
    point = (0, 0)
    with pytest.raises(TypeError):
        Point2D(point)
    with pytest.raises(TypeError):
        Point2D([0, 0])


@pytest.mark.order(11)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin", "test_creation"])
def test_error_creation():
    with pytest.raises(ValueError):
        Point2D("1a", 1.0)
    with pytest.raises(ValueError):
        Point2D(1, "asd")
    with pytest.raises(TypeError):
        Point2D(1, None)


@pytest.mark.order(11)
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


@pytest.mark.order(11)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation",
        "test_indexable",
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


@pytest.mark.order(11)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation",
        "test_indexable",
    ]
)
def test_norm():
    point = Point2D(0, 0)
    assert abs(point) == 0
    point = Point2D(1, 0)
    assert abs(point) == 1
    point = Point2D(3, 4)
    assert abs(point) == 5
    point = Point2D(5, 12)
    assert abs(point) == 13

    point = Point2D(frac(3, 5), frac(4, 5))
    assert abs(point) == 1
    point = Point2D(frac(5, 13), frac(12, 13))
    assert abs(point) == 1

    point = Point2D(0.0, 0.0)
    assert abs(point) == 0.0
    point = Point2D(1.0, 0.0)
    assert abs(point) == 1.0
    point = Point2D(3.0, 4.0)
    assert abs(point) == 5
    point = Point2D(5.0, 12.0)
    assert abs(point) == 13


@pytest.mark.order(11)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation",
        "test_norm",
    ]
)
def test_inner():
    pointa = Point2D(0, 0)
    pointb = Point2D(0, 0)
    assert pointa @ pointb == 0
    assert pointb @ pointa == 0

    pointa = Point2D(1, 0)
    pointb = Point2D(0, 1)
    assert pointa @ pointb == 0
    assert pointb @ pointa == 0

    pointa = Point2D(1, 1)
    pointb = Point2D(1, 1)
    assert pointa @ pointb == 2
    assert pointb @ pointa == 2


@pytest.mark.order(11)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin", "test_creation"])
def test_cross():
    pointa = Point2D(0, 0)
    pointb = Point2D(0, 0)
    assert pointa ^ pointb == 0
    assert pointb ^ pointa == 0

    pointa = Point2D(1, 0)
    pointb = Point2D(0, 1)
    assert pointa ^ pointb == 1
    assert pointb ^ pointa == -1

    pointa = Point2D(1, 1)
    pointb = Point2D(1, 1)
    assert pointa ^ pointb == 0
    assert pointb ^ pointa == 0


@pytest.mark.order(11)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation",
        "test_norm",
        "test_inner",
        "test_cross",
    ]
)
def test_equivalent_expression():
    return
    pta = Point2D(frac(5, 13), frac(12, 13))
    ptb = Point2D(frac(3, 5), frac(4, 5))
    assert pta * ptb == pta[0] * ptb[0] + pta[1] * ptb[1]
    assert ptb * pta == pta[0] * ptb[0] + pta[1] * ptb[1]
    assert pta ^ ptb == pta[0] * ptb[1] - pta[1] * ptb[0]
    assert ptb ^ pta == pta[0] * ptb[1] - pta[1] * ptb[0]


@pytest.mark.order(11)
@pytest.mark.dependency(
    depends=[
        "test_creation",
    ]
)
def test_print():
    pointa = Point2D(0, 0)
    pointb = Point2D(1.0, 1.0)
    print(pointa)
    print(repr(pointa))
    print(type(pointa))
    print(pointb)
    print(repr(pointb))
    print(type(pointb))


@pytest.mark.order(11)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation",
        "test_error_creation",
        "test_indexable",
        "test_addsub",
        "test_inner",
        "test_norm",
        "test_cross",
        "test_equivalent_expression",
        "test_print",
    ]
)
def test_all():
    pass
