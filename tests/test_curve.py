"""
This file contains tests functions to test the module polygon.py
"""

import math
from fractions import Fraction

import numpy as np
import pytest

from compmec.shape.curve import BezierCurve, IntegratePlanar, Math, PlanarCurve


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "tests/test_polygon.py::test_end",
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
        points = np.random.uniform(-1, 1, 2)
        bezier = BezierCurve(points)
        assert bezier(0) == points[0]
        assert bezier(0.5) == 0.5 * (points[0] + points[1])
        assert bezier(1) == points[1]

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestScalarBezier::test_begin"])
    def test_degree_2(self):
        points = np.random.uniform(-1, 1, 3)
        bezier = BezierCurve(points)
        assert abs(bezier(0) - points[0]) < 1e-6
        good = 0.25 * (points[0] + 2 * points[1] + points[2])
        assert abs(bezier(0.5) - good) < 1e-6
        assert abs(bezier(1) - points[2]) < 1e-6

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestScalarBezier::test_begin",
            "TestScalarBezier::test_constant_one",
            "TestScalarBezier::test_constant_two",
            "TestScalarBezier::test_degree_1",
            "TestScalarBezier::test_degree_2",
        ]
    )
    def test_end(self):
        pass


class TestPlanarCurve:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestPlanarCurve::test_begin"])
    def test_construct(self):
        points = [(0, 0), (1, 0), (0, 1)]
        PlanarCurve(points)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestPlanarCurve::test_begin",
            "TestPlanarCurve::test_construct",
        ]
    )
    def test_end(self):
        pass


class TestDerivate:
    @pytest.mark.order(3)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestScalarBezier::test_end",
            "TestPlanarCurve::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestDerivate::test_begin"])
    def test_scalar_bezier(self):
        points = [0, 1, 0]
        curve = BezierCurve(points)
        dcurve = curve.derivate()
        assert id(dcurve) != id(curve)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestDerivate::test_begin"])
    def test_planar_bezier(self):
        points = [(0, 0), (1, 0), (0, 1)]
        curve = PlanarCurve(points)
        dcurve = curve.derivate()
        assert id(dcurve) != id(curve)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestDerivate::test_begin",
            "TestDerivate::test_scalar_bezier",
            "TestDerivate::test_planar_bezier",
        ]
    )
    def test_end(self):
        pass


class TestIntegrate:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestIntegrate::test_begin"])
    def test_lenght(self):
        points = [(0, 0), (1, 0)]
        curve = PlanarCurve(points)
        assert IntegratePlanar.lenght(curve) == 1

        points = [(1, 0), (0, 0)]
        curve = PlanarCurve(points)
        assert IntegratePlanar.lenght(curve) == 1

        points = [(0, 1), (1, 0)]
        curve = PlanarCurve(points)
        assert abs(IntegratePlanar.lenght(curve) - np.sqrt(2)) < 1e-9

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestIntegrate::test_begin"])
    def test_winding_triangles(self):
        curve = PlanarCurve([(1, 0), (2, 0)])
        wind = IntegratePlanar.winding_number(curve)
        assert wind == 0

        curve = PlanarCurve([(1, 0), (1, 1)])
        wind = IntegratePlanar.winding_number(curve)
        assert abs(wind - 0.125) < 1e-9

        curve = PlanarCurve([(1, 0), (0, 1)])
        wind = IntegratePlanar.winding_number(curve)
        assert abs(wind - 0.25) < 1e-9

        curve = PlanarCurve([(1, 0), (-0.5, np.sqrt(3) / 2)])
        wind = IntegratePlanar.winding_number(curve)
        assert abs(3 * wind - 1) < 1e-9

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestIntegrate::test_begin", "TestIntegrate::test_winding_triangles"]
    )
    def test_winding_unit_circle(self):
        ntests = 1000
        maxim = 0
        for k in range(ntests):
            angle0 = np.random.uniform(0, 2 * np.pi)
            good_wind = np.random.uniform(-0.5, 0.5)
            angle1 = angle0 + 2 * np.pi * good_wind
            point0 = (np.cos(angle0), np.sin(angle0))
            point1 = (np.cos(angle1), np.sin(angle1))
            curve = PlanarCurve([point0, point1])
            test_wind = IntegratePlanar.winding_number(curve)
            diff = abs(good_wind - test_wind)
            maxim = max(maxim, diff)
            assert abs(good_wind - test_wind) < 1e-9

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestIntegrate::test_begin",
            "TestIntegrate::test_winding_triangles",
            "TestIntegrate::test_winding_unit_circle",
        ]
    )
    def test_winding_regular_polygon(self):
        for nsides in range(3, 10):
            angles = np.linspace(0, math.tau, nsides + 1)
            ctrlpoints = np.vstack([np.cos(angles), np.sin(angles)]).T
            pairs = zip(ctrlpoints[:-1], ctrlpoints[1:])
            curves = tuple(PlanarCurve(pair) for pair in pairs)
            for curve in curves:
                wind = IntegratePlanar.winding_number(curve)
                assert abs(nsides * wind - 1) < 1e-2

        for nsides in range(3, 10):
            angles = np.linspace(math.tau, 0, nsides + 1)
            ctrlpoints = np.vstack([np.cos(angles), np.sin(angles)]).T
            pairs = zip(ctrlpoints[:-1], ctrlpoints[1:])
            curves = tuple(PlanarCurve(pair) for pair in pairs)
            for curve in curves:
                wind = IntegratePlanar.winding_number(curve)
                assert abs(nsides * wind + 1) < 1e-2

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestIntegrate::test_begin",
            "TestIntegrate::test_lenght",
            "TestIntegrate::test_winding_triangles",
            "TestIntegrate::test_winding_unit_circle",
            "TestIntegrate::test_winding_regular_polygon",
        ]
    )
    def test_end(self):
        pass


class TestOperations:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOperations::test_begin"])
    def test_clean_segment(self):
        points = [(0, 0), (1, 0)]
        curve = PlanarCurve(points)
        curve.clean()
        assert curve.degree == 1

        points = [(2, 3), (-1, 4)]
        curve = PlanarCurve(points)
        curve.clean()
        assert curve.degree == 1

        points = [(2, 3), (-1, 4)]
        curve = PlanarCurve(points)
        curve.clean(tolerance=None)
        assert curve.degree == 1

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestOperations::test_begin",
            "TestOperations::test_clean_segment",
        ]
    )
    def test_clean_quadratic(self):
        points = [(0, 0), (1, 0), (2, 0)]
        curve = PlanarCurve(points)
        assert curve.degree == 2
        curve.clean()
        assert curve.degree == 1

        points = [(0, 2), (1, 4), (2, 6)]
        curve = PlanarCurve(points)
        assert curve.degree == 2
        curve.clean()
        assert curve.degree == 1

        points = [(2, 3), (-1, 4), (-4, 5)]
        curve = PlanarCurve(points)
        assert curve.degree == 2
        curve.clean(tolerance=None)
        assert curve.degree == 1

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestOperations::test_begin",
            "TestOperations::test_clean_segment",
            "TestOperations::test_clean_quadratic",
        ]
    )
    def test_end(self):
        pass


class TestContains:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestContains::test_begin"])
    def test_line(self):
        points = [(0, 0), (1, 0)]
        curve = PlanarCurve(points)
        assert (0, 0) in curve
        assert (1, 0) in curve
        assert (0.5, 0) in curve
        assert (0, 1) not in curve
        assert (0, -1) not in curve

        points = [(0, 1), (0, 0)]
        curve = PlanarCurve(points)
        assert (0, 0) in curve
        assert (0, 1) in curve
        assert (0, 0.5) in curve
        assert (1, 0) not in curve
        assert (-1, 0) not in curve

        points = [(0, 0), (1, 1)]
        curve = PlanarCurve(points)
        assert (0, 0) in curve
        assert (1, 1) in curve
        assert (0.5, 0.5) in curve
        assert (0.25, 0.5) not in curve
        assert (0.75, 0.5) not in curve
        assert (-1, -1) not in curve
        assert (-0.1, -0.1) not in curve

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestContains::test_begin",
            "TestContains::test_line",
        ]
    )
    def test_end(self):
        pass


class TestSplitUnite:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestSplitUnite::test_begin"])
    def test_middle(self):
        half = Fraction(1, 2)
        points = [(0, 0), (1, 0)]
        curve = PlanarCurve(points)
        curvea, curveb = curve.split([half])
        assert curvea == PlanarCurve([(0, 0), (half, 0)])
        assert curveb == PlanarCurve([(half, 0), (1, 0)])

        test = curvea | curveb
        assert test == curve

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestSplitUnite::test_begin",
            "TestSplitUnite::test_middle",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "TestMath::test_end",
        "TestScalarBezier::test_end",
        "TestPlanarCurve::test_end",
        "TestDerivate::test_end",
        "TestIntegrate::test_end",
        "TestOperations::test_end",
        "TestContains::test_end",
        "TestSplitUnite::test_end",
    ]
)
def test_end():
    pass
