import math
import random

import pytest

from shapepy.scalar.angle import arg, degrees, radians, to_angle, turns
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
    radians(-math.pi / 6)
    radians(-math.pi / 4)
    radians(0)
    radians(math.pi / 6)
    radians(math.pi / 4)
    radians(math.pi / 3)
    radians(2 * math.pi / 6)
    radians(math.pi / 2)
    radians(math.pi)
    radians(3 * math.pi / 2)
    radians(2 * math.pi)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/scalar/test_reals.py::test_all",
    ],
    scope="session",
)
def test_build_degrees():
    degrees(0)
    degrees(90)
    degrees(180)
    degrees(270)
    degrees(360)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/scalar/test_reals.py::test_all",
    ],
    scope="session",
)
def test_build_turns():
    turns(0)
    turns(0.125)
    turns(0.250)
    turns(0.375)
    turns(0.500)
    turns(0.625)
    turns(0.750)
    turns(0.875)
    turns(1.000)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["test_build_radians", "test_build_degrees", "test_build_turns"]
)
def test_build_arg():
    coords = (-2, -1, 0, 1, 2)
    for xval in coords:
        for yval in coords:
            arg(xval, yval)

    for xval in coords:
        arg(xval, Math.NEGINF)
        arg(xval, Math.POSINF)

    for yval in coords:
        arg(Math.NEGINF, yval)
        arg(Math.POSINF, yval)

    arg(Math.NEGINF, Math.NEGINF)
    arg(Math.NEGINF, Math.POSINF)
    arg(Math.POSINF, Math.NEGINF)
    arg(Math.POSINF, Math.POSINF)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["test_build_radians", "test_build_degrees", "test_build_turns"]
)
def test_directions():
    for degval in range(-134, -45):
        assert degrees(degval).direction % 4 == 3
    for degval in range(-44, 45):
        assert degrees(degval).direction % 4 == 0
    for degval in range(46, 134):
        assert degrees(degval).direction % 4 == 1
    for degval in range(136, 225):
        assert degrees(degval).direction % 4 == 2
    for degval in range(226, 315):
        assert degrees(degval).direction % 4 == 3


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_directions"])
def test_compare():
    assert radians(0) == degrees(0)
    assert radians(math.pi / 6) == degrees(30)
    assert radians(math.pi / 4) == degrees(45)
    assert radians(math.pi / 3) == degrees(60)
    assert radians(math.pi / 2) == degrees(90)
    assert radians(math.pi) == degrees(180)
    assert radians(3 * math.pi / 2) == degrees(270)
    assert radians(2 * math.pi) == degrees(0)

    for deg in range(0, 360, 15):
        assert degrees(deg) == turns(To.rational(deg, 360))

    assert degrees(0) == radians(0)
    assert degrees(180) == radians(math.pi)
    assert degrees(90) == radians(math.pi / 2)
    assert degrees(270) == radians(-math.pi / 2)
    assert float(degrees(0)) == 0
    assert float(degrees(180)) == math.pi
    assert float(degrees(90)) == math.pi / 2
    assert float(degrees(270)) == 3 * math.pi / 2


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_directions", "test_compare"])
def test_evaluate_arg():
    assert arg(0, 0) == degrees(0)
    assert arg(1, 0) == degrees(0)
    assert arg(2, 0) == degrees(0)
    assert arg(1, 1) == degrees(45)
    assert arg(0, 1) == degrees(90)
    assert arg(-1, 1) == degrees(135)
    assert arg(-1, 0) == degrees(180)
    assert arg(-1, -1) == degrees(225)
    assert arg(0, -1) == degrees(270)
    assert arg(1, -1) == degrees(315)
    assert arg(1, 0) == degrees(360)

    NEGINF = Math.NEGINF
    POSINF = Math.POSINF
    assert arg(POSINF, 0) == degrees(0)
    assert arg(POSINF, POSINF) == degrees(45)
    assert arg(0, POSINF) == degrees(90)
    assert arg(NEGINF, POSINF) == degrees(135)
    assert arg(NEGINF, 0) == degrees(180)
    assert arg(NEGINF, NEGINF) == degrees(225)
    assert arg(0, NEGINF) == degrees(270)
    assert arg(POSINF, NEGINF) == degrees(315)
    assert arg(POSINF, 0) == degrees(360)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_directions"])
def test_evaluate_sincos():
    degs = (0, 90, 180, 270, 360)
    coss = (1, 0, -1, 0, 1)
    sins = (0, 1, 0, -1, 0)

    for deg, cos, sin in zip(degs, coss, sins):
        angle = degrees(deg)
        assert angle.cos() == cos
        assert angle.sin() == sin

    a = math.sqrt(2) / 2
    degs = (45, 135, 225, 315)
    coss = (a, -a, -a, a)
    sins = (a, a, -a, -a)

    for deg, cos, sin in zip(degs, coss, sins):
        angle = degrees(deg)
        assert abs(angle.cos() - cos) < 1e-15
        assert abs(angle.sin() - sin) < 1e-15


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_directions", "test_compare"])
def test_evaluate_operations():
    random.seed(0)

    for _ in range(1000):
        a = random.randint(0, 720)
        b = random.randint(0, 720)
        anglea = degrees(a)
        angleb = degrees(b)

        anglec = degrees(a + b)
        angled = anglea + angleb
        assert angled == anglec

        anglec = degrees(a - b)
        angled = anglea - angleb
        assert angled == anglec

        assert 2 * anglea == anglea + anglea


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_directions", "test_compare"])
def test_convert():
    assert to_angle("90deg") == degrees(90)
    assert to_angle("0.25tur") == turns(0.25)
    assert to_angle("1.25rad") == radians(1.25)

    assert to_angle(1.25) == radians(1.25)

    anglea = degrees(30)
    assert to_angle(anglea) is anglea


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_directions", "test_compare"])
def test_print():
    assert str(degrees(0)) == "0 deg"
    assert str(degrees(90)) == "90 deg"
    assert str(degrees(180)) == "180 deg"
    assert str(degrees(270)) == "270 deg"

    assert repr(degrees(0)) == "Angle(0, 0)"
    assert repr(degrees(90)) == "Angle(1, 0)"
    assert repr(degrees(180)) == "Angle(2, 0)"
    assert repr(degrees(270)) == "Angle(3, 0)"


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_build_radians",
        "test_build_degrees",
        "test_build_turns",
        "test_build_arg",
        "test_directions",
        "test_compare",
        "test_evaluate_arg",
        "test_evaluate_sincos",
        "test_evaluate_operations",
        "test_convert",
        "test_print",
    ]
)
def test_all():
    pass
