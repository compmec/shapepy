"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction

import pytest

from shapepy.analytic import Trignomial
from shapepy.analytic.utils import usincos
from shapepy.core import Math
from shapepy.curve.piecewise import JordanPiecewise, PiecewiseClosedCurve


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "tests/analytic/test_trigonometric.py::test_end",
        "tests/curve/trigonom/test_circle.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(4)
@pytest.mark.timeout(2)
@pytest.mark.dependency(depends=["test_begin"])
def test_create_ellipse():
    xfunc = Trignomial([0, 0, 3])
    yfunc = Trignomial([0, 2, 0])
    curve = PiecewiseClosedCurve([(xfunc, yfunc)])

    assert curve.knots == (0, 1)


@pytest.mark.order(4)
@pytest.mark.timeout(2)
@pytest.mark.dependency(depends=["test_create_circle"])
def test_projection():
    ndivs = 16
    uangles = tuple(Fraction(i, ndivs) for i in range(ndivs))

    xfunc = Trignomial([0, 0, 3])
    yfunc = Trignomial([0, 2, 0])
    curve = PiecewiseClosedCurve([(xfunc, yfunc)])

    assert curve.projection((0, 0)) == (1 / 4, 3 / 4)
    for uangle in uangles:
        sin, cos = usincos(uangle)
        assert curve.projection((3 * cos, 2 * sin)) == (uangle,)

    xfunc = Trignomial([0, 0, 3])
    yfunc = Trignomial([0, -2, 0])
    curve = PiecewiseClosedCurve([(xfunc, yfunc)])

    assert curve.projection((0, 0)) == (1 / 4, 3 / 4)
    for uangle in uangles:
        sin, cos = usincos(uangle)
        assert curve.projection((3 * cos, 2 * sin)) == (1 - uangle,)


@pytest.mark.order(4)
@pytest.mark.timeout(2)
@pytest.mark.dependency(depends=["test_projection"])
def test_winding():
    ndivs = 16
    uangles = tuple(Fraction(i, ndivs) for i in range(ndivs))

    xfunc = Trignomial([0, 0, 3])
    yfunc = Trignomial([0, 2, 0])
    curve = PiecewiseClosedCurve([(xfunc, yfunc)])

    assert curve.winding((0, 0)) == 1
    for uangle in uangles:
        sin, cos = usincos(uangle)
        assert curve.winding((3 * cos, 2 * sin)) == 0.5
        assert curve.winding((6 * cos, 4 * sin)) == 0

    xfunc = Trignomial([0, 0, 3])
    yfunc = Trignomial([0, -2, 0])
    curve = PiecewiseClosedCurve([(xfunc, yfunc)])

    assert curve.winding((0, 0)) == 0
    for uangle in uangles:
        sin, cos = usincos(uangle)
        assert curve.winding((3 * cos, 2 * sin)) == 0.5
        assert curve.winding((6 * cos, 4 * sin)) == 1


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_create_circle",
        "test_winding",
        "test_projection",
    ]
)
def test_end():
    pass
