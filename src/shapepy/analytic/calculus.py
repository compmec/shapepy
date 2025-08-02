"""
Methods to derivate and integrate scalar functions
"""

from typing import Union

from ..scalar.reals import Math
from ..tools import Is
from .bezier import Bezier, bezier2polynomial, polynomial2bezier
from .polynomial import Polynomial


def integrate_polynomial(polynomial: Polynomial, times: int = 1) -> Polynomial:
    """
    Integrates the polynomial curve

    Example
    -------
    >>> poly = Polynomial([1, 2, 5])
    >>> print(poly)
    1 + 2 * t + 5 * t^2
    >>> ipoly = integrate(poly)
    >>> print(ipoly)
    t + t^2 + (5/3) * t^3
    """
    for _ in range(times):
        newcoefs = [0 * polynomial[0]]
        newcoefs += list(coef / (n + 1) for n, coef in enumerate(polynomial))
        polynomial = Polynomial(newcoefs)
    return polynomial


def integrate_bezier(bezier: Bezier, times: int = 1) -> Bezier:
    """
    Integrates the Bezier curve
    """
    poly = bezier2polynomial(bezier)
    ipoly = integrate_polynomial(poly, times)
    return polynomial2bezier(ipoly)


def integrate(
    function: Union[Polynomial, Bezier], times: int = 1
) -> Union[Polynomial, Bezier]:
    """
    Integrates a function
    """
    if Is.instance(function, Polynomial):
        return integrate_polynomial(function, times)
    if Is.instance(function, Bezier):
        return integrate_bezier(function, times)
    raise NotImplementedError(f"Received type {type(function)}")


def derivate_polynomial(polynomial: Polynomial, times: int = 1) -> Polynomial:
    """
    Derivate the polynomial curve, giving a new one

    Example
    -------
    >>> poly = Polynomial([1, 2, 5])
    >>> print(poly)
    1 + 2 * t + 5 * t^2
    >>> dpoly = poly.derivate()
    >>> print(dpoly)
    2 + 10 * t
    """
    if polynomial.degree < times:
        return Polynomial([0 * polynomial[0]])
    coefs = (
        Math.factorial(n + times) // Math.factorial(n) * coef
        for n, coef in enumerate(polynomial[times:])
    )
    return Polynomial(coefs)


def derivate_bezier(bezier: Bezier, times: int = 1) -> Bezier:
    """
    Derivate the bezier curve, giving a new one

    Example
    -------
    >>> bezier = Bezier([1, 2, 5])
    >>> dbezier = derivate(bezier)
    """
    poly = bezier2polynomial(bezier)
    dpoly = derivate_polynomial(poly, times)
    return polynomial2bezier(dpoly)


def derivate(
    function: Union[Polynomial, Bezier], times: int = 1
) -> Union[Polynomial, Bezier]:
    """
    Derivates a function
    """
    if Is.instance(function, Polynomial):
        return derivate_polynomial(function, times)
    if Is.instance(function, Bezier):
        return derivate_bezier(function, times)
    raise NotImplementedError(f"Received type {type(function)}")
