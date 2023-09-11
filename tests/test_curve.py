"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction

import numpy as np
import pytest

from compmec.shape import Point2D
from compmec.shape.curve import BezierCurve, Math, PlanarCurve


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        # "tests/test_polygon.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestMath:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestMath::test_begin"])
    def test_comb(self):
        assert Math.comb(1, 0) == 1
        assert Math.comb(1, 1) == 1

        assert Math.comb(2, 0) == 1
        assert Math.comb(2, 1) == 2
        assert Math.comb(2, 2) == 1

        assert Math.comb(3, 0) == 1
        assert Math.comb(3, 1) == 3
        assert Math.comb(3, 2) == 3
        assert Math.comb(3, 3) == 1

        assert Math.comb(4, 0) == 1
        assert Math.comb(4, 1) == 4
        assert Math.comb(4, 2) == 6
        assert Math.comb(4, 3) == 4
        assert Math.comb(4, 4) == 1

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestMath::test_begin"])
    def test_horner_method(self):
        coefs = [1]  # f(x) = 1
        assert Math.horner_method(0, coefs) == 1
        assert Math.horner_method(0.5, coefs) == 1
        assert Math.horner_method(1, coefs) == 1

        coefs = [2, 1]  # f(x) = 1 + 2*x
        assert Math.horner_method(0, coefs) == 1
        assert Math.horner_method(0.5, coefs) == 2
        assert Math.horner_method(1, coefs) == 3

        coefs = [1, 2]  # f(x) = 2 + x
        assert Math.horner_method(0, coefs) == 2
        assert Math.horner_method(0.5, coefs) == 2.5
        assert Math.horner_method(1, coefs) == 3

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestMath::test_begin",
            "TestMath::test_comb",
        ]
    )
    def test_bezier_carac_matrix(self):
        test = Math.bezier_caract_matrix(0)
        good = [[1]]
        np.testing.assert_allclose(test, good)

        test = Math.bezier_caract_matrix(1)
        good = [[-1, 1], [1, 0]]
        np.testing.assert_allclose(test, good)

        test = Math.bezier_caract_matrix(2)
        good = [[1, -2, 1], [-2, 2, 0], [1, 0, 0]]
        np.testing.assert_allclose(test, good)

        test = Math.bezier_caract_matrix(3)
        good = [[-1, 3, -3, 1], [3, -6, 3, 0], [-3, 3, 0, 0], [1, 0, 0, 0]]
        np.testing.assert_allclose(test, good)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestMath::test_begin",
            "TestMath::test_comb",
            "TestMath::test_horner_method",
            "TestMath::test_bezier_carac_matrix",
        ]
    )
    def test_end(self):
        pass


class TestScalarBezier:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestScalarBezier::test_begin"])
    def test_constant_one(self):
        bezier = BezierCurve([1])
        assert bezier(0) == 1
        assert bezier(0.5) == 1
        assert bezier(1) == 1

        bezier = BezierCurve([1, 1])
        assert bezier(0) == 1
        assert bezier(0.5) == 1
        assert bezier(1) == 1

        bezier = BezierCurve([1, 1, 1])
        assert bezier(0) == 1
        assert bezier(0.5) == 1
        assert bezier(1) == 1

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestScalarBezier::test_begin"])
    def test_constant_two(self):
        const = 2
        bezier = BezierCurve([const])
        assert bezier(0) == const
        assert bezier(0.5) == const
        assert bezier(1) == const

        bezier = BezierCurve([const] * 2)
        assert bezier(0) == const
        assert bezier(0.5) == const
        assert bezier(1) == const

        bezier = BezierCurve([const] * 3)
        assert bezier(0) == const
        assert bezier(0.5) == const
        assert bezier(1) == const

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestScalarBezier::test_begin"])
    def test_degree_1(self):
        const = 2
        bezier = BezierCurve([const])
        assert bezier(0) == const
        assert bezier(0.5) == const
        assert bezier(1) == const

        bezier = BezierCurve([const] * 2)
        assert bezier(0) == const
        assert bezier(0.5) == const
        assert bezier(1) == const

        bezier = BezierCurve([const] * 3)
        assert bezier(0) == const
        assert bezier(0.5) == const
        assert bezier(1) == const

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestScalarBezier::test_begin",
            "TestScalarBezier::test_constant_one",
            "TestScalarBezier::test_constant_two",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["TestMath::test_end", "TestScalarBezier::test_end"])
def test_end():
    pass
