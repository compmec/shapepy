import random
from fractions import Fraction
from typing import Iterable, Union

import pytest

from shapepy.analytic.bezier import Bezier
from shapepy.analytic.calculus import (
    derivate,
    derivate_bezier,
    derivate_polynomial,
    integrate,
    integrate_bezier,
    integrate_polynomial,
)
from shapepy.analytic.polynomial import Polynomial
from shapepy.tools import To


@pytest.mark.order(9)
@pytest.mark.dependency(
    depends=[
        "tests/analytic/test_polynomial.py::test_all",
        "tests/analytic/test_bezier.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


class TestDerivate:

    @pytest.mark.order(9)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_polynomial(self):
        poly = Polynomial([0])
        assert derivate_polynomial(poly, 1) == 0
        assert derivate_polynomial(poly, 2) == 0

        poly = Polynomial([3])
        assert derivate_polynomial(poly, 1) == 0
        assert derivate_polynomial(poly, 2) == 0

        poly = Polynomial([1, 1, 1, 1, 1])
        assert derivate_polynomial(poly, 1) == Polynomial([1, 2, 3, 4])
        assert derivate_polynomial(poly, 2) == Polynomial([2, 6, 12])
        assert derivate_polynomial(poly, 3) == Polynomial([6, 24])

    @pytest.mark.order(9)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_bezier(self):
        bezier = To.bezier([0])
        assert derivate_bezier(bezier, 1) == 0
        assert derivate_bezier(bezier, 2) == 0

        bezier = To.bezier([3])
        assert derivate_bezier(bezier, 1) == 0
        assert derivate_bezier(bezier, 2) == 0

        bezier = To.bezier([1, 1, 1, 1, 1])
        assert derivate_bezier(bezier, 1) == 0
        assert derivate_bezier(bezier, 2) == 0
        assert derivate_bezier(bezier, 3) == 0

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestDerivate::test_polynomial",
            "TestDerivate::test_bezier",
        ]
    )
    def test_all(self):
        pass


class TestIntegrate:

    @pytest.mark.order(9)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_polynomial(self):
        poly = Polynomial([0])
        assert integrate_polynomial(poly, 1) == 0
        assert integrate_polynomial(poly, 2) == 0

        poly = Polynomial([3])
        assert integrate_polynomial(poly, 1) == Polynomial([0, 3])
        assert integrate_polynomial(poly, 2) == Polynomial([0, 0, 3 / 2])

        poly = Polynomial([6, 24, 60])
        assert integrate_polynomial(poly, 1) == Polynomial([0, 6, 12, 20])
        assert integrate_polynomial(poly, 2) == Polynomial([0, 0, 3, 4, 5])
        assert integrate_polynomial(poly, 3) == Polynomial([0, 0, 0, 1, 1, 1])

    @pytest.mark.order(9)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_bezier(self):
        bezier = To.bezier([0])
        assert integrate_bezier(bezier, 1) == 0
        assert integrate_bezier(bezier, 2) == 0

        bezier = To.bezier([3])
        assert integrate_bezier(bezier, 1) == Bezier([0, 3])
        assert integrate_bezier(bezier, 2) == Bezier([0, 0, 1.5])

        bezier = To.bezier([6, 6, 6, 6, 6])
        assert integrate_bezier(bezier, 1) == Bezier([0, 6])
        assert integrate_bezier(bezier, 2) == Bezier([0, 0, 3])
        assert integrate_bezier(bezier, 3) == Bezier([0, 0, 0, 1])

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestIntegrate::test_polynomial",
            "TestIntegrate::test_bezier",
        ]
    )
    def test_all(self):
        pass


class TestIntegrateDerivate:

    @staticmethod
    def generate_functions(
        quantity: int, tipo: type
    ) -> Iterable[Union[Polynomial, Bezier]]:
        random.seed(0)
        for _ in range(quantity):
            npts = random.randint(1, 10)
            coefs = (Fraction(random.randint(-5, 5)) for _ in range(npts))
            yield tipo(coefs)

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestDerivate::test_polynomial",
            "TestIntegrate::test_polynomial",
        ]
    )
    def test_polynomial(self):
        for poly in TestIntegrateDerivate.generate_functions(100, Polynomial):
            for times in range(5):
                assert derivate(integrate(poly, times), times) == poly

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestDerivate::test_bezier",
            "TestIntegrate::test_bezier",
        ]
    )
    def test_bezier(self):
        for bezier in TestIntegrateDerivate.generate_functions(100, Bezier):
            for times in range(5):
                assert derivate(integrate(bezier, times), times) == bezier

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestIntegrateDerivate::test_polynomial",
            "TestIntegrateDerivate::test_bezier",
        ]
    )
    def test_all(self):
        pass


@pytest.mark.order(9)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "TestDerivate::test_all",
        "TestIntegrate::test_all",
        "TestIntegrateDerivate::test_all",
    ]
)
def test_all():
    pass
