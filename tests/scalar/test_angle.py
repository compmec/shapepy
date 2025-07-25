import math
import random

import pytest

from shapepy.scalar.angle import Angle, to_angle
from shapepy.scalar.reals import Math, To


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/scalar/test_reals.py::test_all",
    ],
    scope="session",
)
def test_build_radians():
    Angle.radians(0)
    Angle.radians(math.pi)
    Angle.radians(2 * math.pi)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/scalar/test_reals.py::test_all",
    ],
    scope="session",
)
def test_build_degrees():
    Angle.radians(0)
    Angle.radians(90)
    Angle.radians(180)
    Angle.radians(270)
    Angle.radians(360)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/scalar/test_reals.py::test_all",
    ],
    scope="session",
)
def test_build_turns():
    Angle.turns(0)
    Angle.turns(0.125)
    Angle.turns(0.250)
    Angle.turns(0.375)
    Angle.turns(0.500)
    Angle.turns(0.625)
    Angle.turns(0.750)
    Angle.turns(0.875)
    Angle.turns(1.000)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["test_build_radians", "test_build_degrees", "test_build_turns"]
)
def test_build_atan2():
    coords = (-2, -1, 0, 1, 2)
    for xval in coords:
        for yval in coords:
            Angle.atan2(yval, xval)

    for xval in coords:
        Angle.atan2(xval, Math.NEGINF)
        Angle.atan2(xval, Math.POSINF)

    for yval in coords:
        Angle.atan2(Math.NEGINF, yval)
        Angle.atan2(Math.POSINF, yval)

    Angle.atan2(Math.NEGINF, Math.NEGINF)
    Angle.atan2(Math.NEGINF, Math.POSINF)
    Angle.atan2(Math.POSINF, Math.NEGINF)
    Angle.atan2(Math.POSINF, Math.POSINF)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["test_build_radians", "test_build_degrees", "test_build_turns"]
)
def test_build_arg():
    coords = (-2, -1, 0, 1, 2)
    for xval in coords:
        for yval in coords:
            Angle.arg(xval, yval)

    for xval in coords:
        Angle.arg(xval, Math.NEGINF)
        Angle.arg(xval, Math.POSINF)

    for yval in coords:
        Angle.arg(Math.NEGINF, yval)
        Angle.arg(Math.POSINF, yval)

    Angle.arg(Math.NEGINF, Math.NEGINF)
    Angle.arg(Math.NEGINF, Math.POSINF)
    Angle.arg(Math.POSINF, Math.NEGINF)
    Angle.arg(Math.POSINF, Math.POSINF)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["test_build_radians", "test_build_degrees", "test_build_turns"]
)
def test_compare():
    assert Angle.radians(0) == Angle.degrees(0)
    assert Angle.radians(math.pi / 6) == Angle.degrees(30)
    assert Angle.radians(math.pi / 4) == Angle.degrees(45)
    assert Angle.radians(math.pi / 3) == Angle.degrees(60)
    assert Angle.radians(math.pi / 2) == Angle.degrees(90)
    assert Angle.radians(math.pi) == Angle.degrees(180)
    assert Angle.radians(3 * math.pi / 2) == Angle.degrees(270)
    assert Angle.radians(2 * math.pi) == Angle.degrees(0)

    for deg in range(0, 360, 15):
        assert Angle.degrees(deg) == Angle.turns(To.rational(deg, 360))

    assert Angle.degrees(0) == 0
    assert Angle.degrees(180) == math.pi
    assert Angle.degrees(90) == math.pi / 2
    assert Angle.degrees(270) == -math.pi / 2
    assert float(Angle.degrees(0)) == 0
    assert float(Angle.degrees(180)) == math.pi
    assert float(Angle.degrees(90)) == math.pi / 2
    assert float(Angle.degrees(270)) == 3 * math.pi / 2
    str(Angle())
    repr(Angle())


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["test_build_radians", "test_build_degrees", "test_build_turns"]
)
def test_evaluate_arg():
    assert Angle.arg(0, 0) == Angle.degrees(0)
    assert Angle.arg(1, 0) == Angle.degrees(0)
    assert Angle.arg(2, 0) == Angle.degrees(0)
    assert Angle.arg(1, 1) == Angle.degrees(45)
    assert Angle.arg(0, 1) == Angle.degrees(90)
    assert Angle.arg(-1, 1) == Angle.degrees(135)
    assert Angle.arg(-1, 0) == Angle.degrees(180)
    assert Angle.arg(-1, -1) == Angle.degrees(225)
    assert Angle.arg(0, -1) == Angle.degrees(270)
    assert Angle.arg(1, -1) == Angle.degrees(315)
    assert Angle.arg(1, 0) == Angle.degrees(360)

    NEGINF = Math.NEGINF
    POSINF = Math.POSINF
    assert Angle.arg(POSINF, 0) == Angle.degrees(0)
    assert Angle.arg(POSINF, POSINF) == Angle.degrees(45)
    assert Angle.arg(0, POSINF) == Angle.degrees(90)
    assert Angle.arg(NEGINF, POSINF) == Angle.degrees(135)
    assert Angle.arg(NEGINF, 0) == Angle.degrees(180)
    assert Angle.arg(NEGINF, NEGINF) == Angle.degrees(225)
    assert Angle.arg(0, NEGINF) == Angle.degrees(270)
    assert Angle.arg(POSINF, NEGINF) == Angle.degrees(315)
    assert Angle.arg(POSINF, 0) == Angle.degrees(360)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["test_build_radians", "test_build_degrees", "test_build_turns"]
)
def test_evaluate_atan2():
    assert Angle.atan2(0, 0) == Angle.degrees(0)
    assert Angle.atan2(0, 1) == Angle.degrees(0)
    assert Angle.atan2(0, 2) == Angle.degrees(0)
    assert Angle.atan2(1, 1) == Angle.degrees(45)
    assert Angle.atan2(1, 0) == Angle.degrees(90)
    assert Angle.atan2(1, -1) == Angle.degrees(135)
    assert Angle.atan2(0, -1) == Angle.degrees(180)
    assert Angle.atan2(-1, -1) == Angle.degrees(225)
    assert Angle.atan2(-1, 0) == Angle.degrees(270)
    assert Angle.atan2(-1, 1) == Angle.degrees(315)
    assert Angle.atan2(0, 1) == Angle.degrees(360)

    NEGINF = Math.NEGINF
    POSINF = Math.POSINF
    assert Angle.atan2(0, POSINF) == Angle.degrees(0)
    assert Angle.atan2(POSINF, POSINF) == Angle.degrees(45)
    assert Angle.atan2(POSINF, 0) == Angle.degrees(90)
    assert Angle.atan2(POSINF, NEGINF) == Angle.degrees(135)
    assert Angle.atan2(0, NEGINF) == Angle.degrees(180)
    assert Angle.atan2(NEGINF, NEGINF) == Angle.degrees(225)
    assert Angle.atan2(NEGINF, 0) == Angle.degrees(270)
    assert Angle.atan2(NEGINF, POSINF) == Angle.degrees(315)
    assert Angle.atan2(0, POSINF) == Angle.degrees(360)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["test_build_radians", "test_build_degrees", "test_build_turns"]
)
def test_evaluate_sincos():
    degs = (0, 90, 180, 270, 360)
    coss = (1, 0, -1, 0, 1)
    sins = (0, 1, 0, -1, 0)

    for deg, cos, sin in zip(degs, coss, sins):
        angle = Angle.degrees(deg)
        assert angle.cos() == cos
        assert angle.sin() == sin

    a = math.sqrt(2) / 2
    degs = (45, 135, 225, 315)
    coss = (a, -a, -a, a)
    sins = (a, a, -a, -a)

    for deg, cos, sin in zip(degs, coss, sins):
        angle = Angle.degrees(deg)
        assert abs(angle.cos() - cos) < 1e-15
        assert abs(angle.sin() - sin) < 1e-15


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["test_build_radians", "test_build_degrees", "test_build_turns"]
)
def test_evaluate_operations():

    for _ in range(1000):
        a = random.randint(0, 720)
        b = random.randint(0, 720)
        anglea = Angle.degrees(a)
        angleb = Angle.degrees(b)

        anglec = Angle.degrees(a + b)
        angled = anglea + angleb
        assert angled == anglec

        anglec = Angle.degrees(a - b)
        angled = anglea - angleb
        assert angled == anglec

        assert 2 * anglea == anglea + anglea


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["test_build_radians", "test_build_degrees", "test_build_turns"]
)
def test_convert():

    assert to_angle("90deg") == Angle.degrees(90)
    assert to_angle("0.25tur") == Angle.turns(0.25)
    assert to_angle("1.25rad") == Angle.radians(1.25)

    assert to_angle(1.25) == Angle.radians(1.25)

    anglea = Angle.degrees(30)
    assert to_angle(anglea) is anglea


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_build_radians",
        "test_build_degrees",
        "test_build_turns",
        "test_build_atan2",
        "test_build_arg",
        "test_compare",
        "test_evaluate_arg",
        "test_evaluate_atan2",
        "test_evaluate_sincos",
        "test_evaluate_operations",
        "test_convert",
    ]
)
def test_all():
    pass
