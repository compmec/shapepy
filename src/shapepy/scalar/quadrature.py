"""
Defines the functions used to numerical integration
"""

from functools import lru_cache
from typing import Iterable, Tuple

import pynurbs

from ..tools import Is, To
from .reals import Rational, Real


def inner(vectora: Iterable[Real], vectorb: Iterable[Real]) -> Real:
    """Returns the inner product of two vectors"""
    if not Is.iterable(vectora) or not Is.iterable(vectorb):
        raise TypeError("Expected two iterables")
    vectora = tuple(vectora)
    vectorb = tuple(vectorb)
    result = vectora[0] * vectorb[0]
    return sum((a * b for a, b in zip(vectora[1:], vectorb[1:])), start=result)


@lru_cache(maxsize=None)
def closed_linspace(npts: int) -> Tuple[Rational, ...]:
    """
    Gives a set of numbers in interval [0, 1]

    Example
    -------
    >>> closed_linspace(2)
    (0, 1)
    >>> closed_linspace(3)
    (0, 0.5, 1)
    >>> closed_linspace(4)
    (0, 0.33, 0.66, 1)
    >>> closed_linspace(5)
    (0, 0.25, 0.5, 0.75, 1)
    """
    if not Is.integer(npts) or npts < 2:
        raise ValueError("npts must be integer >= 2")
    return tuple(To.rational(num, npts - 1) for num in range(npts))


@lru_cache(maxsize=None)
def open_linspace(npts: int) -> Tuple[Rational, ...]:
    """
    Gives a set of numbers in interval (0, 1)

    Example
    -------
    >>> open_linspace(1)
    (0.5, )
    >>> open_linspace(2)
    (0.33, 0.66)
    >>> open_linspace(3)
    (0.25, 0.50, 0.75)
    """
    if not Is.integer(npts) or npts < 1:
        raise ValueError("npts must be integer >= 1")
    return tuple(To.rational(num, 2 * npts) for num in range(1, 2 * npts, 2))


@lru_cache(maxsize=None)
def open_newton_cotes(npts: int) -> Tuple[Real, ...]:
    """Returns the weight array for open newton-cotes formula
    in the interval (0, 1)

    Example
    ------------
    >>> open_newton_cotes(1)
    (1, )
    >>> open_newton_cotes(2)
    (1/2, 1/2)
    >>> open_newton_cotes(3)
    (3/8, 1/4, 3/8)
    >>> open_newton_cotes(4)
    (13/48, 11/48, 11/48, 13/48)
    >>> open_newton_cotes(5)
    (275/1152, 25/288, 67/192, 25/288, 275/1152)

    """
    func = pynurbs.heavy.IntegratorArray.open_newton_cotes
    return tuple(map(To.finite, func(npts)))
