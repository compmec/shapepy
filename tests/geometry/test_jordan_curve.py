"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction

import numpy as np
import pynurbs
import pytest

from shapepy.geometry.jordancurve import JordanCurve
from shapepy.geometry.point import Point2D
from shapepy.scalar.reals import To


@pytest.mark.order(6)
@pytest.mark.dependency(
    depends=[
        "tests/geometry/test_polygon.py::test_end",
        "tests/geometry/test_curve.py::test_end",
        "tests/geometry/test_jordan_polygon.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestQuadraticJordan:
    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestQuadraticJordan::test_begin"])
    def test_creation(self):
        knotvector = [0, 0, 0, 1, 1, 2, 2, 2]
        knotvector = [Fraction(knot) for knot in knotvector]
        points = [(0, -1), (2, 0), (0, 1), (0, 1), (0, -1)]
        curve = pynurbs.Curve(knotvector)
        curve.ctrlpoints = [To.point(point) for point in points]
        JordanCurve.from_full_curve(curve)

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestQuadraticJordan::test_begin",
            "TestQuadraticJordan::test_creation",
        ]
    )
    def test_error_creation(self):
        with pytest.raises(TypeError):
            JordanCurve("asd")

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestQuadraticJordan::test_begin",
            "TestQuadraticJordan::test_creation",
            "TestQuadraticJordan::test_error_creation",
        ]
    )
    def test_intersection_fractions(self):
        knotvector = [0, 0, 0, 1, 1, 2, 2, 2]
        knotvector = [Fraction(knot) for knot in knotvector]

        pointsa = [(0, -2), (4, 0), (0, 2), (0, 0), (0, -2)]
        curvea = pynurbs.Curve(knotvector)
        curvea.ctrlpoints = [To.point(pt) for pt in pointsa]
        jordana = JordanCurve.from_full_curve(curvea)

        pointsb = [(3, -2), (-1, 0), (3, 2), (3, 0), (3, -2)]
        curveb = pynurbs.Curve(knotvector)
        curveb.ctrlpoints = [To.point(pt) for pt in pointsb]
        jordanb = JordanCurve.from_full_curve(curveb)

        good = [(0, 0, 1 / 4, 1 / 4), (0, 0, 3 / 4, 3 / 4)]
        test = jordana & jordanb
        test = np.array(test, dtype="float64")
        assert np.all(test == good)

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestQuadraticJordan::test_begin",
            "TestQuadraticJordan::test_creation",
            "TestQuadraticJordan::test_error_creation",
            "TestQuadraticJordan::test_intersection_fractions",
        ]
    )
    def test_intersection_float(self):
        knotvector = [0.0, 0.0, 0.0, 1.0, 1.0, 2.0, 2.0, 2.0]

        pointsa = [(0, -2), (4, 0), (0, 2), (0, 0), (0, -2)]
        # pointsa = np.array(pointsa, dtype="float64")
        curvea = pynurbs.Curve(knotvector)
        curvea.ctrlpoints = [To.point(pt) for pt in pointsa]
        jordana = JordanCurve.from_full_curve(curvea)

        pointsb = [(3, -2), (-1, 0), (3, 2), (3, 0), (3, -2)]
        # pointsb = np.array(pointsb, dtype="float64")
        curveb = pynurbs.Curve(knotvector)
        curveb.ctrlpoints = [To.point(pt) for pt in pointsb]
        jordanb = JordanCurve.from_full_curve(curveb)

        good = [(0, 0, 0.25, 0.25), (0, 0, 0.75, 0.75)]
        test = jordana & jordanb
        test = np.array(test, dtype="float64")
        np.testing.assert_allclose(test, good)

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestQuadraticJordan::test_begin",
            "TestQuadraticJordan::test_creation",
            "TestQuadraticJordan::test_error_creation",
            "TestQuadraticJordan::test_intersection_fractions",
            "TestQuadraticJordan::test_intersection_float",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(6)
@pytest.mark.dependency(
    depends=[
        "TestQuadraticJordan::test_end",
    ]
)
def test_end():
    pass
