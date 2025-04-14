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
def test_trigonometric():
    values = np.linspace(0, 1, 129)
    for unit in values:
        angle = default.tau * unit
        assert default.radsin(angle) == math.sin(angle)
        assert default.radcos(angle) == math.cos(angle)
        assert default.tursin(unit) == math.sin(angle)
        assert default.turcos(unit) == math.cos(angle)
