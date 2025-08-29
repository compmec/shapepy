"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction as frac

import pytest

from shapepy.geometry.point import cartesian, cross, inner, polar
from shapepy.scalar.angle import Angle


@pytest.mark.order(11)
@pytest.mark.dependency(
    depends=[
        "tests/scalar/test_reals.py::test_all",
        "tests/analytic/test_polynomial.py::test_all",
        "tests/analytic/test_bezier.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(11)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_creation_finite_cartesian():
    point = cartesian(0, 0)
    assert point.xcoord == 0
    assert point.ycoord == 0
    point = cartesian(1, 1)
    assert point.xcoord == 1
    assert point.ycoord == 1
    cartesian(0.0, 0.0)
    zero = frac(0)
    cartesian(zero, zero)

    with pytest.raises(TypeError):
        cartesian((0, 0))
    point = (0, 0)
    with pytest.raises(TypeError):
        cartesian(point)
    with pytest.raises(TypeError):
        cartesian([0, 0])

    point = cartesian(3, 4)
    assert point.xcoord == 3
    assert point.ycoord == 4
    assert point.radius == 5


@pytest.mark.order(11)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_creation_finite_polar():
    radius = 0
    for degrees in range(0, 360, 45):
        angle = Angle.degrees(degrees)
        point = polar(radius, angle)
        assert point.xcoord == 0
        assert point.ycoord == 0
        assert point.radius == 0
        assert point.angle == 0

    radius = 10
    for degrees in range(0, 360, 45):
        angle = Angle.degrees(degrees)
        point = polar(radius, angle)
        assert point.xcoord == radius * angle.cos()
        assert point.ycoord == radius * angle.sin()
        assert point.radius == radius
        assert point.angle == angle


@pytest.mark.order(11)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_creation_infinite_cartesian():
    neginf = float("-inf")
    posinf = float("+inf")

    point = cartesian(posinf, 0)
    assert point.xcoord == posinf
    assert point.ycoord == 0
    assert point.radius == posinf
    assert point.angle == Angle.degrees(0)

    point = cartesian(posinf, posinf)
    assert point.xcoord == posinf
    assert point.ycoord == posinf
    assert point.radius == posinf
    assert point.angle == Angle.degrees(45)

    point = cartesian(0, posinf)
    assert point.xcoord == 0
    assert point.ycoord == posinf
    assert point.radius == posinf
    assert point.angle == Angle.degrees(90)

    point = cartesian(neginf, posinf)
    assert point.xcoord == neginf
    assert point.ycoord == posinf
    assert point.radius == posinf
    assert point.angle == Angle.degrees(135)

    point = cartesian(neginf, 0)
    assert point.xcoord == neginf
    assert point.ycoord == 0
    assert point.radius == posinf
    assert point.angle == Angle.degrees(180)

    point = cartesian(neginf, neginf)
    assert point.xcoord == neginf
    assert point.ycoord == neginf
    assert point.radius == posinf
    assert point.angle == Angle.degrees(-135)

    point = cartesian(0, neginf)
    assert point.xcoord == 0
    assert point.ycoord == neginf
    assert point.radius == posinf
    assert point.angle == Angle.degrees(-90)

    point = cartesian(posinf, neginf)
    assert point.xcoord == posinf
    assert point.ycoord == neginf
    assert point.radius == posinf
    assert point.angle == Angle.degrees(-45)


@pytest.mark.order(11)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_creation_infinite_polar():
    neginf = float("-inf")
    posinf = float("+inf")
    radius = posinf

    point = polar(radius, Angle.degrees(0))
    assert point.xcoord == posinf
    assert point.ycoord == 0
    assert point.radius == posinf
    assert point.angle == Angle.degrees(0)

    point = polar(radius, Angle.degrees(90))
    assert point.xcoord == 0
    assert point.ycoord == posinf
    assert point.radius == posinf
    assert point.angle == Angle.degrees(90)

    point = polar(radius, Angle.degrees(180))
    assert point.xcoord == neginf
    assert point.ycoord == 0
    assert point.radius == posinf
    assert point.angle == Angle.degrees(180)

    point = polar(radius, Angle.degrees(270))
    assert point.xcoord == 0
    assert point.ycoord == neginf
    assert point.radius == posinf
    assert point.angle == Angle.degrees(270)

    for degrees in range(1, 90):
        angle = Angle.degrees(degrees)
        point = polar(radius, angle)
        assert point.xcoord == posinf
        assert point.ycoord == posinf
        assert point.radius == posinf
        assert point.angle == angle

    for degrees in range(91, 180):
        angle = Angle.degrees(degrees)
        point = polar(radius, angle)
        assert point.xcoord == neginf
        assert point.ycoord == posinf
        assert point.radius == posinf
        assert point.angle == angle

    for degrees in range(181, 270):
        angle = Angle.degrees(degrees)
        point = polar(radius, angle)
        assert point.xcoord == neginf
        assert point.ycoord == neginf
        assert point.radius == posinf
        assert point.angle == angle

    for degrees in range(271, 360):
        angle = Angle.degrees(degrees)
        point = polar(radius, angle)
        assert point.xcoord == posinf
        assert point.ycoord == neginf
        assert point.radius == posinf
        assert point.angle == angle


@pytest.mark.order(11)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["test_begin", "test_creation_finite_cartesian"]
)
def test_error_creation():
    with pytest.raises(ValueError):
        cartesian("1a", 1.0)
    with pytest.raises(ValueError):
        cartesian(1, "asd")
    with pytest.raises(TypeError):
        cartesian(1, None)


@pytest.mark.order(11)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation_finite_cartesian",
        "test_error_creation",
    ]
)
def test_indexable():
    point = cartesian(0, 0)
    assert point[0] == 0
    assert point[1] == 0

    point = cartesian(1, 2)
    assert point[0] == 1
    assert point[1] == 2


@pytest.mark.order(11)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation_finite_cartesian",
        "test_indexable",
    ]
)
def test_addsub():
    pointa = cartesian(0, 0)
    pointb = cartesian(1, 1)
    assert pointa + pointb == pointb
    assert pointa - pointb == -pointb
    assert pointb + pointa == pointb
    assert pointb - pointa == pointb

    pointa = cartesian(3, 4)
    pointb = cartesian(12, 5)
    aplusb = cartesian(15, 9)
    aminusb = cartesian(-9, -1)
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
        "test_creation_finite_cartesian",
        "test_indexable",
        "test_addsub",
    ]
)
def test_transformations():
    pointa = cartesian(0, 0)
    pointb = pointa.move((1, 3))
    assert id(pointb) == id(pointa)
    assert pointa == (1, 3)

    pointb = pointa.scale(2)
    assert id(pointb) == id(pointa)
    assert pointa == (2, 6)
    pointb = pointa.scale((5, 3))
    assert id(pointb) == id(pointa)
    assert pointa == (10, 18)

    angle = Angle.degrees(90)
    pointb = pointa.rotate(angle)
    assert id(pointb) == id(pointa)
    assert pointa == (-18, 10)


@pytest.mark.order(11)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation_finite_cartesian",
        "test_indexable",
    ]
)
def test_norm():
    point = cartesian(0, 0)
    assert abs(point) == 0
    point = cartesian(1, 0)
    assert abs(point) == 1
    point = cartesian(3, 4)
    assert abs(point) == 5
    point = cartesian(5, 12)
    assert abs(point) == 13

    point = cartesian(frac(3, 5), frac(4, 5))
    assert abs(point) == 1
    point = cartesian(frac(5, 13), frac(12, 13))
    assert abs(point) == 1

    point = cartesian(0.0, 0.0)
    assert abs(point) == 0.0
    point = cartesian(1.0, 0.0)
    assert abs(point) == 1.0
    point = cartesian(3.0, 4.0)
    assert abs(point) == 5
    point = cartesian(5.0, 12.0)
    assert abs(point) == 13


@pytest.mark.order(11)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation_finite_cartesian",
        "test_norm",
    ]
)
def test_inner():
    pointa = cartesian(0, 0)
    pointb = cartesian(0, 0)
    assert inner(pointa, pointb) == 0
    assert inner(pointb, pointa) == 0

    pointa = cartesian(1, 0)
    pointb = cartesian(0, 1)
    assert inner(pointa, pointb) == 0
    assert inner(pointb, pointa) == 0

    pointa = cartesian(1, 1)
    pointb = cartesian(1, 1)
    assert inner(pointa, pointb) == 2
    assert inner(pointb, pointa) == 2


@pytest.mark.order(11)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["test_begin", "test_creation_finite_cartesian"]
)
def test_cross():
    pointa = cartesian(0, 0)
    pointb = cartesian(0, 0)
    assert cross(pointa, pointb) == 0
    assert cross(pointb, pointa) == 0

    pointa = cartesian(1, 0)
    pointb = cartesian(0, 1)
    assert cross(pointa, pointb) == 1
    assert cross(pointb, pointa) == -1

    pointa = cartesian(1, 1)
    pointb = cartesian(1, 1)
    assert cross(pointa, pointb) == 0
    assert cross(pointb, pointa) == 0


@pytest.mark.order(11)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation_finite_cartesian",
        "test_norm",
        "test_inner",
        "test_cross",
    ]
)
def test_equivalent_expression():
    pta = cartesian(frac(5, 13), frac(12, 13))
    ptb = cartesian(frac(3, 5), frac(4, 5))
    assert inner(pta, ptb) == pta[0] * ptb[0] + pta[1] * ptb[1]
    assert inner(ptb, pta) == pta[0] * ptb[0] + pta[1] * ptb[1]
    assert cross(pta, ptb) == pta[0] * ptb[1] - pta[1] * ptb[0]
    assert cross(ptb, pta) == pta[1] * ptb[0] - pta[0] * ptb[1]


@pytest.mark.order(11)
@pytest.mark.dependency(
    depends=[
        "test_creation_finite_cartesian",
    ]
)
def test_print():
    pointa = cartesian(0, 0)
    pointb = cartesian(1.0, 1.0)
    assert str(pointa) == "(0, 0)"
    assert str(pointb) == "(1.0, 1.0)"

    pointc = polar(float("inf"), Angle.degrees(15))
    assert str(pointc) == "(inf:15 deg)"

    repr(pointa)
    repr(pointb)
    repr(pointc)


@pytest.mark.order(11)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_creation_finite_cartesian",
        "test_creation_finite_polar",
        "test_creation_infinite_cartesian",
        "test_creation_infinite_polar",
        "test_error_creation",
        "test_indexable",
        "test_addsub",
        "test_transformations",
        "test_inner",
        "test_norm",
        "test_cross",
        "test_equivalent_expression",
        "test_print",
    ]
)
def test_all():
    pass
