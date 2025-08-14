import random

import numpy as np
import pytest

from shapepy.analytic.bezier import Bezier
from shapepy.analytic.polynomial import Polynomial


def generator_analytic(quantity: int):
    available = (Polynomial, Bezier)
    random.seed(0)
    for _ in range(quantity):
        npts = random.randint(1, 7)
        typo = available[random.randint(0, len(available) - 1)]
        coefs = (random.randint(-3, 3) for _ in range(npts))
        yield typo(coefs)


def generator_constants(quantity: int):
    random.seed(0)
    for _ in range(quantity):
        yield random.randint(-10, 10)


@pytest.mark.order(7)
@pytest.mark.dependency(
    depends=[
        "tests/analytic/test_polynomial.py::test_all",
        "tests/analytic/test_bezier.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(7)
@pytest.mark.dependency(depends=["test_begin"])
def test_neg():
    tsample = np.linspace(-1, 1, 17)
    for funca in generator_analytic(100):
        funcb = -funca
        valuesa = funca(tsample)
        valuesb = funcb(tsample)
        np.testing.assert_allclose(valuesb, -valuesa)


@pytest.mark.order(7)
@pytest.mark.dependency(depends=["test_begin"])
def test_add_const():
    tsample = np.linspace(-1, 1, 17)
    functions = generator_analytic(100)
    constants = generator_constants(100)
    for const, funca in zip(constants, functions):
        funcb = funca + const
        funcc = const + funca
        valuesa = funca(tsample)
        valuesb = funcb(tsample)
        valuesc = funcc(tsample)

        np.testing.assert_allclose(valuesa + const, valuesb)
        np.testing.assert_allclose(const + valuesa, valuesc)


@pytest.mark.order(7)
@pytest.mark.dependency(depends=["test_begin", "test_add_const"])
def test_add_analytic():
    tsample = np.linspace(-1, 1, 17)
    funcsa = generator_analytic(100)
    funcsb = generator_analytic(100)
    for funca, funcb in zip(funcsa, funcsb):
        funcc = funca + funcb
        valuesa = funca(tsample)
        valuesb = funcb(tsample)
        valuesc = funcc(tsample)

        np.testing.assert_allclose(valuesa + valuesb, valuesc)


@pytest.mark.order(7)
@pytest.mark.dependency(depends=["test_begin", "test_add_const"])
def test_sub_const():
    tsample = np.linspace(-1, 1, 17)
    functions = generator_analytic(100)
    constants = generator_constants(100)
    for const, funca in zip(constants, functions):
        funcb = funca - const
        funcc = const - funca
        valuesa = funca(tsample)
        valuesb = funcb(tsample)
        valuesc = funcc(tsample)

        np.testing.assert_allclose(valuesa - const, valuesb)
        np.testing.assert_allclose(const - valuesa, valuesc)


@pytest.mark.order(7)
@pytest.mark.dependency(
    depends=["test_begin", "test_add_analytic", "test_sub_const"]
)
def test_sub_analytic():
    tsample = np.linspace(-1, 1, 17)
    funcsa = generator_analytic(100)
    funcsb = generator_analytic(100)
    for funca, funcb in zip(funcsa, funcsb):
        funcc = funca - funcb
        valuesa = funca(tsample)
        valuesb = funcb(tsample)
        valuesc = funcc(tsample)

        np.testing.assert_allclose(valuesa - valuesb, valuesc)


@pytest.mark.order(7)
@pytest.mark.dependency(depends=["test_begin", "test_add_const"])
def test_mul_const():
    tsample = np.linspace(-1, 1, 17)
    functions = generator_analytic(100)
    constants = generator_constants(100)
    for const, funca in zip(constants, functions):
        funcb = funca * const
        funcc = const * funca
        valuesa = funca(tsample)
        valuesb = funcb(tsample)
        valuesc = funcc(tsample)

        np.testing.assert_allclose(valuesa * const, valuesb)
        np.testing.assert_allclose(const * valuesa, valuesc)


@pytest.mark.order(7)
@pytest.mark.dependency(
    depends=["test_begin", "test_add_analytic", "test_mul_const"]
)
def test_mul_analytic():
    tsample = np.linspace(-1, 1, 17)
    funcsa = generator_analytic(100)
    funcsb = generator_analytic(100)
    for funca, funcb in zip(funcsa, funcsb):
        funcc = funca * funcb
        valuesa = funca(tsample)
        valuesb = funcb(tsample)
        valuesc = funcc(tsample)

        np.testing.assert_allclose(valuesa * valuesb, valuesc)


@pytest.mark.order(7)
@pytest.mark.dependency(depends=["test_begin", "test_mul_analytic"])
def test_pow_analytic():
    tsample = np.linspace(-1, 1, 17)
    for funca in generator_analytic(100):
        for exp in range(0, 4):
            funcb = funca**exp
            valuesa = funca(tsample)
            valuesb = funcb(tsample)
            np.testing.assert_allclose(valuesb, valuesa**exp)


@pytest.mark.order(7)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_neg",
        "test_add_const",
        "test_add_analytic",
        "test_sub_const",
        "test_sub_analytic",
        "test_mul_const",
        "test_mul_analytic",
        "test_pow_analytic",
    ]
)
def test_shift():
    tsample = np.linspace(-1, 1, 17)
    for funca in generator_analytic(100):
        amount = random.randint(-5, 5)
        funcb = funca.shift(amount)
        valuesa = funca(tsample)
        valuesb = funcb(amount + tsample)
        np.testing.assert_allclose(valuesa, valuesb)


@pytest.mark.order(7)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_neg",
        "test_add_const",
        "test_add_analytic",
        "test_sub_const",
        "test_sub_analytic",
        "test_mul_const",
        "test_mul_analytic",
        "test_pow_analytic",
    ]
)
def test_scale():
    tsample = np.linspace(-1, 1, 17)
    for funca in generator_analytic(100):
        amount = random.randint(2, 5)
        funcb = funca.scale(amount)
        valuesa = funca(tsample)
        valuesb = funcb(amount * tsample)
        np.testing.assert_allclose(valuesa, valuesb, atol=1e-12, rtol=1)


@pytest.mark.order(7)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_neg",
        "test_add_const",
        "test_add_analytic",
        "test_sub_const",
        "test_sub_analytic",
        "test_mul_const",
        "test_mul_analytic",
        "test_pow_analytic",
        "test_shift",
        "test_scale",
    ]
)
def test_all():
    pass
