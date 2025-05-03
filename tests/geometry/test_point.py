import pytest

from shapepy import default
from shapepy.angle import Angle
from shapepy.geometry import (
    GeometricPoint,
    move_point,
    rotate_point,
    scale_point,
)


@pytest.mark.order(31)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/test_default.py::test_all",
    ],
    scope="session",
)
def test_build_cartesian():
    coords = (default.NEGINF, -1, 0, 1, default.POSINF)
    for xval in coords:
        for yval in coords:
            GeometricPoint.cartesian(xval, yval)


@pytest.mark.order(31)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/test_default.py::test_all",
        "tests/test_angle.py::test_all",
    ],
    scope="session",
)
def test_build_polar():
    angles = tuple(map(Angle.degrees, range(0, 360, 15)))
    radius = (0, 1, 10, default.POSINF)
    for rad in radius:
        for angle in angles:
            GeometricPoint.polar(rad, angle)

    with pytest.raises(ValueError):
        GeometricPoint.polar(-1, Angle())

    with pytest.raises(ValueError):
        GeometricPoint.polar(default.NEGINF, Angle())


@pytest.mark.order(31)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build_cartesian", "test_build_polar"])
def test_compare():
    pointa = GeometricPoint.cartesian(0, 1)
    pointb = GeometricPoint.polar(1, Angle.degrees(90))

    assert pointa == pointb
    assert pointa == (0, 1)

    assert pointa != 1


@pytest.mark.order(31)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build_cartesian", "test_build_polar"])
def test_extract_cartesians():
    coords = (default.NEGINF, -1, 0, 1, default.POSINF)
    for xval in coords:
        for yval in coords:
            point = GeometricPoint.cartesian(xval, yval)
            assert point.x == xval
            assert point.y == yval

    point = GeometricPoint.cartesian(default.POSINF, 0)
    assert point.x == default.POSINF
    assert point.y == 0
    assert point.radius == default.POSINF
    assert point.angle == Angle.degrees(0)

    point = GeometricPoint.cartesian(0, default.POSINF)
    assert point.x == 0
    assert point.y == default.POSINF
    assert point.radius == default.POSINF
    assert point.angle == Angle.degrees(90)

    point = GeometricPoint.cartesian(default.NEGINF, 0)
    assert point.x == default.NEGINF
    assert point.y == 0
    assert point.radius == default.POSINF
    assert point.angle == Angle.degrees(180)

    point = GeometricPoint.cartesian(0, default.NEGINF)
    assert point.x == 0
    assert point.y == default.NEGINF
    assert point.radius == default.POSINF
    assert point.angle == Angle.degrees(270)

    point = GeometricPoint.cartesian(0, 0)
    assert point.x == 0
    assert point.y == 0
    assert point.radius == 0
    assert point.angle == 0

    point = GeometricPoint.cartesian(3, 4)
    assert point.x == 3
    assert point.y == 4
    assert point.radius == 5
    assert point.angle == Angle.atan2(4, 3)


@pytest.mark.order(31)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build_cartesian", "test_build_polar"])
def test_extract_polar():
    angles = tuple(map(Angle.degrees, range(0, 360, 15)))
    radius = (0, 1, 10, default.POSINF)
    for rad in radius:
        for angle in angles:
            point = GeometricPoint.polar(rad, angle)
            assert point.radius == rad
            assert point.angle == angle

    for angle in angles:
        point = GeometricPoint.polar(default.POSINF, angle)
        assert point.radius == default.POSINF
        assert point.angle == angle
        if angle.cos() == 0:
            assert point.x == 0
        elif angle.cos() > 0:
            assert point.x == default.POSINF
        elif angle.cos() < 0:
            assert point.x == default.NEGINF
        if angle.sin() == 0:
            assert point.y == 0
        elif angle.sin() > 0:
            assert point.y == default.POSINF
        elif angle.sin() < 0:
            assert point.y == default.NEGINF


@pytest.mark.order(31)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build_cartesian", "test_build_polar"])
def test_move_point():
    assert move_point((0, 0), (1, 0)) == (1, 0)


@pytest.mark.order(31)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build_cartesian", "test_build_polar"])
def test_scale_point():
    assert scale_point((3, 4), 1) == (3, 4)
    assert scale_point((3, 4), 3) == (9, 12)
    assert scale_point((3, 4), (3, 4)) == (9, 16)


@pytest.mark.order(31)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build_cartesian", "test_build_polar"])
def test_rotate_point():
    angle = Angle.degrees(90)
    assert rotate_point((1, 0), angle) == (0, 1)
    assert rotate_point((0, 1), angle) == (-1, 0)


@pytest.mark.order(31)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build_cartesian", "test_build_polar"])
def test_print():
    point = GeometricPoint.cartesian(0, 0)
    str(point)
    repr(point)

    point = GeometricPoint.polar(1, Angle.degrees(45))
    str(point)
    repr(point)


@pytest.mark.order(31)
@pytest.mark.dependency(
    depends=[
        "test_build_cartesian",
        "test_build_polar",
        "test_extract_cartesians",
        "test_extract_polar",
        "test_move_point",
        "test_scale_point",
        "test_rotate_point",
        "test_print",
    ]
)
def test_all():
    pass
