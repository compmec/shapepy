"""
This file contains tests functions to test the module polygon.py
"""

import math
from fractions import Fraction

import numpy as np
import pytest

from shapepy import Primitive
from shapepy.curve.spline import JordanSpline, KnotVector
from shapepy.integral import polynomial
from shapepy.shape import SimpleShape


@pytest.mark.order(10)
@pytest.mark.dependency(
    depends=[
        "tests/test_shape.py::test_end",
        "tests/test_primitive.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestRectangle:
    @pytest.mark.order(10)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(10)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestRectangle::test_begin"])
    def test_area(self):
        base, height = 4, 12
        rectangle = Primitive.square().scale(base, height)
        assert polynomial(rectangle, (0, 0)) == base * height

    @pytest.mark.order(10)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestRectangle::test_begin", "TestRectangle::test_area"]
    )
    def test_first(self):
        base, height = 4, 12
        rectangle = Primitive.square().scale(base, height)
        assert polynomial(rectangle, (1, 0)) == 0
        assert polynomial(rectangle, (0, 1)) == 0

    @pytest.mark.order(10)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestRectangle::test_begin",
            "TestRectangle::test_area",
            "TestRectangle::test_first",
        ]
    )
    def test_second(self):
        base, height = 4, 12
        rectangle = Primitive.square().scale(base, height)
        assert polynomial(rectangle, (2, 0)) == base**3 * height / 12
        assert polynomial(rectangle, (1, 1)) == 0
        assert polynomial(rectangle, (0, 2)) == base * height**3 / 12

    @pytest.mark.order(10)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestRectangle::test_begin",
            "TestRectangle::test_area",
            "TestRectangle::test_first",
            "TestRectangle::test_second",
        ]
    )
    def test_centered(self):
        ntests = 100
        for _ in range(ntests):
            base, height = np.random.uniform(1, 3, 2)
            rectangle = Primitive.square().scale(base, height)
            for expx in range(0, 10):
                for expy in range(0, 10):
                    test = polynomial(rectangle, (expx, expy))
                    if expx % 2 or expy % 2:
                        assert abs(test) < 1e-6
                        continue
                    good = base ** (expx + 1) * height ** (expy + 1)
                    good /= (expx + 1) * (expy + 1)
                    good /= 2 ** (expx + expy)
                    assert abs(test - good) < 1e-9

    @pytest.mark.order(10)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestRectangle::test_begin",
            "TestRectangle::test_area",
            "TestRectangle::test_first",
            "TestRectangle::test_second",
            "TestRectangle::test_centered",
        ]
    )
    def test_end(self):
        pass


class TestQuadratic:
    @staticmethod
    def create_simple_shape():
        knotvector = (0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4)
        knotvector = tuple(map(Fraction, knotvector))
        knotvector = KnotVector(knotvector, 2)
        ctrlpoints = (
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1),
            (1, 0),
        )
        jordan = JordanSpline(knotvector, ctrlpoints)
        return SimpleShape(jordan)

    @pytest.mark.order(10)
    @pytest.mark.dependency(
        depends=[
            "tests/curve/spline/test_spline.py::test_end",
            "tests/curve/spline/test_linear.py::test_end",
            "tests/test_integral.py::test_begin",
        ],
        scope="session",
    )
    def test_begin(self):
        TestQuadratic.create_simple_shape()

    @pytest.mark.order(10)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestQuadratic::test_begin"])
    def test_area(self):
        shape = TestQuadratic.create_simple_shape()
        test = polynomial(shape, (0, 0))
        assert abs(test - 10 / 3) < 1e-9
        test = polynomial(~shape, (0, 0))
        assert abs(test + 10 / 3) < 1e-9

    @pytest.mark.order(10)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestQuadratic::test_begin",
            "TestQuadratic::test_area",
        ]
    )
    def test_end(self):
        pass


class TestCircle:
    @staticmethod
    def sincos_integ(expcos: int, expsin: int) -> float:
        """
        Computes I(a, b):
        2*pi * I(a, b) = int_{0}^{2pi} sin(x)^a*cos(x)^b dx
        """
        if expsin % 2 or expcos % 2:
            return 0
        a, b = expsin // 2, expcos // 2
        soma = 0
        for i in range(a + 1):
            val = 1
            for j in range(b + i):
                val *= (2 * j + 1) / (2 * j + 2)
            soma += val * math.comb(a, i) * (1 - 2 * (i % 2))
        return soma

    @staticmethod
    def bidim_integ(
        radius: float, xcenter: float, ycenter: float, expx: int, expy: int
    ):
        """
        Computes I(R, x, y, a, b):
        I(a, b) =
            int_{0}^{2pi} int_{0}^{R} (x+r*cos t)^a * (y+r*sin t)^b * r dr dt
        """
        soma = 0
        for i in range(expx + 1):
            for j in range(expy + 1):
                value = math.comb(expx, i) * math.comb(expy, j)
                value *= xcenter ** (expx - i) * ycenter ** (expy - j)
                value *= radius ** (i + j + 2) / (i + j + 2)
                value *= TestCircle.sincos_integ(i, j)
                soma += value
        return 2 * math.pi * soma

    @pytest.mark.order(10)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(10)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestCircle::test_begin"])
    def test_area(self):
        circle = Primitive.circle(radius=1, center=(0, 0))
        assert polynomial(circle, (0, 0)) == math.pi

        for radius in (1, 2, 3, 10):
            circle = Primitive.circle(radius=radius, center=(0, 0))
            assert polynomial(circle, (0, 0)) == math.pi * radius**2
            assert polynomial(~circle, (0, 0)) == -math.pi * radius**2

    @pytest.mark.order(10)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestCircle::test_begin", "TestCircle::test_area"]
    )
    def test_first(self):
        for radius in (1, 2, 3, 10):
            circle = Primitive.circle(radius=radius, center=(0, 0))
            assert polynomial(circle, (1, 0)) == 0
            assert polynomial(circle, (0, 1)) == 0
            circle = ~circle
            assert polynomial(circle, (1, 0)) == 0
            assert polynomial(circle, (0, 1)) == 0

    @pytest.mark.order(10)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestCircle::test_begin",
            "TestCircle::test_area",
            "TestCircle::test_first",
        ]
    )
    def test_second(self):
        for radius in (1, 2, 3, 10):
            circle = Primitive.circle(radius=radius, center=(0, 0))
            assert polynomial(circle, (2, 0)) == math.pi * radius**4 / 4
            assert polynomial(circle, (1, 1)) == 0
            assert polynomial(circle, (0, 2)) == math.pi * radius**4 / 4
            circle = ~circle
            assert polynomial(circle, (2, 0)) == -math.pi * radius**4 / 4
            assert polynomial(circle, (1, 1)) == 0
            assert polynomial(circle, (0, 2)) == -math.pi * radius**4 / 4

    @pytest.mark.order(10)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestCircle::test_begin",
            "TestCircle::test_area",
            "TestCircle::test_first",
            "TestCircle::test_second",
        ]
    )
    def test_centered(self):
        ntests = 5
        for _ in range(ntests):
            radius = np.random.uniform(1, 2)
            circle = Primitive.circle(radius, (0, 0))
            for expx in range(0, 10):
                for expy in range(0, 10):
                    test = polynomial(circle, (expx, expy))
                    good = radius ** (expx + expy + 2)
                    good *= 2 * math.pi / (expx + expy + 2)
                    good *= TestCircle.sincos_integ(expx, expy)
                    assert abs(test - good) < 1e-6

    @pytest.mark.order(10)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestCircle::test_centered"])
    def test_random(self):
        ntests = 5
        for _ in range(ntests):
            radius = np.random.uniform(0.25, 1)
            xcen, ycen = np.random.uniform(-1, 1, 2)
            circle = Primitive.circle(radius, (xcen, ycen))
            for expx in range(10):
                for expy in range(10):
                    test = polynomial(circle, (expx, expy))
                    good = TestCircle.bidim_integ(
                        radius, xcen, ycen, expx, expy
                    )
                    assert abs(test - good) < 1e-9

    @pytest.mark.order(10)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestCircle::test_begin",
            "TestCircle::test_area",
            "TestCircle::test_first",
            "TestCircle::test_second",
            "TestCircle::test_centered",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(10)
@pytest.mark.dependency(
    depends=[
        "TestRectangle::test_end",
        "TestQuadratic::test_end",
        "TestCircle::test_end",
    ]
)
def test_end():
    pass
