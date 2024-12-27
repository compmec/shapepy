"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction

import pytest

from shapepy.analytic import Trignomial
from shapepy.analytic.utils import usincos
from shapepy.core import Math
from shapepy.curve.piecewise import PiecewiseClosedCurve, PiecewiseOpenCurve


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=["tests/analytic/test_trigonometric.py::test_end"],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(4)
@pytest.mark.timeout(2)
@pytest.mark.dependency(depends=["test_begin"])
def test_create_circle():
    xfunc = Trignomial([0, 0, 1])
    yfunc = Trignomial([0, 1, 0])
    curve = PiecewiseClosedCurve([(xfunc, yfunc)])

    assert curve.knots == (0, 1)
    assert curve.lenght == Math.tau


@pytest.mark.order(4)
@pytest.mark.timeout(2)
@pytest.mark.dependency(depends=["test_create_circle"])
def test_projection():
    ndivs = 4
    uangles = tuple(Fraction(i, ndivs) for i in range(ndivs))

    xfunc = Trignomial([0, 0, 1])
    yfunc = Trignomial([0, 1, 0])
    curve = PiecewiseClosedCurve([(xfunc, yfunc)])

    for uangle in uangles:
        sin, cos = usincos(uangle)
        for s in (1 / 2, 1, 2):
            nodes = curve.projection((s * cos, s * sin))
            assert len(nodes) == 1
            assert abs(nodes[0] - uangle) < 1e-9

    xfunc = Trignomial([0, 0, 1])
    yfunc = Trignomial([0, -1, 0])
    curve = PiecewiseClosedCurve([(xfunc, yfunc)])

    for uangle in uangles[1:]:
        sin, cos = usincos(uangle)
        for s in (1 / 2, 1, 2):
            nodes = curve.projection((s * cos, s * sin))
            assert len(nodes) == 1
            assert abs(1 - uangle - nodes[0]) < 1e-9


@pytest.mark.order(4)
@pytest.mark.timeout(2)
@pytest.mark.dependency(depends=["test_projection"])
def test_winding():
    ndivs = 4
    uangles = tuple(Fraction(i, ndivs) for i in range(ndivs))

    xfunc = Trignomial([0, 0, 1])
    yfunc = Trignomial([0, 1, 0])
    curve = PiecewiseClosedCurve([(xfunc, yfunc)])

    assert curve.winding((0, 0)) == 1
    for uangle in uangles:
        sin, cos = usincos(uangle)
        assert curve.winding((cos / 2, sin / 2)) == 1
        assert curve.winding((cos, sin)) == 0.5
        assert curve.winding((2 * cos, 2 * sin)) == 0

    xfunc = Trignomial([0, 0, 1])
    yfunc = Trignomial([0, -1, 0])
    curve = PiecewiseClosedCurve([(xfunc, yfunc)])

    assert curve.winding((0, 0)) == 0
    for uangle in uangles:
        sin, cos = usincos(uangle)
        assert curve.winding((cos / 2, sin / 2)) == 0
        assert curve.winding((cos, sin)) == 0.5
        assert curve.winding((2 * cos, 2 * sin)) == 1


@pytest.mark.order(4)
@pytest.mark.timeout(2)
@pytest.mark.dependency(depends=["test_create_circle"])
def test_section():
    xfunc = Trignomial([0, 0, 1])
    yfunc = Trignomial([0, 1, 0])
    fullcurve = PiecewiseClosedCurve([(xfunc, yfunc)])
    assert fullcurve.section(0, 1) == fullcurve

    nodes = tuple(Fraction(i, 16) for i in range(16))
    for nodea, nodeb in zip(nodes, nodes[1:]):
        curve = fullcurve.section(nodea, nodeb)
        assert len(curve.functions) == 1
        for xfunc, yfunc in curve.functions:
            assert isinstance(xfunc, Trignomial)
            assert isinstance(yfunc, Trignomial)
            assert xfunc.frequency == 1 / 16
            assert yfunc.frequency == 1 / 16
        assert fullcurve.eval(nodea) == curve.vertices[0]
        assert fullcurve.eval(nodeb) == curve.vertices[-1]

    xfunc = Trignomial([0, 0, 1], 1 / 4)
    yfunc = Trignomial([0, 1, 0], 1 / 4)
    curve = PiecewiseOpenCurve([(xfunc, yfunc)])
    assert fullcurve.section(0, 1 / 4) == curve

    xfunc = Trignomial([0, -1, 0], 1 / 4)
    yfunc = Trignomial([0, 0, 1], 1 / 4)
    curve = PiecewiseOpenCurve([(xfunc, yfunc)])
    assert fullcurve.section(1 / 4, 2 / 4) == curve

    xfunc = Trignomial([0, 0, -1], 1 / 4)
    yfunc = Trignomial([0, -1, 0], 1 / 4)
    curve = PiecewiseOpenCurve([(xfunc, yfunc)])
    assert fullcurve.section(2 / 4, 3 / 4) == curve

    xfunc = Trignomial([0, 1, 0], 1 / 4)
    yfunc = Trignomial([0, 0, -1], 1 / 4)
    curve = PiecewiseOpenCurve([(xfunc, yfunc)])
    assert fullcurve.section(3 / 4, 1) == curve


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_create_circle",
        "test_winding",
        "test_projection",
        "test_section",
    ]
)
def test_end():
    pass
