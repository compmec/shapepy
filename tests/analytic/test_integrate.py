import pytest

from shapepy.analytic.bezier import Bezier
from shapepy.analytic.polynomial import Polynomial
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
    poly = Polynomial([0])
    assert poly.integrate(1) == 0
    assert poly.integrate(2) == 0

    poly = Polynomial([3])
    assert poly.integrate(1) == Polynomial([0, 3])
    assert poly.integrate(2) == Polynomial([0, 0, 3 / 2])

    poly = Polynomial([6, 24, 60])
    assert poly.integrate(1) == Polynomial([0, 6, 12, 20])
    assert poly.integrate(2) == Polynomial([0, 0, 3, 4, 5])
    assert poly.integrate(3) == Polynomial([0, 0, 0, 1, 1, 1])


@pytest.mark.order(9)
@pytest.mark.dependency(depends=["test_begin"])
def test_bezier():
    bezier = To.bezier([0])
    assert bezier.integrate(1) == 0
    assert bezier.integrate(2) == 0

    bezier = To.bezier([3])
    assert bezier.integrate(1) == Bezier([0, 3])
    assert bezier.integrate(2) == Bezier([0, 0, 1.5])

    bezier = To.bezier([6, 6, 6, 6, 6])
    assert bezier.integrate(1) == Bezier([0, 6])
    assert bezier.integrate(2) == Bezier([0, 0, 3])
    assert bezier.integrate(3) == Bezier([0, 0, 0, 1])


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
