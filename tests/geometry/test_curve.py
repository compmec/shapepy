import pytest

from shapepy.analytic.elementar import piecewise, polynomial
from shapepy.bool1d import IntervalR1
from shapepy.geometry import ClosedCurve, ContinuousCurve, JordanCurve, reverse


@pytest.mark.order(15)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "tests/analytic/test_polynomial.py::test_all",
        "tests/geometry/test_point.py::test_all",
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

    @pytest.mark.order(15)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_build_polynomial"])
    def test_build(self):
        xfunc, yfunc = TestSquare.square_analytics()
        ContinuousCurve(xfunc, yfunc)
        ClosedCurve(xfunc, yfunc)
        JordanCurve(xfunc, yfunc)

    @pytest.mark.order(15)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestSquare::test_build"])
    def test_length(self):
        xfunc, yfunc = TestSquare.square_analytics()
        curve = ContinuousCurve(xfunc, yfunc)
        assert curve.lenght == 8

    @pytest.mark.order(15)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestSquare::test_build"])
    def test_area(self):
        xfunc, yfunc = TestSquare.square_analytics()
        curve = ClosedCurve(xfunc, yfunc)
        assert curve.area == 4

    @pytest.mark.order(15)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestSquare::test_build"])
    def test_winding(self):
        xfunc, yfunc = TestSquare.square_analytics()
        curve = ClosedCurve(xfunc, yfunc)
        # Points on vertices
        for vertex in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            assert curve.winding(vertex) == 0.25
        # Points on edges
        for point in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
            assert curve.winding(point) == 0.5
        # Exterior points
        for point in [(-2, -2), (2, 2)]:
            assert curve.winding(point) == 0
        # Interior points
        for point in [(0, 0)]:
            assert curve.winding(point) == 1

    @pytest.mark.order(15)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestSquare::test_build"])
    def test_projection(self):
        xfunc, yfunc = TestSquare.square_analytics()
        curve = ContinuousCurve(xfunc, yfunc)

        point = (0, 0)
        test = curve.projection(point)
        good = {0.5, 1.5, 2.5, 3.5}
        assert test == good

    @pytest.mark.order(15)
    @pytest.mark.dependency(
        depends=[
            "TestSquare::test_build",
            "TestSquare::test_length",
            "TestSquare::test_area",
            "TestSquare::test_winding",
            "TestSquare::test_projection",
        ]
    )
    def test_all(self):
        pass


@pytest.mark.order(15)
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


@pytest.mark.order(15)
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


@pytest.mark.order(15)
@pytest.mark.dependency(
    depends=[
        "test_build_polynomial",
        "test_build_piecewise_square",
        "test_evaluate",
        "test_reverse",
        "TestProjection::test_square",
    ]
)
def test_all():
    pass
