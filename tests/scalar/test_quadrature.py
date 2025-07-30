from typing import Iterable

import pytest

from shapepy.scalar.polynomial import Polynomial
from shapepy.scalar.quadrature import (
    AdaptativeIntegrator,
    DirectIntegratorFactory,
)
from shapepy.tools import To


def all_methods():
    methods = {DirectIntegratorFactory.open_newton_cotes: range(1, 6)}
    for method in methods:
        for npts in methods[method]:
            yield method, npts


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "tests/scalar/test_reals.py::test_all",
        "tests/scalar/test_angle.py::test_all",
        "tests/scalar/test_polynomial.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_begin"])
def test_build():
    for method, npts in all_methods():
        method(npts)


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_begin", "test_build"])
def test_polynomial():
    import numpy as np

    ntests = 100
    for method, npts in all_methods():
        direct = method(npts)
        for degree in range(npts):
            for _ in range(ntests):
                coefs = np.random.randint(-4, 5, size=degree + 1)
                coefs = tuple(map(To.rational, coefs))
                function = Polynomial(coefs)
                good = sum((coef / (n + 1)) for n, coef in enumerate(coefs))
                test = direct.integrate(function, (0, 1))
                assert test == good


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=["test_begin", "test_build", "test_polynomial"]
)
def test_trignometric():
    import numpy as np

    tolerance = 1e-6
    direct = DirectIntegratorFactory.open_newton_cotes(3, float)
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
        "test_polynomial",
        "test_trignometric",
    ]
)
def test_all():
    pass
