"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve 
"""

import math

import pytest

from shapepy.jordancurve import JordanCurve
from shapepy.primitive import Primitive
from shapepy.shape import EmptyShape, IntegrateShape, SimpleShape, WholeShape


@pytest.mark.order(8)
@pytest.mark.dependency(
    depends=[
        "tests/test_polygon.py::test_end",
        "tests/test_jordan_polygon.py::test_end",
        "tests/test_jordan_curve.py::test_end",
        "tests/test_primitive.py::test_end",
        "tests/test_contains.py::test_end",
        "tests/test_empty_whole.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestIntegrate:
    @pytest.mark.order(8)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(8)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestIntegrate::test_begin"])
    def test_centered_rectangular(self):
        width, height = 6, 10  # sides of rectangle
        nx, ny = 5, 5  # Max exponential
        rectangular = Primitive.square()
        rectangular.scale(width, height)
        for expx in range(nx):
            for expy in range(ny):
                test = IntegrateShape.polynomial(rectangular, expx, expy)
                if expx % 2 or expy % 2:
                    good = 0
                else:
                    good = width ** (expx + 1)
                    good *= height ** (expy + 1)
                    good /= (1 + expx) * (1 + expy)
                    good /= 2 ** (expx + expy)
                assert abs(test - good) < 1e-9

    @pytest.mark.order(8)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestIntegrate::test_begin",
            "TestIntegrate::test_centered_rectangular",
        ]
    )
    def test_noncenter_rectangular(self):
        width, height = 6, 10  # sides of rectangle
        center = 7, -3  # Center of shape
        nx, ny = 5, 5  # Max exponential
        rectangular = Primitive.square()
        rectangular.scale(width, height)
        rectangular.move(center)
        for expx in range(nx):
            for expy in range(ny):
                test = IntegrateShape.polynomial(rectangular, expx, expy)
                good = (center[0] + width / 2) ** (expx + 1) - (
                    center[0] - width / 2
                ) ** (expx + 1)
                good *= (center[1] + height / 2) ** (expy + 1) - (
                    center[1] - height / 2
                ) ** (expy + 1)
                good /= (1 + expx) * (1 + expy)
                assert abs(test - good) < 1e-9 * abs(good)

    @pytest.mark.order(8)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestIntegrate::test_begin",
            "TestIntegrate::test_centered_rectangular",
            "TestIntegrate::test_noncenter_rectangular",
        ]
    )
    def test_centered_rombo(self):
        width, height = 3, 5
        rombo = Primitive.regular_polygon(4)
        rombo.scale(width, height)
        nx, ny = 5, 5
        for expx in range(nx):
            for expy in range(ny):
                test = IntegrateShape.polynomial(rombo, expx, expy)
                if expx % 2 or expy % 2:
                    good = 0
                else:
                    good = 4 * width ** (expx + 1) * height ** (expy + 1)
                    good *= math.factorial(expx) * math.factorial(expy)
                    good /= math.factorial(expx + expy)
                    good /= (1 + expx + expy) * (2 + expx + expy)
                assert abs(test - good) < 1e-9

    @pytest.mark.order(8)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestIntegrate::test_begin",
            "TestIntegrate::test_centered_rectangular",
            "TestIntegrate::test_noncenter_rectangular",
            "TestIntegrate::test_centered_rombo",
        ]
    )
    def test_end(self):
        pass


class TestOthers:
    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
        ]
    )
    def test_print(self):
        points = [(0, 0), (1, 0), (0, 1)]
        jordancurve = JordanCurve.from_vertices(points)
        shape = SimpleShape(jordancurve)
        str(shape)
        repr(shape)

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
        ]
    )
    def test_compare(self):
        shapea = Primitive.regular_polygon(3)
        shapeb = Primitive.regular_polygon(4)
        assert shapea != shapeb
        with pytest.raises(ValueError):
            shapea != 0

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
            "TestOthers::test_print",
            "TestOthers::test_compare",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(8)
@pytest.mark.dependency(
    depends=[
        "TestIntegrate::test_end",
        "TestOthers::test_end",
    ]
)
def test_end():
    pass
