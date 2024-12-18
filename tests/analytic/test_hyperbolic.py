"""
This file contains tests functions to test the module polygon.py
"""

import math

import numpy as np
import pytest
import sympy as sp

from shapepy.analytic.hyperbolic import Hypernomial


@pytest.mark.order(3)
@pytest.mark.dependency()
def test_begin():
    pass


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin"])
def test_build():
    Hypernomial([1])  # p(x) = 1
    Hypernomial([1, 1])  # p(x) = 1 + sin(2*pi*x)
    Hypernomial([1, 2])  # p(x) = 1 + 2*sin(2*pi*x)
    Hypernomial([1, 3, 2])  # 1 + 3*sin(2*pi*x) + 2*cos(2*pi*x)
    Hypernomial([1.0, 2.0, 3.0])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin"])
def test_degree():
    assert Hypernomial([1]).pmax == 0
    assert Hypernomial([1, 1]).pmax == 1
    assert Hypernomial([1, 2]).pmax == 1
    assert Hypernomial([1, 3, 2]).pmax == 1
    assert Hypernomial([1.0, 2.0, 3.0]).pmax == 1
    assert Hypernomial([1, 3, 2, 4, 5]).pmax == 2


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_degree"])
def test_simplify():
    coefs = [1, 2, 3, 0]
    polya = Hypernomial(coefs)
    assert polya.pmax == 1
    assert tuple(polya) == (1, 2, 3)


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build"])
def test_evaluate_natural():
    trig = Hypernomial([1])  # p(x) = 1
    assert trig.eval(0) == 1
    assert trig.eval(1) == 1
    assert trig.eval(2) == 1
    assert trig.eval(1.0) == 1

    trig = Hypernomial([1, 2])  # p(x) = 1 + 2*sinh(x)
    assert trig.eval(0) == 1
    assert trig.eval(1) == 1 + 2 * math.sinh(1)
    assert trig.eval(2) == 1 + 2 * math.sinh(2)
    assert trig.eval(0.0) == 1
    assert trig.eval(1.0) == 1 + 2 * math.sinh(1)

    trig = Hypernomial([1, 2, 3])  # p(x) = 1 + 2*sinh(x) + 3*cos(x)
    assert trig.eval(0) == 4
    assert trig.eval(1) == 1 + 2 * math.sinh(1) + 3 * math.cosh(1)
    assert trig.eval(2) == 1 + 2 * math.sinh(2) + 3 * math.cosh(2)
    assert trig.eval(0.0) == 4
    assert trig.eval(1.0) == 1 + 2 * math.sinh(1) + 3 * math.cosh(1)

    assert trig(1.0) == 1 + 2 * math.sinh(1) + 3 * math.cosh(1)


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_degree"])
def test_compare():
    coefs = [3, 5, -4, 3, 2]
    polya = Hypernomial(coefs)
    coefs = [3, 5, -4, 3, 2, 7]
    polyb = Hypernomial(coefs)
    assert polya != polyb

    coefs = [3, 5, -4, 3, 2]
    polya = Hypernomial(coefs)
    coefs = [3, 5, -4, 3, 2]
    polyb = Hypernomial(coefs)
    assert polya == polyb

    coefs = [3, 5, -4, 3, 2]
    polya = Hypernomial(coefs)
    coefs = [3, -3, -4, 3, 2]
    polyb = Hypernomial(coefs)
    assert polya != polyb

    trig = Hypernomial([0])
    assert trig == 0
    trig = Hypernomial([1])
    assert trig == 1
    trig = Hypernomial([2])
    assert trig == 2


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_add():
    polya = Hypernomial([1, 3])
    assert polya + 3 == Hypernomial([4, 3])
    assert 3 + polya == Hypernomial([4, 3])

    polya = Hypernomial([1, 2, 3])
    polyb = Hypernomial([3, 2, 1])
    assert polya + polyb == Hypernomial([4, 4, 4])

    polya = Hypernomial([1, 2, 3])
    polyb = Hypernomial([3, 2, 1, 7])
    assert polya + polyb == Hypernomial([4, 4, 4, 7])

    polya = Hypernomial([1, 2, 3, 7])
    polyb = Hypernomial([3, 2, 1])
    assert polya + polyb == Hypernomial([4, 4, 4, 7])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_compare", "test_add"])
def test_sub():
    polya = Hypernomial([1, 3])
    assert polya - 3 == Hypernomial([-2, 3])
    assert 3 - polya == Hypernomial([2, -3])


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare", "test_add"])
def test_mult():
    sinht = Hypernomial([0, 1, 0])
    cosht = Hypernomial([0, 0, 1])
    sinh2t = Hypernomial([0, 0, 0, 1, 0])
    cosh2t = Hypernomial([0, 0, 0, 0, 1])

    val = cosht * cosht - sinht * sinht
    print("1 = ", val)
    assert cosht * cosht - sinht * sinht == 1
    assert cosh2t * cosh2t - sinh2t * sinh2t == 1
    assert 2 * sinht * cosht == sinh2t
    assert cosht * cosht + sinht * sinht == cosh2t
    assert cosh2t + 1 == 2 * cosht * cosht
    assert cosh2t - 1 == 2 * sinht * sinht


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare", "test_mult"])
def test_pow():
    sinht = Hypernomial([0, 1, 0])
    cosht = Hypernomial([0, 0, 1])
    sinh2t = Hypernomial([0, 0, 0, 1, 0])
    cosh2t = Hypernomial([0, 0, 0, 0, 1])

    assert sinht**0 == 1
    assert cosht**0 == 1
    assert sinh2t**0 == 1
    assert cosh2t**0 == 1
    assert sinht**1 == sinht
    assert cosht**1 == cosht
    assert sinh2t**1 == sinh2t
    assert cosh2t**1 == cosh2t

    assert cosht**2 - sinht**2 == 1
    assert cosh2t**2 - sinh2t**2 == 1
    assert 2 * sinht * cosht == sinh2t
    assert cosht**2 + sinht**2 == cosh2t
    assert cosh2t + 1 == 2 * cosht**2
    assert cosh2t - 1 == 2 * sinht**2


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_derivate():
    coefs = [3, 5, -4, 3, 2]
    trig = Hypernomial(coefs)
    test = trig.derivate(0)
    assert test == trig

    test = trig.derivate(1)
    good = Hypernomial([0, -4, 5, 4, 6])
    assert test != trig
    assert test == good


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_derivate"])
def test_integrate():
    coefs = [0, 5, -4, 3, 2]
    trig = Hypernomial(coefs)
    test = trig.integrate(0)
    assert test == trig

    for times in range(5):
        test = trig.derivate(times)
        test = test.integrate(times)
        assert test == trig


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_evaluate_natural", "test_derivate"])
def test_evaluate_derivate():
    trig = Hypernomial([1])  # p(x) = 1
    assert trig.eval(0, 1) == 0
    assert trig.eval(1, 1) == 0
    assert trig.eval(2, 1) == 0
    assert trig.eval(1.0, 1) == 0
    assert trig.eval(1, 2) == 0

    trig = Hypernomial([1, 2])  # p(x) = 1 + 2*sinh(x)
    assert trig.eval(0, 1) == 2
    assert trig.eval(1, 1) == 2 * math.cosh(1)
    assert trig.eval(2, 1) == 2 * math.cosh(2)
    assert trig.eval(0.0, 1) == 2
    assert trig.eval(1.0, 1) == 2 * math.cosh(1)
    assert trig.eval(2, 2) == 2 * math.sinh(2)
    assert trig.eval(0.0, 2) == 0

    trig = Hypernomial([1, 2, 3])  # p(x) = 1 + 2*sinh(x) + 3*cosh(x)
    assert trig.eval(0, 1) == 2
    assert trig.eval(1, 1) == 2 * math.cosh(1) + 3 * math.sinh(1)
    assert trig.eval(2, 1) == 2 * math.cosh(2) + 3 * math.sinh(2)
    assert trig.eval(0.0, 1) == 2
    assert trig.eval(1.0, 1) == 2 * math.cosh(1) + 3 * math.sinh(1)
    assert trig.eval(2, 2) == 2 * math.sinh(2) + 3 * math.cosh(2)
    assert trig.eval(0.0, 2) == 3
    assert trig.eval(2, 3) == 2 * math.cosh(2) + 3 * math.sinh(2)
    assert trig.eval(0.0, 3) == 2


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare", "test_simplify"])
def test_divide_scalar():
    sint = Hypernomial([0, 1, 0])
    cost = Hypernomial([0, 0, 1])

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
    assert sint // 2 == Hypernomial([0, 1 / 2, 0])
    assert cost // 2 == Hypernomial([0, 0, 1 / 2])
    assert sint / 2 == Hypernomial([0, 1 / 2, 0])
    assert cost / 2 == Hypernomial([0, 0, 1 / 2])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_divide_scalar"])
def test_divide_zero():
    numer = Hypernomial([1])
    denom = Hypernomial([0])
    with pytest.raises(ZeroDivisionError):
        numer / denom


@pytest.mark.order(3)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_divide_scalar"])
def test_divide_pmax1():
    sint = Hypernomial([0, 1, 0])
    cost = Hypernomial([0, 0, 1])


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build"])
def test_print():
    trig = Hypernomial([0])
    assert str(trig) == "0"
    trig = Hypernomial([0, 0])
    assert str(trig) == "0"
    trig = Hypernomial([0, 0, 0])
    assert str(trig) == "0"
    trig = Hypernomial([1])
    assert str(trig) == "1"
    trig = Hypernomial([1, 1])
    assert str(trig) == "1 + sinh(t)"
    trig = Hypernomial([1, 1, 1])
    assert str(trig) == "1 + sinh(t) + cosh(t)"
    trig = Hypernomial([1, 0, 1])
    assert str(trig) == "1 + cosh(t)"
    trig = Hypernomial([0, 0, 1])
    assert str(trig) == "cosh(t)"
    trig = Hypernomial([-1])
    assert str(trig) == "-1"
    trig = Hypernomial([-1, 1])
    assert str(trig) == "- 1 + sinh(t)"
    trig = Hypernomial([1, -1, 1])
    assert str(trig) == "1 - sinh(t) + cosh(t)"
    trig = Hypernomial([1, 0, 1])
    assert str(trig) == "1 + cosh(t)"
    trig = Hypernomial([1, 2, 3])
    assert str(trig) == "1 + 2 * sinh(t) + 3 * cosh(t)"
    repr(trig)

    trig = Hypernomial([1, 2, 3, 4, 5, 6, 7.9, 9])
    str(trig)
    repr(trig)


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_integrate"])
def test_definite_integrate():
    # Integrate constant
    trig = Hypernomial([0])
    assert trig.defintegral(0, 1) == 0
    for _ in range(100):  # ntests
        const, lower, upper = np.random.randint(-10, 10, 3)
        trig = Hypernomial([const])
        assert trig.defintegral(lower, upper) == (upper - lower) * const


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_build",
        "test_degree",
        "test_simplify",
        "test_evaluate_natural",
        "test_compare",
        "test_derivate",
        "test_integrate",
        "test_evaluate_derivate",
        "test_add",
        "test_sub",
        "test_mult",
        "test_pow",
        "test_divide_scalar",
        "test_divide_zero",
        "test_divide_pmax1",
        "test_definite_integrate",
    ]
)
def test_end():
    pass
