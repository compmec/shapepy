import pytest

from shapepy.analytic.bezier import Bezier
from shapepy.analytic.polynomial import Polynomial
from shapepy.analytic.tools import derivate_analytic
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


@pytest.mark.order(9)
@pytest.mark.dependency(depends=["test_begin"])
def test_polynomial():
    poly = To.polynomial([0])
    assert derivate_analytic(poly) == 0

    poly = To.polynomial([3])
    assert derivate_analytic(poly) == 0

    poly = To.polynomial([1, 1, 1, 1, 1])
    assert derivate_analytic(poly, 1) == Polynomial([1, 2, 3, 4])
    assert derivate_analytic(poly, 2) == Polynomial([2, 6, 12])
    assert derivate_analytic(poly, 3) == Polynomial([6, 24])

    assert poly.eval(0, 1) == 1
    assert poly.eval(1, 1) == 10
    assert poly.eval(0, 2) == 2
    assert poly.eval(1, 2) == 20


@pytest.mark.order(9)
@pytest.mark.dependency(depends=["test_begin"])
def test_bezier():
    bezier = To.bezier([0])
    assert derivate_analytic(bezier) == 0

    bezier = To.bezier([3])
    assert derivate_analytic(bezier) == 0

    bezier = To.bezier([1, 1, 1, 1, 1])
    assert derivate_analytic(bezier) == 0

    assert bezier.eval(0, 1) == 0
    assert bezier.eval(1, 1) == 0


@pytest.mark.order(9)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_polynomial",
        "test_bezier",
    ]
)
def test_all():
    pass
