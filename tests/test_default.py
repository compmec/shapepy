import math

import numpy as np
import pytest

from shapepy import default


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_constants():
    assert abs(default.tau - math.tau) < 1e-9


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_numbers():
    assert default.real(1) == 1
    assert default.real("1") == 1
    assert default.real("inf") == float("inf")
    assert default.finite(1) == 1
    assert default.integer(1) == 1
    assert default.integer("1") == 1
    assert default.isreal(1)
    assert default.isfinite(1)
    assert default.isinfinity(float("inf"))
    assert default.isrational(1)
    assert default.isinteger(1)
    assert default.fmod(3.0, 2.5) == 0.5
    assert default.hypot(3, 4) == 5
    assert default.rational(4, 2) == 2
    assert default.rational(3, 4) == 0.75
    assert default.rational(3, 4.0) == 0.75
    with pytest.raises(ValueError):
        default.finite("inf")


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_trigonometric():
    values = (i / 128 for i in range(128 + 1))
    for unit in values:
        angle = default.tau * unit
        assert default.radsin(angle) == math.sin(angle)
        assert default.radcos(angle) == math.cos(angle)
        assert default.tursin(unit) == math.sin(angle)
        assert default.turcos(unit) == math.cos(angle)

    assert default.atan2(0, 1) == 0
    assert default.atan2(1, 0) == default.tau / 4
    assert default.atan2(0, -1) == default.tau / 2
    assert default.atan2(-1, 0) == -default.tau / 4

    assert default.degrees(0) == 0
    assert default.degrees(default.tau / 4) == 90
