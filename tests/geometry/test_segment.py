"""
This file contains tests functions to test the module polygon.py
"""

import math
from fractions import Fraction

import numpy as np
import pytest

from shapepy.geometry.segment import IntegratePlanar, Math, Segment


@pytest.mark.order(13)
@pytest.mark.dependency(
    depends=[
        "tests/geometry/test_point.py::test_all",
        "tests/geometry/test_box.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(13)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_build():
    Segment([(0, 0), (1, 0), (0, 1)])


class TestDerivate:
    @pytest.mark.order(13)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "test_build",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestDerivate::test_begin"])
    def test_planar_bezier(self):
        points = [(0, 0), (1, 0), (0, 1)]
        curve = Segment(points)
        dcurve = curve.derivate()
        assert id(dcurve) != id(curve)

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestDerivate::test_begin",
            "TestDerivate::test_planar_bezier",
        ]
    )
    def test_end(self):
        pass


class TestIntegrate:
    @pytest.mark.order(13)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestIntegrate::test_begin"])
    def test_lenght(self):
        points = [(0, 0), (1, 0)]
        curve = Segment(points)
        assert IntegratePlanar.lenght(curve) == 1

        points = [(1, 0), (0, 0)]
        curve = Segment(points)
        assert IntegratePlanar.lenght(curve) == 1

        points = [(0, 1), (1, 0)]
        curve = Segment(points)
        assert abs(IntegratePlanar.lenght(curve) - np.sqrt(2)) < 1e-9

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestIntegrate::test_begin"])
    def test_winding_triangles(self):
        curve = Segment([(1, 0), (2, 0)])
        wind = IntegratePlanar.winding_number(curve)
        assert wind == 0

        curve = Segment([(1, 0), (1, 1)])
        wind = IntegratePlanar.winding_number(curve)
        assert abs(wind - 0.125) < 1e-9

        curve = Segment([(1, 0), (0, 1)])
        wind = IntegratePlanar.winding_number(curve)
        assert abs(wind - 0.25) < 1e-9

        curve = Segment([(1, 0), (-0.5, np.sqrt(3) / 2)])
        wind = IntegratePlanar.winding_number(curve)
        assert abs(3 * wind - 1) < 1e-9

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestIntegrate::test_begin",
            "TestIntegrate::test_winding_triangles",
        ]
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
            curve = Segment([point0, point1])
            test_wind = IntegratePlanar.winding_number(curve)
            diff = abs(good_wind - test_wind)
            maxim = max(maxim, diff)
            assert abs(good_wind - test_wind) < 1e-9

    @pytest.mark.order(13)
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
            curves = tuple(Segment(pair) for pair in pairs)
            for curve in curves:
                wind = IntegratePlanar.winding_number(curve)
                assert abs(nsides * wind - 1) < 1e-2

        for nsides in range(3, 10):
            angles = np.linspace(math.tau, 0, nsides + 1)
            ctrlpoints = np.vstack([np.cos(angles), np.sin(angles)]).T
            pairs = zip(ctrlpoints[:-1], ctrlpoints[1:])
            curves = tuple(Segment(pair) for pair in pairs)
            for curve in curves:
                wind = IntegratePlanar.winding_number(curve)
                assert abs(nsides * wind + 1) < 1e-2

    @pytest.mark.order(13)
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
    @pytest.mark.order(13)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOperations::test_begin"])
    def test_clean_segment(self):
        points = [(0, 0), (1, 0)]
        curve = Segment(points)
        curve.clean()
        assert curve.degree == 1

        points = [(2, 3), (-1, 4)]
        curve = Segment(points)
        curve.clean()
        assert curve.degree == 1

        points = [(2, 3), (-1, 4)]
        curve = Segment(points)
        curve.clean(tolerance=None)
        assert curve.degree == 1

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestOperations::test_begin",
            "TestOperations::test_clean_segment",
        ]
    )
    def test_clean_quadratic(self):
        points = [(0, 0), (1, 0), (2, 0)]
        curve = Segment(points)
        assert curve.degree == 2
        curve.clean()
        assert curve.degree == 1

        points = [(0, 2), (1, 4), (2, 6)]
        curve = Segment(points)
        assert curve.degree == 2
        curve.clean()
        assert curve.degree == 1

        points = [(2, 3), (-1, 4), (-4, 5)]
        curve = Segment(points)
        assert curve.degree == 2
        curve.clean(tolerance=None)
        assert curve.degree == 1

    @pytest.mark.order(13)
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
    @pytest.mark.order(13)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestContains::test_begin"])
    def test_line(self):
        points = [(0, 0), (1, 0)]
        curve = Segment(points)
        assert (0, 0) in curve
        assert (1, 0) in curve
        assert (0.5, 0) in curve
        assert (0, 1) not in curve
        assert (0, -1) not in curve

        points = [(0, 1), (0, 0)]
        curve = Segment(points)
        assert (0, 0) in curve
        assert (0, 1) in curve
        assert (0, 0.5) in curve
        assert (1, 0) not in curve
        assert (-1, 0) not in curve

        points = [(0, 0), (1, 1)]
        curve = Segment(points)
        assert (0, 0) in curve
        assert (1, 1) in curve
        assert (0.5, 0.5) in curve
        assert (0.25, 0.5) not in curve
        assert (0.75, 0.5) not in curve
        assert (-1, -1) not in curve
        assert (-0.1, -0.1) not in curve

    @pytest.mark.order(13)
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
    @pytest.mark.order(13)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestSplitUnite::test_begin"])
    def test_middle(self):
        half = Fraction(1, 2)
        points = [(0, 0), (1, 0)]
        curve = Segment(points)
        curvea, curveb = curve.split([half])
        assert curvea == Segment([(0, 0), (half, 0)])
        assert curveb == Segment([(half, 0), (1, 0)])

        test = curvea | curveb
        assert test == curve

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestSplitUnite::test_begin",
            "TestSplitUnite::test_middle",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(13)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_build",
    ]
)
def test_print():
    segment = Segment([(0, 0), (1, 0), (0, 1)])
    str(segment)
    repr(segment)


@pytest.mark.order(13)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_build",
        "TestDerivate::test_end",
        "TestIntegrate::test_end",
        "TestOperations::test_end",
        "TestContains::test_end",
        "TestSplitUnite::test_end",
        "test_print",
    ]
)
def test_all():
    pass
