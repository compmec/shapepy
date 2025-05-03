import numpy as np
import pytest

from shapepy.quadrature import chebyshev, closed_newton, gauss, open_newton


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_open_newton():
    """
    Tests if the given nodes and weights integrates exactly
    a polynomial of degree p, with p+1 evaluation points

    We start with P(x) = x^{p}
    And after we evaluate P(x) = sum_i c_i * x^i
    for random c_i
    """
    for nptsinteg in range(1, 4):
        quad = open_newton(nptsinteg)
        for degree in range(nptsinteg):  # Integrate each basis
            good_integral = 1 / (1 + degree)
            fvalues = tuple(node**degree for node in quad.nodes)
            test_integral = np.inner(fvalues, quad.weights)
            diff = abs(test_integral - good_integral)
            assert abs(diff) < 1e-5

    for nptsinteg in range(1, 4):
        quad = open_newton(nptsinteg)
        fvalues = np.zeros(len(quad.nodes))
        for degree in range(nptsinteg):
            coefs = np.random.uniform(-1, 1, degree + 1)
            good_integral = sum(ci / (1 + i) for i, ci in enumerate(coefs))
            fvalues.fill(0)
            for i, node in enumerate(quad.nodes):
                for ck in coefs[::-1]:  # Horner's method
                    fvalues[i] *= node
                    fvalues[i] += ck
            test_integral = np.inner(fvalues, quad.weights)
            diff = abs(test_integral - good_integral)
            assert diff < 1e-15


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_closed_newton():
    """
    Tests if the given nodes and weights integrates exactly
    a polynomial of degree p, with p+1 evaluation points

    We start with P(x) = x^{p}
    And after we evaluate P(x) = sum_i c_i * x^i
    for random c_i
    """
    for nptsinteg in range(2, 6):
        quad = closed_newton(nptsinteg)
        for degree in range(nptsinteg):  # Integrate each basis
            good_integral = 1 / (1 + degree)
            fvalues = tuple(node**degree for node in quad.nodes)
            test_integral = np.inner(fvalues, quad.weights)
            diff = abs(test_integral - good_integral)
            assert abs(diff) < 1e-5

    for nptsinteg in range(2, 6):
        quad = closed_newton(nptsinteg)
        fvalues = np.zeros(len(quad.nodes))
        for degree in range(nptsinteg):
            coefs = np.random.uniform(-1, 1, degree + 1)
            good_integral = sum(ci / (1 + i) for i, ci in enumerate(coefs))
            fvalues.fill(0)
            for i, node in enumerate(quad.nodes):
                for ck in coefs[::-1]:  # Horner's method
                    fvalues[i] *= node
                    fvalues[i] += ck
            test_integral = np.inner(fvalues, quad.weights)
            diff = abs(test_integral - good_integral)
            assert diff < 1e-15


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_chebyshev():
    """
    Tests if the given nodes and weights integrates exactly
    a polynomial of degree p, with p+1 evaluation points

    We start with P(x) = x^{p}
    And after we evaluate P(x) = sum_i c_i * x^i
    for random c_i
    """
    for nptsinteg in range(1, 6):
        quad = chebyshev(nptsinteg)
        for degree in range(nptsinteg):  # Integrate each basis
            good_integral = 1 / (1 + degree)
            fvalues = tuple(node**degree for node in quad.nodes)
            test_integral = np.inner(fvalues, quad.weights)
            diff = abs(test_integral - good_integral)
            assert abs(diff) < 1e-5

    for nptsinteg in range(1, 6):
        quad = chebyshev(nptsinteg)
        fvalues = np.zeros(len(quad.nodes))
        for degree in range(nptsinteg):
            coefs = np.random.uniform(-1, 1, degree + 1)
            good_integral = sum(ci / (1 + i) for i, ci in enumerate(coefs))
            fvalues.fill(0)
            for i, node in enumerate(quad.nodes):
                for ck in coefs[::-1]:  # Horner's method
                    fvalues[i] *= node
                    fvalues[i] += ck
            test_integral = np.inner(fvalues, quad.weights)
            diff = abs(test_integral - good_integral)
            assert diff < 1e-15


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_gauss():
    """
    Tests if the given nodes and weights integrates exactly
    a polynomial of degree p, with p+1 evaluation points

    We start with P(x) = x^{p}
    And after we evaluate P(x) = sum_i c_i * x^i
    for random c_i
    """
    for nptsinteg in range(1, 9):
        quad = gauss(nptsinteg)
        for degree in range(2 * nptsinteg):  # Integrate each basis
            good_integral = 1 / (1 + degree)
            fvalues = tuple(node**degree for node in quad.nodes)
            test_integral = np.inner(fvalues, quad.weights)
            diff = abs(test_integral - good_integral)
            assert abs(diff) < 1e-5

    for nptsinteg in range(1, 9):
        quad = gauss(nptsinteg)
        fvalues = np.zeros(len(quad.nodes))
        for degree in range(2 * nptsinteg):
            coefs = np.random.uniform(-1, 1, degree + 1)
            good_integral = sum(ci / (1 + i) for i, ci in enumerate(coefs))
            fvalues.fill(0)
            for i, node in enumerate(quad.nodes):
                for ck in coefs[::-1]:  # Horner's method
                    fvalues[i] *= node
                    fvalues[i] += ck
            test_integral = np.inner(fvalues, quad.weights)
            diff = abs(test_integral - good_integral)
            assert diff < 1e-9


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_adaptative():
    for quadfunc in (open_newton, chebyshev, gauss):
        for nptsinteg in range(1, 4):
            quad = quadfunc(nptsinteg)
            for degree in range(nptsinteg + 1):

                def function(x):
                    return x**degree

                good = 1 / (1 + degree)
                test = quad.adaptative(function, 0, 1, 1e-9)
                assert abs(test - good) < 1e-8


@pytest.mark.order(1)
@pytest.mark.dependency(
    depends=[
        "test_open_newton",
        "test_closed_newton",
        "test_chebyshev",
        "test_gauss",
        "test_adaptative",
    ]
)
def test_end():
    pass
