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
    assert poly.derivate() == 0

    poly = Polynomial([3])
    assert poly.derivate() == 0

    poly = Polynomial([1, 1, 1, 1, 1])
    assert poly.derivate(1) == Polynomial([1, 2, 3, 4])
    assert poly.derivate(2) == Polynomial([2, 6, 12])
    assert poly.derivate(3) == Polynomial([6, 24])

    assert poly.eval(0, 1) == 1
    assert poly.eval(1, 1) == 10
    assert poly.eval(0, 2) == 2
    assert poly.eval(1, 2) == 20


@pytest.mark.order(9)
@pytest.mark.dependency(depends=["test_begin"])
def test_bezier():
    bezier = Bezier([0])
    assert bezier.derivate() == 0

    bezier = Bezier([3])
    assert bezier.derivate() == 0

    bezier = Bezier([1, 1, 1, 1, 1])
    assert bezier.derivate() == 0

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
