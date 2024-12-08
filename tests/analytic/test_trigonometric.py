"""
This file contains tests functions to test the module polygon.py
"""

import math

import numpy as np
import pytest
import sympy as sp

from shapepy.analytic.trigonometric import Trignomial


@pytest.mark.order(3)
@pytest.mark.dependency()
def test_begin():
    pass


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin"])
def test_build():
    Trignomial([1])  # p(x) = 1
    Trignomial([1, 1])  # p(x) = 1 + sin(2*pi*x)
    Trignomial([1, 2])  # p(x) = 1 + 2*sin(2*pi*x)
    Trignomial([1, 3, 2])  # 1 + 3*sin(2*pi*x) + 2*cos(2*pi*x)
    Trignomial([1.0, 2.0, 3.0])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin"])
def test_degree():
    assert Trignomial([1]).pmax == 0
    assert Trignomial([1, 1]).pmax == 1
    assert Trignomial([1, 2]).pmax == 1
    assert Trignomial([1, 3, 2]).pmax == 1
    assert Trignomial([1.0, 2.0, 3.0]).pmax == 1
    assert Trignomial([1, 3, 2, 4, 5]).pmax == 2


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_degree"])
def test_simplify():
    coefs = [1, 2, 3, 0]
    polya = Trignomial(coefs)
    assert polya.pmax == 1
    assert tuple(polya) == (1, 2, 3)


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build"])
def test_evaluate_sincos():
    nodes = np.linspace(0, 1, 129)
    for node in nodes:
        angle = node * 2 * np.pi
        sin, cos = Trignomial.sincos(node)
        assert abs(sin - np.sin(angle)) < 1e-9
        assert abs(cos - np.cos(angle)) < 1e-9


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build", "test_evaluate_sincos"])
def test_evaluate_natural():
    trig = Trignomial([1])  # p(x) = 1
    assert trig.eval(0) == 1
    assert trig.eval(1) == 1
    assert trig.eval(2) == 1
    assert trig.eval(1.0) == 1

    trig = Trignomial([1, 2])  # p(x) = 1 + 2*sin(2*pi*x)
    assert trig.eval(0) == 1
    assert trig.eval(1) == 1
    assert trig.eval(2) == 1
    assert trig.eval(0.0) == 1
    assert trig.eval(1.0) == 1

    trig = Trignomial([1, 2, 3])  # p(x) = 1 + 2*sin(2*pi*x) + 3*cos(2*pi*x)
    assert trig.eval(0) == 4
    assert trig.eval(1) == 4
    assert trig.eval(2) == 4
    assert trig.eval(0.0) == 4
    assert trig.eval(1.0) == 4

    assert trig(1.0) == 4


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=["test_evaluate_natural", "test_evaluate_derivate", "test_degree"]
)
def test_keep_type():
    nodes = np.linspace(-5, 5, 41)

    coefs = [3, 5, -4, 3, 2]
    trig = Trignomial(coefs)
    for node in nodes:
        val = trig.eval(node, 0)
        assert val == int(val)

    coefs = [3.0, 5.0, -4.0, 3.0, 2.0]
    trig = Trignomial(coefs)
    for deriv in range(5):
        for node in nodes:
            val = trig.eval(node, deriv)
            assert isinstance(val, float)

    from fractions import Fraction

    one = Fraction(1)
    coefs = [3 * one, 5 * one, -4 * one, 3 * one, 2 * one]
    trig = Trignomial(coefs)

    for node in nodes:
        val = trig.eval(node, 0)
        assert isinstance(val, Fraction)


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_degree"])
def test_compare():
    coefs = [3, 5, -4, 3, 2]
    polya = Trignomial(coefs)
    coefs = [3, 5, -4, 3, 2, 7]
    polyb = Trignomial(coefs)
    assert polya != polyb

    coefs = [3, 5, -4, 3, 2]
    polya = Trignomial(coefs)
    coefs = [3, 5, -4, 3, 2]
    polyb = Trignomial(coefs)
    assert polya == polyb

    coefs = [3, 5, -4, 3, 2]
    polya = Trignomial(coefs)
    coefs = [3, -3, -4, 3, 2]
    polyb = Trignomial(coefs)
    assert polya != polyb

    trig = Trignomial([0])
    assert trig == 0
    trig = Trignomial([1])
    assert trig == 1
    trig = Trignomial([2])
    assert trig == 2


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_add():
    polya = Trignomial([1, 3])
    assert polya + 3 == Trignomial([4, 3])
    assert 3 + polya == Trignomial([4, 3])

    polya = Trignomial([1, 2, 3])
    polyb = Trignomial([3, 2, 1])
    assert polya + polyb == Trignomial([4, 4, 4])

    polya = Trignomial([1, 2, 3])
    polyb = Trignomial([3, 2, 1, 7])
    assert polya + polyb == Trignomial([4, 4, 4, 7])

    polya = Trignomial([1, 2, 3, 7])
    polyb = Trignomial([3, 2, 1])
    assert polya + polyb == Trignomial([4, 4, 4, 7])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_compare", "test_add"])
def test_sub():
    polya = Trignomial([1, 3])
    assert polya - 3 == Trignomial([-2, 3])
    assert 3 - polya == Trignomial([2, -3])


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare", "test_add"])
def test_mult():
    sint = Trignomial([0, 1, 0])
    cost = Trignomial([0, 0, 1])
    sin2t = Trignomial([0, 0, 0, 1, 0])
    cos2t = Trignomial([0, 0, 0, 0, 1])

    assert sint * sint + cost * cost == 1
    assert sin2t * sin2t + cos2t * cos2t == 1
    assert 2 * sint * cost == sin2t
    assert cost * cost - sint * sint == cos2t
    assert 1 + cos2t == 2 * cost * cost
    assert 1 - cos2t == 2 * sint * sint


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare", "test_mult"])
def test_pow():

    sint = Trignomial([0, 1, 0])
    cost = Trignomial([0, 0, 1])
    sin2t = Trignomial([0, 0, 0, 1, 0])
    cos2t = Trignomial([0, 0, 0, 0, 1])

    assert sint**0 == 1
    assert cost**0 == 1
    assert sin2t**0 == 1
    assert cos2t**0 == 1
    assert sint**1 == sint
    assert cost**1 == cost
    assert sin2t**1 == sin2t
    assert cos2t**1 == cos2t

    assert sint**2 + cost**2 == 1
    assert sin2t**2 + cos2t**2 == 1
    assert 2 * sint * cost == sin2t
    assert cost**2 - sint**2 == cos2t
    assert 1 + cos2t == 2 * cost**2
    assert 1 - cos2t == 2 * sint**2


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_derivate():
    coefs = [3, 5, -4, 3, 2]
    trig = Trignomial(coefs)
    test = trig.derivate(0)
    assert test == trig

    test = trig.derivate(1)
    good = 2 * sp.pi * Trignomial([0, 4, 5, -4, 6])
    assert test != trig
    assert test == good


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_derivate"])
def test_integrate():
    coefs = [0, 5, -4, 3, 2]
    trig = Trignomial(coefs)
    test = trig.integrate(0)
    assert test == trig

    for times in range(5):
        test = trig.derivate(times)
        test = test.integrate(times)
        assert test == trig


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_evaluate_natural", "test_derivate"])
def test_evaluate_derivate():
    trig = Trignomial([1])  # p(x) = 1
    assert trig.eval(0, 1) == 0
    assert trig.eval(1, 1) == 0
    assert trig.eval(2, 1) == 0
    assert trig.eval(1.0, 1) == 0
    assert trig.eval(1, 2) == 0

    trig = Trignomial([1, 2])  # p(x) = 1 + 2*sin(2*pi*x)
    assert trig.eval(0, 1) == 2 * Trignomial.TAU
    assert trig.eval(1, 1) == 2 * Trignomial.TAU
    assert trig.eval(2, 1) == 2 * Trignomial.TAU
    assert trig.eval(0.0, 1) == 2 * Trignomial.TAU
    assert trig.eval(1.0, 1) == 2 * Trignomial.TAU
    assert trig.eval(2, 2) == 0
    assert trig.eval(0.0, 2) == 0

    trig = Trignomial([1, 2, 3])  # p(x) = 1 + 2*sin(w*x) + 3*cos(w*x)
    assert trig.eval(0, 1) == 2 * Trignomial.TAU
    assert trig.eval(1, 1) == 2 * Trignomial.TAU
    assert trig.eval(2, 1) == 2 * Trignomial.TAU
    assert trig.eval(0.0, 1) == 2 * Trignomial.TAU
    assert trig.eval(1.0, 1) == 2 * Trignomial.TAU
    assert trig.eval(2, 2) == -3 * Trignomial.TAU**2
    assert trig.eval(0.0, 2) == -3 * Trignomial.TAU**2
    assert trig.eval(2, 3) == -2 * Trignomial.TAU**3
    assert trig.eval(0.0, 3) == -2 * Trignomial.TAU**3


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_shift():
    trig = Trignomial([0, 0, 1])  # cost
    assert trig.shift(0.25) == Trignomial([0, 1])  # sint


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_scale():
    trig = Trignomial([1, 2, 3], 1)
    assert trig.scale(2) == Trignomial([1, 2, 3], 2)


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare", "test_simplify"])
def test_divide_scalar():
    sint = Trignomial([0, 1, 0])
    cost = Trignomial([0, 0, 1])

    qrig, rrig = divmod(sint, 1)
    assert qrig == sint
    assert rrig == 0

    qrig, rrig = divmod(sint, 2)
    assert qrig == sint / 2
    assert rrig == 0

    qrig, rrig = divmod(cost, 1)
    assert qrig == cost
    assert rrig == 0

    assert sint % 2 == 0
    assert cost % 2 == 0
    assert sint // 2 == Trignomial([0, 1 / 2, 0])
    assert cost // 2 == Trignomial([0, 0, 1 / 2])
    assert sint / 2 == Trignomial([0, 1 / 2, 0])
    assert cost / 2 == Trignomial([0, 0, 1 / 2])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_divide_scalar"])
def test_divide_zero():
    numer = Trignomial([1])
    denom = Trignomial([0])
    with pytest.raises(ZeroDivisionError):
        numer / denom


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_divide_scalar"])
def test_divide_pmax1():
    sint = Trignomial([0, 1, 0])
    cost = Trignomial([0, 0, 1])

    assert sint % sint == 0
    assert cost % cost == 0
    assert (sint + cost) % (sint + cost) == 0
    assert (sint - cost) % (sint - cost) == 0
    assert (-sint + cost) % (-sint + cost) == 0
    assert (-sint - cost) % (-sint - cost) == 0
    assert sint // sint == 1
    assert cost // cost == 1
    assert (sint + cost) // (sint + cost) == 1
    assert (sint - cost) // (sint - cost) == 1
    assert (-sint + cost) // (-sint + cost) == 1
    assert (-sint - cost) // (-sint - cost) == 1


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_divide_pmax1"])
def test_divide_random_pmax1():
    sint = Trignomial([0, 1, 0])
    cost = Trignomial([0, 0, 1])

    for _ in range(200):
        a, b, c, d = np.random.randint(-10, 11, 4)
        if not (a or b or c):
            continue
        denom = a * sint + b * cost + c
        numer = d * denom
        quot, rest = divmod(numer, denom)
        assert numer == quot * denom + rest
        assert quot == d
        assert rest == 0

    for _ in range(200):
        a, b, c = np.random.randint(-10, 11, 3)
        numer = a * sint + b * cost + c
        a, b, c = np.random.randint(-10, 11, 3)
        if not (a or b or c):
            continue
        denom = a * sint + b * cost + c
        quot, rest = divmod(numer, denom)
        assert numer == quot * denom + rest
        assert rest.pmax <= denom.pmax


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_divide_random_pmax1"])
def test_divmod_sum():
    ntests = 5
    for pmaxa in range(11):
        for pmaxb in range(5):
            for _ in range(ntests):
                coefsa = np.random.randint(-10, 10, 2 * pmaxa + 1)
                while True:
                    coefsb = np.random.randint(-10, 10, 2 * pmaxb + 1)
                    if any(coefsb):
                        break
                numer = Trignomial(map(int, coefsa))
                denom = Trignomial(map(int, coefsb))
                quot, rest = divmod(numer, denom)
                assert numer == denom * quot + rest
                if denom.pmax <= numer.pmax:
                    assert numer.pmax == denom.pmax + quot.pmax


@pytest.mark.order(3)
@pytest.mark.timeout(5)
@pytest.mark.dependency(depends=["test_divmod_sum"])
def test_divide_random_mult():
    ntests = 5
    for pmaxa in range(5):
        for pmaxb in range(5):
            for _ in range(ntests):
                while True:
                    coefsa = np.random.randint(-5, 6, 2 * pmaxa + 1)
                    if any(coefsa):
                        break
                while True:
                    coefsb = np.random.randint(-5, 6, 2 * pmaxb + 1)
                    if any(coefsb):
                        break
                coefsa = tuple(map(int, coefsa))
                coefsb = tuple(map(int, coefsb))
                triga = Trignomial(coefsa)
                trigb = Trignomial(coefsb)
                produ = triga * trigb

                quot, rest = divmod(produ, triga)
                assert produ == triga * quot + rest
                assert rest == 0
                assert quot == trigb
                quot, rest = divmod(produ, trigb)
                assert produ == trigb * quot + rest
                assert rest == 0
                assert quot == triga


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build"])
def test_print():
    trig = Trignomial([0])
    assert str(trig) == "0"
    trig = Trignomial([0, 0])
    assert str(trig) == "0"
    trig = Trignomial([0, 0, 0])
    assert str(trig) == "0"
    trig = Trignomial([1])
    assert str(trig) == "1"
    trig = Trignomial([1, 1])
    assert str(trig) == "1 + sin(tau*t)"
    trig = Trignomial([1, 1, 1])
    assert str(trig) == "1 + sin(tau*t) + cos(tau*t)"
    trig = Trignomial([1, 0, 1])
    assert str(trig) == "1 + cos(tau*t)"
    trig = Trignomial([0, 0, 1])
    assert str(trig) == "cos(tau*t)"
    trig = Trignomial([-1])
    assert str(trig) == "-1"
    trig = Trignomial([-1, 1])
    assert str(trig) == "- 1 + sin(tau*t)"
    trig = Trignomial([1, -1, 1])
    assert str(trig) == "1 - sin(tau*t) + cos(tau*t)"
    trig = Trignomial([1, 0, 1])
    assert str(trig) == "1 + cos(tau*t)"
    trig = Trignomial([1, 2, 3])
    assert str(trig) == "1 + 2 * sin(tau*t) + 3 * cos(tau*t)"
    repr(trig)

    trig = Trignomial([1, 2, 3, 4, 5, 6, 7.9, 9])
    str(trig)
    repr(trig)


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_integrate"])
def test_definite_integrate():
    # Integrate constant
    trig = Trignomial([0])
    assert trig.defintegral(0, 1) == 0
    for _ in range(100):  # ntests
        const, lower, upper = np.random.randint(-10, 10, 3)
        trig = Trignomial([const])
        assert trig.defintegral(lower, upper) == (upper - lower) * const

    # Integrate linear
    for _ in range(100):  # ntests
        freq = np.random.randint(1, 10)
        omega = freq * 2 * np.pi
        const, lower, upper = np.random.randint(-10, 10, 3)
        sincoef, coscoef = np.random.randint(-10, 10, 2)
        trig = Trignomial([const, sincoef, coscoef], freq)
        good = const * (upper - lower)
        good += (
            sincoef * (np.cos(omega * lower) - np.cos(omega * upper)) / omega
        )
        good += (
            coscoef * (np.sin(omega * upper) - np.sin(omega * lower)) / omega
        )
        test = trig.defintegral(lower, upper)
        assert abs(test - good) < 1e-9


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
        "test_evaluate_derivate",
        "test_add",
        "test_sub",
        "test_mult",
        "test_pow",
        "test_shift",
        "test_scale",
        "test_divide_scalar",
        "test_divide_zero",
        "test_divmod_sum",
        "test_divide_pmax1",
        "test_divide_random_pmax1",
        "test_divide_random_mult",
        "test_definite_integrate",
    ]
)
def test_end():
    pass
