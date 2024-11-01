"""
This file contains tests functions to test the module polygon.py
"""

import pytest

from shapepy.curve.spline.analytic import Polynomial


@pytest.mark.order(3)
@pytest.mark.dependency()
def test_begin():
    pass


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin"])
def test_build():
    Polynomial([1])  # p(x) = 1
    Polynomial([1, 1])  # p(x) = 1 + x
    Polynomial([1, 2])  # p(x) = 1 + 2*x
    Polynomial([1, 3, 2])  # 1 + 3*x + 2*x^2
    Polynomial([1.0, 2.0, 3.0])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin"])
def test_degree():
    assert Polynomial([1]).degree == 0
    assert Polynomial([1, 1]).degree == 1
    assert Polynomial([1, 2]).degree == 1
    assert Polynomial([1, 3, 2]).degree == 2
    assert Polynomial([1.0, 2.0, 3.0]).degree == 2


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build"])
def test_evaluate_natural():
    poly = Polynomial([1])  # p(x) = 1
    assert poly.eval(0) == 1
    assert poly.eval(1) == 1
    assert poly.eval(2) == 1
    assert poly.eval(1.0) == 1

    poly = Polynomial([1, 2])  # p(x) = 1 + 2*x
    assert poly.eval(0) == 1
    assert poly.eval(1) == 3
    assert poly.eval(2) == 5
    assert poly.eval(0.0) == 1
    assert poly.eval(1.0) == 3

    poly = Polynomial([1, 2, 3])  # p(x) = 1 + 2*x + 3*x^2
    assert poly.eval(0) == 1
    assert poly.eval(1) == 6
    assert poly.eval(2) == 17
    assert poly.eval(0.0) == 1
    assert poly.eval(1.0) == 6


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=["test_evaluate_natural", "test_evaluate_derivate", "test_degree"]
)
def test_keep_type():
    coefs = [3, 5, -4, 3, 2]
    poly = Polynomial(coefs)
    for deriv in range(0, poly.degree):
        for node in range(-5, 6):
            val = poly.eval(node, deriv)
            assert isinstance(val, int)
        for node in range(-5, 6):
            val = poly.eval(float(node), deriv)
            assert isinstance(val, float)

    coefs = [3.0, 5.0, -4.0, 3.0, 2.0]
    poly = Polynomial(coefs)
    for deriv in range(0, poly.degree):
        for node in range(-5, 6):
            val = poly.eval(node, deriv)
            assert isinstance(val, float)
        for node in range(-5, 6):
            val = poly.eval(float(node), deriv)
            assert isinstance(val, float)

    from fractions import Fraction

    one = Fraction(1)
    coefs = [3 * one, 5 * one, -4 * one, 3 * one, 2 * one]
    poly = Polynomial(coefs)
    for deriv in range(0, poly.degree):
        for node in range(-5, 6):
            val = poly.eval(node, deriv)
            assert isinstance(val, Fraction)
        for node in range(-5, 6):
            val = poly.eval(float(node), deriv)
            assert isinstance(val, float)


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_degree"])
def test_compare():
    coefs = [3, 5, -4, 3, 2]
    polya = Polynomial(coefs)
    coefs = [3, 5, -4, 3, 2, 7]
    polyb = Polynomial(coefs)
    assert polya != polyb

    coefs = [3, 5, -4, 3, 2]
    polya = Polynomial(coefs)
    coefs = [3, 5, -4, 3, 2]
    polyb = Polynomial(coefs)
    assert polya == polyb

    coefs = [3, 5, -4, 3, 2]
    polya = Polynomial(coefs)
    coefs = [3, -3, -4, 3, 2]
    polyb = Polynomial(coefs)
    assert polya != polyb


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_derivate():
    coefs = [3, 5, -4, 3, 2]
    poly = Polynomial(coefs)
    test = poly.derivate(0)
    assert test == poly

    test = poly.derivate(1)
    good = Polynomial([5, -8, 9, 8])
    assert test != poly
    assert test == good

    test = poly.derivate(2)
    good = Polynomial([-8, 18, 24])
    assert test != poly
    assert test == good


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_evaluate_natural", "test_derivate"])
def test_evaluate_derivate():
    poly = Polynomial([1])  # p(x) = 1
    assert poly.eval(0, 1) == 0
    assert poly.eval(1, 1) == 0
    assert poly.eval(2, 1) == 0
    assert poly.eval(1.0, 1) == 0
    assert poly.eval(1, 2) == 0

    poly = Polynomial([1, 2])  # p(x) = 1 + 2*x
    assert poly.eval(0, 1) == 2
    assert poly.eval(1, 1) == 2
    assert poly.eval(2, 1) == 2
    assert poly.eval(0.0, 1) == 2
    assert poly.eval(1.0, 1) == 2
    assert poly.eval(2, 2) == 0
    assert poly.eval(0.0, 2) == 0

    poly = Polynomial([1, 2, 3])  # p(x) = 1 + 2*x + 3*x^2
    assert poly.eval(0, 1) == 2
    assert poly.eval(1, 1) == 8
    assert poly.eval(2, 1) == 14
    assert poly.eval(0.0, 1) == 2
    assert poly.eval(1.0, 1) == 8
    assert poly.eval(2, 2) == 6
    assert poly.eval(0.0, 2) == 6
    assert poly.eval(2, 3) == 0
    assert poly.eval(0.0, 3) == 0


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_add():
    polya = Polynomial([1, 3])
    assert polya + 3 == Polynomial([4, 3])
    assert 3 + polya == Polynomial([4, 3])

    polya = Polynomial([1, 2, 3])
    polyb = Polynomial([3, 2, 1])
    assert polya + polyb == Polynomial([4, 4, 4])

    polya = Polynomial([1, 2, 3])
    polyb = Polynomial([3, 2, 1, 7])
    assert polya + polyb == Polynomial([4, 4, 4, 7])

    polya = Polynomial([1, 2, 3, 7])
    polyb = Polynomial([3, 2, 1])
    assert polya + polyb == Polynomial([4, 4, 4, 7])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_sub():
    polya = Polynomial([1, 3])
    assert polya - 3 == Polynomial([-2, 3])
    assert 3 - polya == Polynomial([2, -3])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_mult():
    polya = Polynomial([1, 3])
    assert 4 * polya == Polynomial([4, 12])
    assert polya * 4 == Polynomial([4, 12])

    polya = Polynomial([1, 1])
    polyb = Polynomial([1, 1])
    assert polya * polyb == Polynomial([1, 2, 1])

    polya = Polynomial([1, 1])
    polyb = Polynomial([1, 2, 1])
    assert polya * polyb == Polynomial([1, 3, 3, 1])

    polya = Polynomial([1, 2, 1])
    polyb = Polynomial([1, 2, 1])
    assert polya * polyb == Polynomial([1, 4, 6, 4, 1])

    polya = Polynomial([1, 1])
    polyb = Polynomial([1, 3, 3, 1])
    assert polya * polyb == Polynomial([1, 4, 6, 4, 1])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_pow():
    poly = Polynomial([1, 1])
    assert poly**0 == Polynomial([1])
    assert poly**1 == Polynomial([1, 1])
    assert poly**2 == Polynomial([1, 2, 1])
    assert poly**3 == Polynomial([1, 3, 3, 1])
    assert poly**4 == Polynomial([1, 4, 6, 4, 1])

    poly = Polynomial([1, 2])
    assert poly**0 == Polynomial([1])
    assert poly**1 == Polynomial([1, 2])
    assert poly**2 == Polynomial([1, 4, 4])
    assert poly**3 == Polynomial([1, 6, 12, 8])
    assert poly**4 == Polynomial([1, 8, 24, 32, 16])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_shift():
    poly = Polynomial([-1, 3, -3, 1])  # (x-1)^3
    assert poly.shift(-1) == Polynomial([0, 0, 0, 1])  # x^3

    poly = Polynomial([1, 8, 24, 32, 16])  # (1+2*x)^4
    assert poly.shift(1 / 2) == Polynomial([0, 0, 0, 0, 16])  # (2*x)^4


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_scale():
    poly = Polynomial([1, 2, 3])  # 1 + 2*x + 3*x^2
    assert poly.scale(2) == Polynomial([1, 4, 12])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build"])
def test_print():
    poly = Polynomial([0])
    assert str(poly) == "0"
    poly = Polynomial([0, 0])
    assert str(poly) == "0"
    poly = Polynomial([0, 0, 0])
    assert str(poly) == "0"
    poly = Polynomial([1])
    assert str(poly) == "1"
    poly = Polynomial([1, 1])
    assert str(poly) == "1 + x"
    poly = Polynomial([1, 1, 1])
    assert str(poly) == "1 + x + x^2"
    poly = Polynomial([1, 0, 1])
    assert str(poly) == "1 + x^2"
    poly = Polynomial([0, 0, 1])
    assert str(poly) == "x^2"
    poly = Polynomial([-1])
    assert str(poly) == "- 1"
    poly = Polynomial([-1, 1])
    assert str(poly) == "- 1 + x"
    poly = Polynomial([1, -1, 1])
    assert str(poly) == "1 - x + x^2"
    poly = Polynomial([1, 0, 1])
    assert str(poly) == "1 + x^2"
    poly = Polynomial([1, 2, 3])
    assert str(poly) == "1 + 2 * x + 3 * x^2"
    repr(poly)


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_build",
        "test_degree",
        "test_evaluate_natural",
        "test_keep_type",
        "test_compare",
        "test_derivate",
        "test_evaluate_derivate",
        "test_add",
        "test_sub",
        "test_mult",
        "test_pow",
        "test_shift",
        "test_scale",
    ]
)
def test_end():
    pass
