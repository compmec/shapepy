import math

import pytest

from shapepy.scalar.reals import Is, Math, To


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_constants():
    assert abs(Math.tau - math.tau) < 1e-9


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_conversion():
    assert To.real(1) == 1
    assert To.real("1") == 1
    assert To.real("inf") == float("inf")
    assert To.finite(1) == 1
    assert To.integer(1) == 1
    assert To.integer("1") == 1
    assert To.rational(4, 2) == 2
    assert To.rational(3, 4) == 0.75
    with pytest.raises(TypeError):
        To.rational(3, 4.0)
    with pytest.raises(ValueError):
        To.finite("inf")


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_verification():
    assert Is.real(1)
    assert Is.finite(1)
    assert Is.infinity(float("inf"))
    assert Is.rational(1)
    assert Is.integer(1)


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_trigonometric():
    values = (i / 128 for i in range(128 + 1))
    for unit in values:
        angle = Math.tau * unit
        assert Math.radsin(angle) == math.sin(angle)
        assert Math.radcos(angle) == math.cos(angle)
        assert Math.tursin(unit) == math.sin(angle)
        assert Math.turcos(unit) == math.cos(angle)

    assert Math.atan2(0, 1) == 0
    assert Math.atan2(1, 0) == Math.tau / 4
    assert Math.atan2(0, -1) == Math.tau / 2
    assert Math.atan2(-1, 0) == -Math.tau / 4

    assert Math.degrees(0) == 0
    assert Math.degrees(Math.tau / 4) == 90


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_math_functions():
    assert Math.fmod(3.0, 2.5) == 0.5
    assert Math.hypot(3, 4) == 5


@pytest.mark.order(1)
@pytest.mark.skip()
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_constants",
        "test_conversion",
        "test_verification",
        "test_trigonometric",
        "test_math_functions",
    ]
)
def test_all():
    pass
