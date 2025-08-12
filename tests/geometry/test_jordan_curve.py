"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction
from typing import Set

import numpy as np
import pynurbs
import pytest

from shapepy.geometry.factory import FactoryJordan
from shapepy.geometry.jordancurve import JordanCurve
from shapepy.scalar.reals import To


def equal_sets(
    seta: Set[float], setb: Set[float], tolerance: float = 1e-9
) -> bool:
    seta = set(seta)
    setb = set(setb)
    lista = sorted(seta - setb)
    listb = sorted(setb - seta)
    if len(lista) != len(listb):
        return False
    return all(abs(a - b) < tolerance for a, b in zip(lista, listb))


def equal_rbool_sets(
    seta: Set[float], setb: Set[float], tolerance: float = 1e-9
) -> bool:
    seta = set(v.internal for v in seta)
    setb = set(v for v in setb)
    lista = sorted(seta - setb)
    listb = sorted(setb - seta)
    if len(lista) != len(listb):
        return False
    return all(abs(a - b) < tolerance for a, b in zip(lista, listb))


@pytest.mark.order(16)
@pytest.mark.dependency(
    depends=[
        "tests/geometry/test_point.py::test_all",
        "tests/geometry/test_box.py::test_all",
        "tests/geometry/test_segment.py::test_all",
        "tests/geometry/test_piecewise.py::test_all",
        "tests/geometry/test_jordan_polygon.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


class TestQuadraticJordan:
    @pytest.mark.order(16)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(16)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestQuadraticJordan::test_begin"])
    def test_creation(self):
        knotvector = [0, 0, 0, 1, 1, 2, 2, 2]
        knotvector = [Fraction(knot) for knot in knotvector]
        points = [(0, -1), (2, 0), (0, 1), (0, 1), (0, -1)]
        curve = pynurbs.Curve(knotvector)
        curve.ctrlpoints = [To.point(point) for point in points]
        FactoryJordan.spline_curve(curve)

    @pytest.mark.order(16)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestQuadraticJordan::test_begin",
            "TestQuadraticJordan::test_creation",
        ]
    )
    def test_error_creation(self):
        with pytest.raises(ValueError):
            JordanCurve("asd")

    @pytest.mark.order(16)
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
        jordana = FactoryJordan.spline_curve(curvea)

        pointsb = [(3, -2), (-1, 0), (3, 2), (3, 0), (3, -2)]
        curveb = pynurbs.Curve(knotvector)
        curveb.ctrlpoints = [To.point(pt) for pt in pointsb]
        jordanb = FactoryJordan.spline_curve(curveb)

        test = jordana & jordanb
        assert equal_sets(test.all_knots[id(jordana)], {0, 0.25, 0.75, 1, 2})
        assert equal_sets(test.all_knots[id(jordanb)], {0, 0.25, 0.75, 1, 2})
        assert equal_rbool_sets(test.all_subsets[id(jordana)], {0.25, 0.75})
        assert equal_rbool_sets(test.all_subsets[id(jordanb)], {0.25, 0.75})

    @pytest.mark.order(16)
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
        pointsa = np.array(pointsa, dtype="float64")
        curvea = pynurbs.Curve(knotvector)
        curvea.ctrlpoints = [To.point(pt) for pt in pointsa]
        jordana = FactoryJordan.spline_curve(curvea)

        pointsb = [(3, -2), (-1, 0), (3, 2), (3, 0), (3, -2)]
        pointsb = np.array(pointsb, dtype="float64")
        curveb = pynurbs.Curve(knotvector)
        curveb.ctrlpoints = [To.point(pt) for pt in pointsb]
        jordanb = FactoryJordan.spline_curve(curveb)

        test = jordana & jordanb
        assert equal_sets(test.all_knots[id(jordana)], {0, 0.25, 0.75, 1, 2})
        assert equal_sets(test.all_knots[id(jordanb)], {0, 0.25, 0.75, 1, 2})
        assert equal_rbool_sets(test.all_subsets[id(jordana)], {0.25, 0.75})
        assert equal_rbool_sets(test.all_subsets[id(jordanb)], {0.25, 0.75})

    @pytest.mark.order(16)
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


@pytest.mark.order(16)
@pytest.mark.dependency(
    depends=[
        "TestQuadraticJordan::test_end",
    ]
)
def test_all():
    pass
