import random

import pytest

from shapepy.analytic.polynomial import Polynomial
from shapepy.scalar.reals import Math


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "tests/scalar/test_reals.py::test_all",
        "tests/scalar/test_angle.py::test_all",
    ],
    scope="session",
)
def test_build():
    Polynomial([0])  # p(t) = 0
    Polynomial([1])  # p(t) = 1
    Polynomial([1, 2])  # p(t) = 1 + 2 * t
    Polynomial([1, 2, 3])  # p(t) = 1 + 2 * t + 3 * t^2
    Polynomial([1.0, 2, -3.0])  # p(t) = 1.0 + 2 * t - 3.0 * t^2


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build"])
def test_degree():
    poly = Polynomial([0])  # p(t) = 0
    assert poly.degree == 0
    poly = Polynomial([1])  # p(t) = 1
    assert poly.degree == 0
    poly = Polynomial([1, 2])  # p(t) = 1 + 2 * t
    assert poly.degree == 1
    poly = Polynomial([1, 2, 3])  # p(t) = 1 + 2 * t + 3 * t^2
    assert poly.degree == 2


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build"])
def test_coefficients():
    bezier = Polynomial([0])
    assert bezier[0] == 0
    bezier = Polynomial([1])
    assert bezier[0] == 1
    bezier = Polynomial([1, 2])
    assert bezier[0] == 1
    assert bezier[1] == 2
    bezier = Polynomial([1, 2, 3])
    assert bezier[0] == 1
    assert bezier[1] == 2
    assert bezier[2] == 3


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build", "test_degree"])
def test_compare():
    poly = Polynomial([0])
    assert poly == 0
    assert poly != 1
    assert poly != "asd"

    polya = Polynomial([3, 2])
    polyb = Polynomial([3.0, 2.0])
    assert polya == polyb


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build", "test_degree"])
def test_evaluate():
    poly = Polynomial([0])  # p(t) = 0
    assert poly(0) == 0
    assert poly(-1) == 0
    assert poly(2) == 0
    poly = Polynomial([1])  # p(t) = 1
    assert poly(0) == 1
    assert poly(-1) == 1
    assert poly(2) == 1
    poly = Polynomial([1, 2])  # p(t) = 1 + 2 * t
    assert poly(0) == 1
    assert poly(-1) == 1 + 2 * (-1)
    assert poly(2) == 1 + 2 * (+2)
    poly = Polynomial([1, 2, 3])  # p(t) = 1 + 2 * t + 3 * t^2
    assert poly(0) == 1
    assert poly(-1) == 1 + 2 * (-1) + 3 * (-1) * (-1)
    assert poly(2) == 1 + 2 * (+2) + 3 * (+2) * (+2)


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=["test_build", "test_degree", "test_evaluate", "test_compare"]
)
def test_neg():
    polya = Polynomial([1, 2, 3, 4])
    polyb = Polynomial([-1, -2, -3, -4])

    assert -polya == polyb


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=["test_build", "test_degree", "test_evaluate", "test_compare"]
)
def test_mul():
    """
    BasisFunctions to test if the polynomials coefficients
    are correctly computed
    """
    poly = Polynomial([1, -2, 3])
    assert 0 * poly == 0
    assert 0 * poly == Polynomial([0])
    assert 1 * poly == Polynomial([1, -2, 3])
    assert 2 * poly == Polynomial([2, -4, 6])

    poly = Polynomial([-1, 1])
    assert poly * poly == Polynomial([1, -2, 1])


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "test_build",
        "test_degree",
        "test_evaluate",
        "test_compare",
        "test_mul",
    ]
)
def test_pow():
    poly = Polynomial([-1, 1])
    assert poly**0 == 1
    assert poly**1 == poly
    assert poly**2 == poly * poly
    assert poly**3 == poly * poly * poly


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build"])
def test_print():
    poly = Polynomial([0])
    assert str(poly) == "0"
    poly = Polynomial([1])
    assert str(poly) == "1"
    poly = Polynomial([0, 1])
    assert str(poly) == "t"
    repr(poly)

    poly = Polynomial([1, 2, 3])
    assert str(poly) == "1 + 2 * t + 3 * t^2"
    repr(poly)

    poly = Polynomial([1, 2, 3], domain=[0, 1])
    assert repr(poly) == "[0, 1]: 1 + 2 * t + 3 * t^2"


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_evaluate"])
def test_infinity_evaluation():
    for const in range(-10, 11):
        poly = Polynomial([const])
        assert poly(Math.NEGINF) == const
        assert poly(Math.POSINF) == const

    for degree in range(1, 8, 2):
        subcoefs = list(random.randint(-10, 10) for _ in range(degree))
        poly = Polynomial(subcoefs + [1])
        assert poly(Math.NEGINF) == Math.NEGINF
        assert poly(Math.POSINF) == Math.POSINF
        poly = Polynomial(subcoefs + [-1])
        assert poly(Math.NEGINF) == Math.POSINF
        assert poly(Math.POSINF) == Math.NEGINF

    for degree in range(2, 9, 2):
        subcoefs = list(random.randint(-10, 10) for _ in range(degree))
        poly = Polynomial(subcoefs + [1])
        assert poly(Math.NEGINF) == Math.POSINF
        assert poly(Math.POSINF) == Math.POSINF
        poly = Polynomial(subcoefs + [-1])
        assert poly(Math.NEGINF) == Math.NEGINF
        assert poly(Math.POSINF) == Math.NEGINF


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "test_build",
        "test_degree",
        "test_evaluate",
        "test_neg",
        "test_mul",
        "test_pow",
        "test_infinity_evaluation",
    ]
)
def test_all():
    pass
