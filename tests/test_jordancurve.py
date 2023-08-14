"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction

import pytest

from compmec import nurbs
from compmec.shape import Point2D
from compmec.shape.jordancurve import JordanCurve


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "tests/test_polygon.py::test_end",
        "tests/test_jordanpolygon.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestQuadraticJordan:
    @pytest.mark.order(4)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestQuadraticJordan::test_begin"])
    def test_creation(self):
        knotvector = [0, 0, 0, 1, 1, 2, 2, 2]
        knotvector = [Fraction(knot) for knot in knotvector]
        points = [(0, -1), (2, 0), (0, 1), (0, 1), (0, -1)]
        curve = nurbs.Curve(knotvector)
        curve.ctrlpoints = [Point2D(point) for point in points]
        JordanCurve(curve)

    @pytest.mark.order(4)
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

    @pytest.mark.order(4)
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
        # pointsa = np.array(pointsa, dtype="float64")
        curvea = nurbs.Curve(knotvector)
        curvea.ctrlpoints = [Point2D(pt) for pt in pointsa]
        jordana = JordanCurve(curvea)

        pointsb = [(3, -2), (-1, 0), (3, 2), (3, 0), (3, -2)]
        # pointsb = np.array(pointsb, dtype="float64")
        curveb = nurbs.Curve(knotvector)
        curveb.ctrlpoints = [Point2D(pt) for pt in pointsb]
        jordanb = JordanCurve(curveb)

        assert jordana & jordanb == set([(1 / 4, 1 / 4), (3 / 4, 3 / 4)])

    @pytest.mark.order(4)
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
        curvea = nurbs.Curve(knotvector)
        curvea.ctrlpoints = [Point2D(pt) for pt in pointsa]
        jordana = JordanCurve(curvea)

        pointsb = [(3, -2), (-1, 0), (3, 2), (3, 0), (3, -2)]
        # pointsb = np.array(pointsb, dtype="float64")
        curveb = nurbs.Curve(knotvector)
        curveb.ctrlpoints = [Point2D(pt) for pt in pointsb]
        jordanb = JordanCurve(curveb)

        good_inters = set([(0.25, 0.25), (0.75, 0.75)])
        test_inters = jordana & jordanb

        set0 = set(test_inters - good_inters)
        set1 = set(good_inters - test_inters)
        for ui, vj in tuple(set0):
            for uk, vl in tuple(set1):
                if abs(ui - uk) > 1e-9:
                    continue
                if abs(vj - vl) > 1e-9:
                    continue
                set0.remove((ui, vj))
                set1.remove((uk, vl))
        assert (set0 | set1) == set()

    @pytest.mark.order(4)
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


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "TestQuadraticJordan::test_end",
    ]
)
def test_end():
    pass