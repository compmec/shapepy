import numpy as np
import pytest

from shapepy.scalar.polynomial import Polynomial
from shapepy.scalar.quadrature import AdaptativeIntegrator, IntegratorFactory
from shapepy.tools import To

all_methods = {
    IntegratorFactory.closed_newton_cotes: range(2, 7),
    IntegratorFactory.open_newton_cotes: range(1, 7),
    IntegratorFactory.custom_open_formula: range(1, 7),
    IntegratorFactory.clenshaw_curtis: range(1, 7),
}


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "tests/scalar/test_reals.py::test_all",
        "tests/scalar/test_angle.py::test_all",
        "tests/scalar/test_polynomial.py::test_all",
        "tests/scalar/test_nodes_sample.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(4)
@pytest.mark.timeout(5)
@pytest.mark.dependency(depends=["test_begin"])
def test_build():
    for method in all_methods:
        for npts in all_methods[method]:
            method(npts)


@pytest.mark.order(4)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin", "test_build"])
def test_polynomial_closed_newton_cotes():
    np.random.seed(0)

    ntests = 100
    method = IntegratorFactory.closed_newton_cotes
    numbers = all_methods[method]
    for npts in numbers:
        direct = method(npts)
        for degree in range(npts):
            for _ in range(ntests):
                coefs = np.random.randint(-4, 5, size=degree + 1)
                coefs = tuple(map(To.rational, coefs))
                function = Polynomial(coefs)
                good = sum((coef / (n + 1)) for n, coef in enumerate(coefs))
                test = direct.integrate(function, (0, 1))
                assert abs(test - good) < 1e-9


@pytest.mark.order(4)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin", "test_build"])
def test_polynomial_open_newton_cotes():
    np.random.seed(0)

    ntests = 100
    method = IntegratorFactory.open_newton_cotes
    numbers = all_methods[method]
    for npts in numbers:
        direct = method(npts)
        for degree in range(npts):
            for _ in range(ntests):
                coefs = np.random.randint(-4, 5, size=degree + 1)
                coefs = tuple(map(To.rational, coefs))
                function = Polynomial(coefs)
                good = sum((coef / (n + 1)) for n, coef in enumerate(coefs))
                test = direct.integrate(function, (0, 1))
                assert abs(test - good) < 1e-9


@pytest.mark.order(4)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin", "test_build"])
def test_polynomial_custom_open_formula():
    np.random.seed(0)

    ntests = 100
    method = IntegratorFactory.custom_open_formula
    numbers = all_methods[method]
    for npts in numbers:
        direct = method(npts)
        for degree in range(npts):
            for _ in range(ntests):
                coefs = np.random.randint(-4, 5, size=degree + 1)
                coefs = tuple(map(To.rational, coefs))
                function = Polynomial(coefs)
                good = sum((coef / (n + 1)) for n, coef in enumerate(coefs))
                test = direct.integrate(function, (0, 1))
                assert abs(test - good) < 1e-9


@pytest.mark.order(4)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin", "test_build"])
def test_polynomial_clenshaw_curtis():
    np.random.seed(0)

    ntests = 100
    method = IntegratorFactory.clenshaw_curtis
    numbers = all_methods[method]
    for npts in numbers:
        direct = method(npts)
        for degree in range(npts):
            for _ in range(ntests):
                coefs = np.random.randint(-4, 5, size=degree + 1)
                coefs = tuple(map(To.rational, coefs))
                function = Polynomial(coefs)
                good = sum((coef / (n + 1)) for n, coef in enumerate(coefs))
                test = direct.integrate(function, (0, 1))
                assert abs(test - good) < 1e-9


@pytest.mark.order(4)
@pytest.mark.timeout(5)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_build",
        "test_polynomial_open_newton_cotes",
        "test_polynomial_custom_open_formula",
        "test_polynomial_clenshaw_curtis",
    ]
)
def test_trignometric():
    tolerance = 1e-6
    direct = IntegratorFactory.open_newton_cotes(3, float)
    adaptative = AdaptativeIntegrator(direct, tolerance)
    function = np.sin
    interval = (0, 1)
    good = np.cos(interval[0]) - np.cos(interval[1])
    test = adaptative.integrate(function, interval)
    assert abs(test - good) < tolerance


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_polynomial_closed_newton_cotes",
        "test_polynomial_open_newton_cotes",
        "test_polynomial_custom_open_formula",
        "test_polynomial_clenshaw_curtis",
        "test_trignometric",
    ]
)
def test_all():
    pass
