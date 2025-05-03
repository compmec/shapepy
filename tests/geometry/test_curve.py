import pytest

from shapepy.analytic.elementar import piecewise, polynomial
from shapepy.angle import Angle
from shapepy.bool1d import IntervalR1
from shapepy.geometry import (
    ClosedCurve,
    ContinuousCurve,
    JordanCurve,
    move_curve,
    move_point,
    reverse,
    rotate_curve,
    rotate_point,
    scale_curve,
    scale_point,
)


@pytest.mark.order(32)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "tests/analytic/test_polynomial.py::test_all",
        "tests/geometry/test_point.py::test_all",
        "tests/geometry/test_bound.py::test_all",
    ],
    scope="session",
)
def test_build_polynomial():
    domain = (-1, 1)
    xfunc = polynomial((1, 2, 3), domain)
    yfunc = polynomial((3, -2, 6), domain)
    ContinuousCurve(xfunc, yfunc)


class TestSquare:

    @staticmethod
    def square_analytics():
        xpolys = [
            polynomial([-1, 2]),  # (0, 1)
            polynomial([1]),  # (1, 2)
            polynomial([5, -2]),  # (2, 3)
            polynomial([-1]),  # (3, 4)
        ]
        ypolys = [
            polynomial([-1]),  # (0, 1)
            polynomial([-3, 2]),  # (1, 2)
            polynomial([1]),  # (2, 3)
            polynomial([7, -2]),  # (3, 4)
        ]

        xfunc = piecewise(xpolys, range(5))
        yfunc = piecewise(ypolys, range(5))
        return xfunc, yfunc

    @pytest.mark.order(32)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_build_polynomial"])
    def test_build(self):
        xfunc, yfunc = TestSquare.square_analytics()
        ContinuousCurve(xfunc, yfunc)
        ClosedCurve(xfunc, yfunc)
        JordanCurve(xfunc, yfunc)

    @pytest.mark.order(32)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestSquare::test_build"])
    def test_length(self):
        xfunc, yfunc = TestSquare.square_analytics()
        curve = ContinuousCurve(xfunc, yfunc)
        assert curve.lenght == 8

    @pytest.mark.order(32)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestSquare::test_build"])
    def test_area(self):
        xfunc, yfunc = TestSquare.square_analytics()
        curve = ClosedCurve(xfunc, yfunc)
        assert curve.area == 4

    @pytest.mark.order(32)
    @pytest.mark.timeout(5)
    @pytest.mark.dependency(depends=["TestSquare::test_build"])
    def test_winding(self):
        xfunc, yfunc = TestSquare.square_analytics()
        curve = ClosedCurve(xfunc, yfunc)
        # Exterior points
        for point in [(-2, -2), (-2, 2), (2, 2), (2, -2)]:
            assert curve.winding(point) == 0
        # Interior points
        coords = (-0.5, 0, 0.5)
        for xcoord in coords:
            for ycoord in coords:
                point = (xcoord, ycoord)
                assert curve.winding(point) == 1
        # Edge points
        for coord in coords:
            assert curve.winding((-1, coord)) == 0.5
            assert curve.winding((1, coord)) == 0.5
            assert curve.winding((coord, 1)) == 0.5
            assert curve.winding((coord, -1)) == 0.5

        # Vertices of the square
        for vertex in [(-1, -1), (-1, 1), (1, 1), (1, -1)]:
            assert curve.winding(vertex) == 0.25

    @pytest.mark.order(32)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestSquare::test_build"])
    def test_projection(self):
        xfunc, yfunc = TestSquare.square_analytics()
        curve = ContinuousCurve(xfunc, yfunc)

        point = (0, 0)
        test = curve.projection(point)
        good = {0.5, 1.5, 2.5, 3.5}
        assert test == good

    @pytest.mark.order(32)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestSquare::test_build"])
    def test_move(self):
        xfunc, yfunc = TestSquare.square_analytics()
        curve = ContinuousCurve(xfunc, yfunc)
        vector = (5, -7)
        moved = move_curve(curve, vector)

        tvalues = (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4)
        for tval in tvalues:
            good = move_point(curve.eval(tval), vector)
            assert moved.eval(tval) == good

    @pytest.mark.order(32)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestSquare::test_build"])
    def test_scale(self):
        xfunc, yfunc = TestSquare.square_analytics()
        curve = ContinuousCurve(xfunc, yfunc)
        vector = (5, -7)
        scaled = scale_curve(curve, vector)

        tvalues = (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4)
        for tval in tvalues:
            good = scale_point(curve.eval(tval), vector)
            assert scaled.eval(tval) == good

    @pytest.mark.order(32)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestSquare::test_build"])
    def test_rotate(self):
        xfunc, yfunc = TestSquare.square_analytics()
        curve = ContinuousCurve(xfunc, yfunc)
        angle = Angle.degrees(90)
        rotated = rotate_curve(curve, angle)

        tvalues = (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4)
        for tval in tvalues:
            good = rotate_point(curve.eval(tval), angle)
            assert rotated.eval(tval) == good

    @pytest.mark.order(32)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestSquare::test_build"])
    def test_print(self):
        xfunc, yfunc = TestSquare.square_analytics()
        curve = ContinuousCurve(xfunc, yfunc)
        str(curve)
        repr(curve)

        curve = ClosedCurve(xfunc, yfunc)
        str(curve)
        repr(curve)

        curve = JordanCurve(xfunc, yfunc)
        str(curve)
        repr(curve)

    @pytest.mark.order(32)
    @pytest.mark.dependency(
        depends=[
            "TestSquare::test_build",
            "TestSquare::test_length",
            "TestSquare::test_area",
            "TestSquare::test_winding",
            "TestSquare::test_projection",
            "TestSquare::test_move",
            "TestSquare::test_scale",
            "TestSquare::test_rotate",
            "TestSquare::test_print",
        ]
    )
    def test_all(self):
        pass


@pytest.mark.order(32)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build_polynomial"])
def test_compare():
    domain = IntervalR1(-1, 1)
    xfunc = polynomial((1, 2), domain)
    yfunc = polynomial((3, -2), domain)
    curvea = ContinuousCurve(xfunc, yfunc)

    xfunc = polynomial((1, 2), domain)
    yfunc = polynomial((3, -2), domain)
    curveb = ContinuousCurve(xfunc, yfunc)

    xfunc = polynomial((3, 2), domain)
    yfunc = polynomial((1, -2), domain)
    curvec = ContinuousCurve(xfunc, yfunc)

    assert curvea == curveb
    assert curvea != curvec

    assert curvea != 0
    assert curvea != {0, 1, 2}


@pytest.mark.order(32)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build_polynomial"])
def test_evaluate():
    domain = IntervalR1(-1, 1)
    xfunc = polynomial((1, 2), domain)
    yfunc = polynomial((3, -2), domain)
    curve = ContinuousCurve(xfunc, yfunc)
    assert curve.eval(-1) == (-1, 5)
    assert curve.eval(0) == (1, 3)
    assert curve.eval(1) == (3, 1)


@pytest.mark.order(32)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build_polynomial"])
def test_reverse():
    domain = [-1, 1]
    xfunc = polynomial((1, 2, 3), domain)
    yfunc = polynomial((3, -2, 6), domain)
    ocurve = ContinuousCurve(xfunc, yfunc)
    rcurve = reverse(ocurve)

    assert rcurve.eval(-1) == ocurve.eval(1)
    assert rcurve.eval(-0.5) == ocurve.eval(0.5)
    assert rcurve.eval(0) == ocurve.eval(0)
    assert rcurve.eval(0.5) == ocurve.eval(-0.5)
    assert rcurve.eval(1) == ocurve.eval(-1)

    domain = [0, 1]
    xfunc = polynomial((1, 2, 3), domain)
    yfunc = polynomial((3, -2, 6), domain)
    ocurve = ContinuousCurve(xfunc, yfunc)
    rcurve = reverse(ocurve)

    assert rcurve.eval(0) == ocurve.eval(1)
    assert rcurve.eval(0.5) == ocurve.eval(0.5)
    assert rcurve.eval(1) == ocurve.eval(0)


@pytest.mark.order(32)
@pytest.mark.dependency(
    depends=[
        "test_build_polynomial",
        "TestSquare::test_all",
        "test_evaluate",
        "test_reverse",
    ]
)
def test_all():
    pass
