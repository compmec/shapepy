import pytest

from shapepy import default
from shapepy.angle import Angle
from shapepy.geometry import GeometricPoint


@pytest.mark.order(14)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_build_cartesian():
    coords = (default.NEGINF, -1, 0, 1, default.POSINF)
    for xval in coords:
        for yval in coords:
            GeometricPoint.cartesian(xval, yval)


@pytest.mark.order(14)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
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


@pytest.mark.order(14)
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


@pytest.mark.order(14)
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


@pytest.mark.order(14)
@pytest.mark.dependency(
    depends=[
        "test_build_cartesian",
        "test_build_polar",
        "test_extract_cartesians",
        "test_extract_polar",
    ]
)
def test_all():
    pass
