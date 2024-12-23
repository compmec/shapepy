"""
This file contains tests functions to test the module polygon.py
"""

import numpy as np
import pytest

from shapepy.analytic.helper import check_shifted_polynomial
from shapepy.analytic.polynomial import (
    Polynomial,
    find_rational_roots,
    find_roots,
)


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
@pytest.mark.dependency(depends=["test_degree"])
def test_simplify():
    coefs = [1, 2, 3, 0]
    polya = Polynomial(coefs)
    assert polya.degree == 2
    assert tuple(polya) == (1, 2, 3)


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

    assert poly(1.0) == 6


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

    poly = Polynomial([0])
    assert poly == 0
    poly = Polynomial([1])
    assert poly == 1
    poly = Polynomial([2])
    assert poly == 2


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
@pytest.mark.dependency(depends=["test_derivate"])
def test_integrate():
    coefs = [3, 5, -4, 3, 2]
    poly = Polynomial(coefs)
    test = poly.integrate(0)
    assert test == poly

    for times in range(5):
        test = poly.integrate(times)
        test = test.derivate(times)
        assert test == poly


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_derivate", "test_integrate"])
def test_definite_integral():
    coefs = [3, 6, -12, 8, 10]
    poly = Polynomial(coefs)
    test = poly.defintegral(0, 3)
    assert test == 576


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
@pytest.mark.timeout(3)
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
@pytest.mark.timeout(3)
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
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_shift():
    poly = Polynomial([-1, 3, -3, 1])  # (x-1)^3
    assert poly.shift(-1) == Polynomial([0, 0, 0, 1])  # x^3

    poly = Polynomial([1, 8, 24, 32, 16])  # (1+2*x)^4
    assert poly.shift(1 / 2) == Polynomial([0, 0, 0, 0, 16])  # (2*x)^4


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_scale():
    poly = Polynomial([1, 2, 3])  # 1 + 2*x + 3*x^2
    assert poly.scale(2) == Polynomial([1, 4, 12])


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare", "test_simplify"])
def test_divide_poly():
    x = Polynomial([0, 1])
    poly = 1 - x  # 1 - x
    qoly, roly = divmod(poly, poly)
    assert qoly == 1
    assert roly == 0

    poly = (1 - x) ** 2  # 1 - 2*x + x^2
    assert poly % (1 - x) == 0
    assert poly // (1 - x) == (1 - x)
    assert poly / (1 - x) == (1 - x)

    poly = 2 * x * (1 - x)
    assert poly / 2 == x * (1 - x)


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_divide_poly"])
def test_find_analytic_roots():
    ntests = 10
    for degree in range(1, 3):
        for _ in range(ntests):
            good_roots = np.random.randint(-20, 20, degree)
            good_roots = tuple(sorted(map(int, good_roots)))
            poly = Polynomial.from_roots(good_roots)
            test_roots = find_rational_roots(poly)
            assert len(test_roots) == degree
            for test, good in zip(test_roots, good_roots):
                assert test == good


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(
    depends=["test_divide_poly", "test_find_analytic_roots"]
)
def test_find_roots():
    poly = Polynomial([1, -1])  # 1 - x
    roots = find_roots(poly)
    assert roots == (1,)
    poly = Polynomial([1, 1])  # 1 + x
    roots = find_roots(poly)
    assert roots == (-1,)

    poly = Polynomial([1, 0, 1])  # 1 + x^2
    roots = find_roots(poly)
    assert roots == tuple()
    poly = Polynomial([1, 0, -1])  # 1 - x^2
    roots = find_roots(poly)
    assert roots == (-1, 1)
    poly = Polynomial([-1, 0, 1])  # 1 - x^2
    roots = find_roots(poly)
    assert roots == (-1, 1)

    poly = Polynomial([3, -4, 1])  # 3 - 4*x + x^2
    roots = find_roots(poly)
    assert roots == (1, 3)
    poly = Polynomial([1, -4, 4])  # 1 - 4*x + 4*x^2
    roots = find_roots(poly)
    assert roots == (0.5, 0.5)
    poly = Polynomial([2, -1, -2, 1])  # 2 - x - 2*x + x^3
    roots = find_roots(poly)
    assert roots == (-1, 1, 2)

    poly = Polynomial([1, -2, 1])  # (x-1)^2
    roots = find_roots(poly)
    assert roots == (1, 1)
    poly = Polynomial([-1, 3, -3, 1])  # (x-1)^3
    roots = find_roots(poly)
    assert roots == (1, 1, 1)
    poly = Polynomial([-16, 48, -36, 8])  # 4*(x-2)^2*(2x-1)
    roots = find_roots(poly)
    assert roots == (0.5, 2, 2)
    poly = Polynomial([24, -28, 8])  # 4*(2x-3)*(x-2)
    roots = find_roots(poly)
    assert roots == (3 / 2, 2)
    poly = Polynomial([-344, 294, -84, 8])
    roots = find_roots(poly)
    assert roots == (4,)

    poly = Polynomial([-5, 13, -9, 2])
    roots = find_roots(poly)
    assert len(roots) == 1
    assert abs(roots[0] - 0.601839048370279232474813636733) < 1e-9
    poly = Polynomial([-4, 4, -12, 8])
    roots = find_roots(poly)
    assert len(roots) == 1
    assert abs(roots[0] - 1.398160951629720767525186363267) < 1e-9
    coefs = [0.24576122535081, -1.3132004733713565, 8]
    poly = Polynomial(coefs)
    roots = find_roots(poly)
    assert len(roots) == 0


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_evaluate_natural"])
def test_shift_polynomials():
    polya = Polynomial([1])
    param = check_shifted_polynomial(polya, polya)
    assert param is None
    polya = Polynomial([1, 1])
    param = check_shifted_polynomial(polya, polya)
    assert param == 0

    polyb = Polynomial([2])
    param = check_shifted_polynomial(polya, polyb)
    assert param is None
    polyb = Polynomial([2, 2])
    param = check_shifted_polynomial(polya, polyb)
    assert param is None

    polya = Polynomial([0, 0, 1])  # x^2
    polyb = Polynomial([1, -2, 1])  # (x-1)^2
    param = check_shifted_polynomial(polya, polyb)
    assert param == 1

    xpoly = Polynomial([0, 1])
    for degree in range(1, 6):
        polya = Polynomial([0] * degree + [1])
        for good in (-2, -1, 0, 1, 2):
            polyb = (xpoly - good) ** degree
            test = check_shifted_polynomial(polya, polyb)
            assert test == good


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
    assert str(poly) == "-1"
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
        "test_simplify",
        "test_evaluate_natural",
        "test_keep_type",
        "test_compare",
        "test_derivate",
        "test_integrate",
        "test_definite_integral",
        "test_evaluate_derivate",
        "test_add",
        "test_sub",
        "test_mult",
        "test_pow",
        "test_shift",
        "test_scale",
        "test_divide_poly",
        "test_find_roots",
        "test_shift_polynomials",
    ]
)
def test_end():
    pass
