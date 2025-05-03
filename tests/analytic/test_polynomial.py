"""
This file contains tests functions to test the module polygon.py
"""

from numbers import Integral, Rational, Real

import pytest

from shapepy import default
from shapepy.analytic.elementar import polynomial
from shapepy.bool1d import EmptyR1, IntervalR1, WholeR1


@pytest.mark.order(20)
@pytest.mark.dependency(
    depends=[
        "tests/bool1d/test_compare.py::test_all",
        "tests/bool1d/test_contains.py::test_all",
        "tests/bool1d/test_boolean.py::test_all",
        "tests/bool1d/test_transform.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_begin"])
def test_build():
    polynomial([1])  # p(t) = 1
    polynomial([1, 1])  # p(t) = 1 + t
    polynomial([1, 2])  # p(t) = 1 + 2*t
    polynomial([1, 3, 2])  # 1 + 3*t + 2*t^2
    polynomial([1.0, 2.0, 3.0])


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_build"])
def test_evaluate_natural():
    poly = polynomial([1])  # p(t) = 1
    assert poly.eval(0) == 1
    assert poly.eval(1) == 1
    assert poly.eval(2) == 1
    assert poly.eval(1.0) == 1

    poly = polynomial([1, 2])  # p(t) = 1 + 2*t
    assert poly.eval(0) == 1
    assert poly.eval(1) == 3
    assert poly.eval(2) == 5
    assert poly.eval(0.0) == 1
    assert poly.eval(1.0) == 3

    poly = polynomial([1, 2, 3])  # p(t) = 1 + 2*t + 3*t^2
    assert poly.eval(0) == 1
    assert poly.eval(1) == 6
    assert poly.eval(2) == 17
    assert poly.eval(0.0) == 1
    assert poly.eval(1.0) == 6

    assert poly(1.0) == 6


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_build", "test_evaluate_natural"])
def test_keep_type():
    coefs = [3, 5, -4, 3, 2]
    poly = polynomial(coefs)
    for deriv in range(0, 4):
        for node in range(-5, 6):
            val = poly.eval(node, deriv)
            assert isinstance(val, Integral)
        for node in range(-5, 6):
            val = poly.eval(float(node), deriv)
            assert isinstance(val, Real)

    coefs = [3.0, 5.0, -4.0, 3.0, 2.0]
    poly = polynomial(coefs)
    for deriv in range(0, 4):
        for node in range(-5, 6):
            val = poly.eval(node, deriv)
            assert isinstance(val, Real)
        for node in range(-5, 6):
            val = poly.eval(float(node), deriv)
            assert isinstance(val, Real)

    from fractions import Fraction

    one = Fraction(1)
    coefs = [3 * one, 5 * one, -4 * one, 3 * one, 2 * one]
    poly = polynomial(coefs)
    for deriv in range(0, 4):
        for node in range(-5, 6):
            val = poly.eval(node, deriv)
            assert isinstance(val, Rational)
        for node in range(-5, 6):
            val = poly.eval(float(node), deriv)
            assert isinstance(val, Real)


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_build", "test_evaluate_natural"])
def test_compare():
    coefs = [3, 5, -4, 3, 2]
    polya = polynomial(coefs)
    coefs = [3, 5, -4, 3, 2, 7]
    polyb = polynomial(coefs)
    assert polya != polyb

    coefs = [3, 5, -4, 3, 2]
    polya = polynomial(coefs)
    coefs = [3, 5, -4, 3, 2]
    polyb = polynomial(coefs)
    assert polya == polyb

    coefs = [3, 5, -4, 3, 2]
    polya = polynomial(coefs)
    coefs = [3, -3, -4, 3, 2]
    polyb = polynomial(coefs)
    assert polya != polyb

    poly = polynomial([0])
    assert poly == 0
    poly = polynomial([1])
    assert poly == 1
    poly = polynomial([2])
    assert poly == 2


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_compare"])
def test_derivate():
    coefs = [3, 5, -4, 3, 2]
    poly = polynomial(coefs)
    test = poly.derivate(0)
    assert test == poly

    test = poly.derivate(1)
    good = polynomial([5, -8, 9, 8])
    assert test != poly
    assert test == good

    test = poly.derivate(2)
    good = polynomial([-8, 18, 24])
    assert test != poly
    assert test == good


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_evaluate_natural", "test_derivate"])
def test_evaluate_derivate():
    poly = polynomial([1])  # p(t) = 1
    assert poly.eval(0, 1) == 0
    assert poly.eval(1, 1) == 0
    assert poly.eval(2, 1) == 0
    assert poly.eval(1.0, 1) == 0
    assert poly.eval(1, 2) == 0

    poly = polynomial([1, 2])  # p(t) = 1 + 2*t
    assert poly.eval(0, 1) == 2
    assert poly.eval(1, 1) == 2
    assert poly.eval(2, 1) == 2
    assert poly.eval(0.0, 1) == 2
    assert poly.eval(1.0, 1) == 2
    assert poly.eval(2, 2) == 0
    assert poly.eval(0.0, 2) == 0

    poly = polynomial([1, 2, 3])  # p(t) = 1 + 2*t + 3*t^2
    assert poly.eval(0, 1) == 2
    assert poly.eval(1, 1) == 8
    assert poly.eval(2, 1) == 14
    assert poly.eval(0.0, 1) == 2
    assert poly.eval(1.0, 1) == 8
    assert poly.eval(2, 2) == 6
    assert poly.eval(0.0, 2) == 6
    assert poly.eval(2, 3) == 0
    assert poly.eval(0.0, 3) == 0


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_compare"])
def test_add():
    polya = polynomial([1, 3])
    assert polya + 3 == polynomial([4, 3])
    assert 3 + polya == polynomial([4, 3])

    polya = polynomial([1, 2, 3])
    polyb = polynomial([3, 2, 1])
    assert polya + polyb == polynomial([4, 4, 4])

    polya = polynomial([1, 2, 3])
    polyb = polynomial([3, 2, 1, 7])
    assert polya + polyb == polynomial([4, 4, 4, 7])

    polya = polynomial([1, 2, 3, 7])
    polyb = polynomial([3, 2, 1])
    assert polya + polyb == polynomial([4, 4, 4, 7])

    assert polya - polya == 0
    assert polyb - polyb == 0
    assert polya - polyb == polynomial([-2, 0, 2, 7])


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_compare"])
def test_sub():
    polya = polynomial([1, 3])
    assert polya - 3 == polynomial([-2, 3])
    assert 3 - polya == polynomial([2, -3])


@pytest.mark.order(20)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_mul():
    polya = polynomial([1, 3])
    assert 4 * polya == polynomial([4, 12])
    assert polya * 4 == polynomial([4, 12])

    polya = polynomial([1, 1])
    polyb = polynomial([1, 1])
    assert polya * polyb == polynomial([1, 2, 1])

    polya = polynomial([1, 1])
    polyb = polynomial([1, 2, 1])
    assert polya * polyb == polynomial([1, 3, 3, 1])

    polya = polynomial([1, 2, 1])
    polyb = polynomial([1, 2, 1])
    assert polya * polyb == polynomial([1, 4, 6, 4, 1])

    polya = polynomial([1, 1])
    polyb = polynomial([1, 3, 3, 1])
    assert polya * polyb == polynomial([1, 4, 6, 4, 1])


@pytest.mark.order(20)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_div():
    assert polynomial([4, 12]) / 4 == polynomial([1, 3])
    assert polynomial([1, 1]) / 1 == polynomial([1, 1])


@pytest.mark.order(20)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_shift():
    poly = polynomial([-1, 3, -3, 1])  # (t-1)^3
    good = polynomial([0, 0, 0, 1])  # t^3
    test = poly.shift(-1)
    assert test == good

    poly = polynomial([1, 8, 24, 32, 16])  # (1+2*t)^4
    good = polynomial([0, 0, 0, 0, 16])
    test = poly.shift(1 / 2)  # (2*t)^4
    assert test == good

    nodes = tuple(i / 16 for i in range(4 * 16 + 1))
    even_poly = polynomial([2, 0, -4, 0, 6, 0, -8])
    odd_poly = polynomial([0, 1, 0, -3, 0, 5, 0, -7])
    for shi_val in (1, 0.5, 0.25, 0.125):
        for ori_trig in (even_poly, odd_poly):
            shi_trig = ori_trig.shift(shi_val)
            for node in nodes:
                good = ori_trig.eval(node - shi_val)
                test = shi_trig.eval(node)
                assert abs(test - good) < 1e-9


@pytest.mark.order(20)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_scale():
    oripoly = polynomial([1, 2, 3])  # 1 + 2*t + 3*t^2
    scapoly = oripoly.scale(2)
    assert scapoly == polynomial([1, 4, 12])

    nodes = tuple(i / 16 for i in range(4 * 16 + 1))
    for node in nodes:
        assert scapoly.eval(node / 2) == oripoly.eval(node)


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_build"])
def test_print():
    poly = polynomial([0])
    assert str(poly) == "0"
    poly = polynomial([0, 0])
    assert str(poly) == "0"
    poly = polynomial([0, 0, 0])
    assert str(poly) == "0"
    poly = polynomial([1])
    assert str(poly) == "1"
    poly = polynomial([1, 1])
    # assert str(poly) == "1 + t"
    poly = polynomial([1, 1, 1])
    # assert str(poly) == "1 + t + t^2"
    poly = polynomial([1, 0, 1])
    # assert str(poly) == "1 + t^2"
    poly = polynomial([0, 0, 1])
    # assert str(poly) == "t^2"
    poly = polynomial([-1])
    assert str(poly) == "-1"
    poly = polynomial([-1, 1])
    # assert str(poly) == "- 1 + t"
    poly = polynomial([1, -1, 1])
    # assert str(poly) == "1 - t + t^2"
    poly = polynomial([1, 0, 1])
    # assert str(poly) == "1 + t^2"
    poly = polynomial([1, 2, 3])
    # assert str(poly) == "1 + 2 * t + 3 * t^2"
    repr(poly)


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_build"])
def test_divide_zero():
    numer = polynomial([1])
    denom = polynomial([0])
    with pytest.raises(ZeroDivisionError):
        numer / denom


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_build"])
def test_wrong_type():
    assert polynomial([0]) != "asd"
    with pytest.raises(ValueError):
        polynomial([0]) + "asd"
    with pytest.raises(ValueError):
        "asd" + polynomial([0])
    with pytest.raises(TypeError):
        polynomial([0]) - "asd"
    with pytest.raises(ValueError):
        "asd" - polynomial([0])


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_build"])
def test_definite_integral():
    domain = IntervalR1(0, 1)
    for degree in range(10):
        poly = polynomial([0] * degree + [1])
        good = 1 / (1 + degree)
        test = poly.integrate(domain)
        assert abs(test - good) < 1e-5

    domain = IntervalR1(-1, -0.5) | IntervalR1(0.5, 1)
    for degree in range(10):
        poly = polynomial([0] * degree + [1])
        good = 0 if degree % 2 else (2 - 0.5**degree) / (1 + degree)
        test = poly.integrate(domain)
        assert abs(test - good) < 1e-5

    poly = polynomial([1, 2, 3])
    assert poly.integrate(WholeR1()) == default.POSINF
    assert poly.integrate(EmptyR1()) == 0

    # Cauchy integral value
    poly = polynomial([0, 2, 0, -4])
    assert poly.integrate(WholeR1()) == 0
    assert poly.integrate(EmptyR1()) == 0


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_build"])
def test_find_roots():
    poly = polynomial([0])
    assert poly.where(0, EmptyR1()) == EmptyR1()
    assert poly.where(0, WholeR1()) == WholeR1()
    assert poly.where(0) == WholeR1()

    poly = polynomial([-1, 1])
    assert poly.where(0) == {1}
    poly = polynomial([-3, 1])
    assert poly.where(0) == {3}

    poly = polynomial([1, -2, 1])
    assert poly.where(0) == {1}
    poly = polynomial([-1, 3, -3, 1])
    assert poly.where(0) == {1}

    poly = polynomial([3, -4, 1])
    assert poly.where(0) == {1, 3}

    poly = polynomial([-2, 0, 1])
    assert poly.where(0) == {-default.sqrt(2), +default.sqrt(2)}


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_build"])
def test_image():
    poly = polynomial([1])
    assert poly.image() == {1}

    poly = polynomial([1, 1])
    assert poly.image() == WholeR1()

    interv = IntervalR1(-1, 1)
    assert poly.image(interv) == [0, 2]

    poly = polynomial([1, 0, -1])
    assert poly.image() == [default.NEGINF, 1]
    assert poly.image(interv) == [0, 1]

    poly = polynomial([1, 0, 1])
    assert poly.image() == [1, default.POSINF]
    assert poly.image(interv) == [1, 2]


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_build"])
def test_section():
    poly = polynomial([1])

    assert poly.section() == poly
    assert id(poly.section()) != id(poly)

    domain = (-1, 1)
    test = poly.section(domain)
    good = polynomial([1], domain)
    assert test == good


@pytest.mark.order(20)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_build",
        "test_evaluate_natural",
        "test_keep_type",
        "test_compare",
        "test_derivate",
        "test_evaluate_derivate",
        "test_add",
        "test_sub",
        "test_mul",
        "test_div",
        "test_shift",
        "test_scale",
        "test_print",
        "test_divide_zero",
        "test_wrong_type",
        "test_definite_integral",
        "test_find_roots",
        "test_image",
        "test_section",
    ]
)
def test_all():
    pass
