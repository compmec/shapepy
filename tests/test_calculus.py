"""
This file contains tests functions to test the module polygon.py
"""

import math
from fractions import Fraction

import numpy as np
import pytest

from compmec.shape.calculus import BezierCurveIntegral, JordanCurveIntegral
from compmec.shape.jordancurve import JordanCurve
from compmec.shape.primitive import Primitive


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "tests/test_polygon.py::test_end",
        "tests/test_jordan_polygon.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestIntegralSurface:
    @pytest.mark.order(4)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestIntegralSurface::test_begin"])
    def test_centered_rectangular(self):
        width, height = 6, 10  # sides of rectangle
        nx, ny = 5, 5  # Max exponential
        rectangular = Primitive.square()
        rectangular.scale(width // 2, height // 2)
        jordan_curve = rectangular.jordancurve
        segments = jordan_curve.segments
        for expx in range(nx):
            for expy in range(ny):
                test = JordanCurveIntegral.polynomial((expx, expy), segments)
                if expx % 2 or expy % 2:
                    good = 0
                else:
                    good = width ** (expx + 1)
                    good *= height ** (expy + 1)
                    good /= (1 + expx) * (1 + expy)
                    good /= 2 ** (expx + expy)
                assert abs(test - good) < 1e-9

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestIntegralSurface::test_begin",
            "TestIntegralSurface::test_centered_rectangular",
        ]
    )
    def test_noncenter_rectangular(self):
        width, height = 6, 10  # sides of rectangle
        center = 7, -3  # Center of shape
        nx, ny = 5, 5  # Max exponential
        rectangular = Primitive.square()
        rectangular.scale(width // 2, height // 2)
        rectangular.move(center)
        jordan_curve = rectangular.jordancurve
        segments = jordan_curve.segments
        for expx in range(nx):
            for expy in range(ny):
                test = JordanCurveIntegral.polynomial((expx, expy), segments)
                good = (center[0] + width / 2) ** (expx + 1) - (
                    center[0] - width / 2
                ) ** (expx + 1)
                good *= (center[1] + height / 2) ** (expy + 1) - (
                    center[1] - height / 2
                ) ** (expy + 1)
                good /= (1 + expx) * (1 + expy)
                assert abs(test - good) < 1e-9 * abs(good)

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestIntegralSurface::test_begin",
            "TestIntegralSurface::test_centered_rectangular",
            "TestIntegralSurface::test_noncenter_rectangular",
        ]
    )
    def test_centered_rombo(self):
        width, height = 3, 5
        rombo = Primitive.regular_polygon(4)
        rombo.scale(width, height)
        jordan_curve = rombo.jordancurve
        segments = jordan_curve.segments
        nx, ny = 5, 5
        for expx in range(nx):
            for expy in range(ny):
                test = JordanCurveIntegral.polynomial((expx, expy), segments)
                if expx % 2 or expy % 2:
                    good = 0
                else:
                    good = 4 * width ** (expx + 1) * height ** (expy + 1)
                    good /= math.comb(expx + expy, expx)
                    good /= (1 + expx + expy) * (2 + expx + expy)
                assert abs(test - good) < 1e-9

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestIntegralSurface::test_begin",
            "TestIntegralSurface::test_centered_rectangular",
            "TestIntegralSurface::test_noncenter_rectangular",
            "TestIntegralSurface::test_centered_rombo",
        ]
    )
    def test_end(self):
        pass


class TestWindingNumber:
    @pytest.mark.order(4)
    @pytest.mark.dependency(depends=["test_begin", "TestIntegralSurface::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestWindingNumber::test_begin"])
    def test_regular_polygon(self):
        for nsides in range(3, 10):
            angles = np.linspace(0, math.tau, nsides + 1)
            ctrlpoints = np.vstack([np.cos(angles), np.sin(angles)]).T
            for pair in zip(ctrlpoints[:-1], ctrlpoints[1:]):
                wind = BezierCurveIntegral.winding_number(pair)
                assert abs(nsides * wind - 1) < 1e-9

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestWindingNumber::test_begin",
            "TestWindingNumber::test_regular_polygon",
        ]
    )
    def test_end(self):
        pass


class TestLenght:
    @pytest.mark.order(4)
    @pytest.mark.dependency(depends=["test_begin", "TestIntegralSurface::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestLenght::test_begin"])
    def test_square(self):
        side = 3
        square = Primitive.square(side)
        jordan_curve = square.jordancurve
        assert abs(jordan_curve.lenght - 4 * side) < 1e-9

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestLenght::test_begin"])
    def test_regular_polygon(self):
        for nsides in range(3, 10):
            lenght = 2 * nsides * np.sin(math.pi / nsides)
            shape = Primitive.regular_polygon(nsides)
            jordan_curve = shape.jordancurve
            assert (jordan_curve.lenght - lenght) < 1e-9

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestLenght::test_begin"])
    def test_circle(self):
        shape = Primitive.circle()
        jordan_curve = shape.jordancurve
        test = jordan_curve.lenght
        good = math.tau
        assert abs(test - good) < 1e-3

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestLenght::test_begin",
            "TestLenght::test_square",
            "TestLenght::test_regular_polygon",
            "TestLenght::test_circle",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "TestIntegralSurface::test_end",
        "TestWindingNumber::test_end",
        "TestLenght::test_end",
    ]
)
def test_end():
    pass
