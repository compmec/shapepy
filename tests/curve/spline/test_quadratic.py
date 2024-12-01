"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction
from typing import Tuple

import pytest

from shapepy.curve.spline import KnotVector, SplineClosedCurve, SplineOpenCurve


@pytest.mark.order(6)
@pytest.mark.dependency(
    depends=[
        "tests/test_point.py::test_end",
        "tests/curve/spline/test_spline.py::test_end",
        "tests/curve/spline/test_linear.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestOpenCurve:

    @staticmethod
    def create_open_curve() -> SplineOpenCurve:
        knotvector = [0, 0, 0, 1, 1, 2, 2, 2]
        knotvector = KnotVector(knotvector, 2)
        ctrlpoints = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]
        return SplineOpenCurve(knotvector, ctrlpoints)

    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_begin"])
    def test_build(self):
        TestOpenCurve.create_open_curve()

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_build"])
    def test_check_vertices(self):
        curve = TestOpenCurve.create_open_curve()
        assert len(curve.vertices) == 3
        assert curve.vertices[0] == (1, 0)
        assert curve.vertices[1] == (0, 1)
        assert curve.vertices[2] == (-1, 0)

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_check_vertices"])
    def test_evaluate_vertices(self):
        curve = TestOpenCurve.create_open_curve()
        assert curve.eval(0) == curve.vertices[0]
        assert curve.eval(1) == curve.vertices[1]
        assert curve.eval(2) == curve.vertices[2]

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_evaluate_vertices"])
    def test_evaluate_middle(self):
        curve = TestOpenCurve.create_open_curve()
        assert curve.eval(0.5) == (0.75, 0.75)
        assert curve.eval(1.5) == (-0.75, 0.75)

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_evaluate_vertices"])
    def test_evaluate_derivate(self):
        curve = TestOpenCurve.create_open_curve()
        assert curve.eval(0, 1) == (0, 2)
        assert curve.eval(0.5, 1) == (-1, 1)
        assert curve.eval(1, 1) == (-2, 0)
        assert curve.eval(1.5, 1) == (-1, -1)
        assert curve.eval(2, 1) == (0, -2)

        assert curve.eval(0, 2) == (-2, -2)
        assert curve.eval(0.5, 2) == (-2, -2)
        assert curve.eval(1, 2) == (2, -2)
        assert curve.eval(1.5, 2) == (2, -2)
        assert curve.eval(2, 2) == (2, -2)

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_evaluate_vertices"])
    def test_projection(self):
        curve = TestOpenCurve.create_open_curve()
        assert curve.projection((0, 0)) == (0, 1, 2)
        assert curve.projection((1, 0)) == (0,)
        assert curve.projection((0, 1)) == (1,)
        assert curve.projection((-1, 0)) == (2,)
        assert curve.projection((1, 1)) == (0.5,)
        assert curve.projection((-1, 1)) == (1.5,)

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_build"])
    def test_lenght(self):
        curve = TestOpenCurve.create_open_curve()
        good_lenght = 4.820952239083992
        assert abs(curve.lenght - good_lenght) < 1e-9

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestOpenCurve::test_begin",
            "TestOpenCurve::test_build",
            "TestOpenCurve::test_check_vertices",
            "TestOpenCurve::test_evaluate_vertices",
            "TestOpenCurve::test_evaluate_middle",
            "TestOpenCurve::test_evaluate_derivate",
            "TestOpenCurve::test_projection",
            "TestOpenCurve::test_lenght",
        ]
    )
    def test_end(self):
        pass


class TestClosedCurve:

    @staticmethod
    def create_closed_curve() -> SplineOpenCurve:
        knotvector = [0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4]
        knotvector = KnotVector(knotvector, 2)
        ctrlpoints = [
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1),
            (1, 0),
        ]
        return SplineClosedCurve(knotvector, ctrlpoints)

    @pytest.mark.order(6)
    @pytest.mark.dependency(depends=["test_begin", "TestOpenCurve::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_begin"])
    def test_build(self):
        TestClosedCurve.create_closed_curve()

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_build"])
    def test_check_vertices(self):
        curve = TestClosedCurve.create_closed_curve()
        assert len(curve.vertices) == 4
        assert curve.vertices[0] == (1, 0)
        assert curve.vertices[1] == (0, 1)
        assert curve.vertices[2] == (-1, 0)
        assert curve.vertices[3] == (0, -1)

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_check_vertices"])
    def test_evaluate_vertices(self):
        curve = TestClosedCurve.create_closed_curve()
        assert curve.eval(0) == curve.vertices[0]
        assert curve.eval(1) == curve.vertices[1]
        assert curve.eval(2) == curve.vertices[2]
        assert curve.eval(3) == curve.vertices[3]
        assert curve.eval(4) == curve.vertices[0]

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestClosedCurve::test_evaluate_vertices"]
    )
    def test_evaluate_middle(self):
        curve = TestClosedCurve.create_closed_curve()
        assert curve.eval(0.5) == (0.5, 0)
        assert curve.eval(1.5) == (1, 0.5)
        assert curve.eval(2.5) == (0.5, 1)
        assert curve.eval(3.5) == (0, 0.5)

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestClosedCurve::test_evaluate_vertices"]
    )
    def test_evaluate_derivate(self):
        curve = TestClosedCurve.create_closed_curve()
        assert curve.eval(0, 1) == (0, 2)
        assert curve.eval(0.5, 1) == (-1, 1)
        assert curve.eval(1, 1) == (-2, 0)

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestClosedCurve::test_evaluate_vertices"]
    )
    def test_projection(self):
        curve = TestClosedCurve.create_closed_curve()
        assert curve.projection((0, 0)) == (0, 1, 2, 3)
        assert curve.projection((1, 0)) == (0,)
        assert curve.projection((1, 1)) == (0.5,)
        assert curve.projection((0, 1)) == (1,)

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_build"])
    def test_lenght(self):
        curve = TestClosedCurve.create_closed_curve()
        good_lenght = 19.25869268177884
        assert abs(curve.lenght - good_lenght) < 1e-9

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_build"])
    def test_area(self):
        curve = TestClosedCurve.create_closed_curve()
        good = 10 / 3
        assert abs(curve.area - good) < 1e-9

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_area"])
    def test_winding(self):
        curve = TestClosedCurve.create_closed_curve()
        assert curve.winding((0, 0)) == 1
        assert curve.winding((1, 0)) == 0.5
        assert curve.winding((1, 1)) == 0
        assert curve.winding((0, 1)) == 0.5
        assert curve.winding((0.5, 0)) == 1

    @pytest.mark.order(6)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestClosedCurve::test_begin",
            "TestClosedCurve::test_build",
            "TestClosedCurve::test_check_vertices",
            "TestClosedCurve::test_evaluate_vertices",
            "TestClosedCurve::test_evaluate_middle",
            "TestClosedCurve::test_evaluate_derivate",
            "TestClosedCurve::test_projection",
            "TestClosedCurve::test_compare",
            "TestClosedCurve::test_section",
            "TestClosedCurve::test_lenght",
            "TestClosedCurve::test_area",
            "TestClosedCurve::test_winding",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(6)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "TestOpenCurve::test_end",
        "TestClosedCurve::test_end",
    ]
)
def test_end():
    pass
