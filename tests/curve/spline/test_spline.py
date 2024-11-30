"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction

import numpy as np
import pynurbs
import pytest

from shapepy.curve.spline.spline import KnotVector, Spline


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=["tests/analytic/test_polynomial.py::test_end"],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_begin"])
def test_build():
    knotvector = KnotVector([0, 0, 1, 2, 2])
    ctrlpoints = np.random.uniform(-1, 1, knotvector.npts)
    Spline(knotvector, ctrlpoints)


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build"])
def test_bezier():
    nsample = 17
    tsample = tuple(Fraction(i, nsample - 1) for i in range(nsample))
    for degree in range(8):
        knotvector = pynurbs.GeneratorKnotVector.bezier(degree, Fraction)
        ctrlpoints = np.random.randint(-3, 4, degree + 1)
        ctrlpoints = tuple(map(Fraction, ctrlpoints))
        pynurbs_curve = pynurbs.Curve(knotvector, ctrlpoints)
        knotvector = KnotVector(knotvector, knotvector.degree)
        custom_curve = Spline(knotvector, ctrlpoints)
        for ti in tsample:
            assert custom_curve.eval(ti) == pynurbs_curve(ti)


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_bezier"])
def test_spline():
    nsample = 33
    tsample = tuple(Fraction(i, nsample - 1) for i in range(nsample))
    uniform = pynurbs.GeneratorKnotVector.uniform
    for degree in range(4):
        for npts in range(degree + 1, degree + 6):
            knotvector = uniform(degree, npts, Fraction)
            ctrlpoints = np.random.randint(-3, 4, npts)
            ctrlpoints = tuple(map(Fraction, ctrlpoints))
            pynurbs_curve = pynurbs.Curve(knotvector, ctrlpoints)
            knotvector = KnotVector(knotvector, knotvector.degree)
            custom_curve = Spline(knotvector, ctrlpoints)
            for ti in tsample:
                assert custom_curve.eval(ti) == pynurbs_curve(ti)


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_build",
        "test_bezier",
        "test_spline",
    ]
)
def test_end():
    pass
