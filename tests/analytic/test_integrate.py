import pytest

from shapepy.analytic.bezier import Bezier
from shapepy.analytic.polynomial import Polynomial


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
    assert poly.integrate([0, 1]) == 0

    poly = Polynomial([3])
    assert poly.integrate([0, 1]) == 3
    assert poly.integrate([0, 2]) == 6

    poly = Polynomial([6, 24, 60])
    assert poly.integrate([0, 1]) == 38
    assert poly.integrate([0, 2]) == 220


@pytest.mark.order(9)
@pytest.mark.dependency(depends=["test_begin"])
def test_bezier():
    bezier = Bezier([0])
    assert bezier.integrate([0, 1]) == 0

    bezier = Bezier([3])
    assert bezier.integrate([0, 0.5]) == 3 / 2
    assert bezier.integrate([0.5, 1]) == 3 / 2

    bezier = Bezier([6, 12, 6])
    assert bezier.integrate([0, 0.5]) == 4
    assert bezier.integrate([0.5, 1]) == 4


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
