"""
Defines the most used analytical functions used on the package
"""

from numbers import Real
from typing import Iterable

from .. import default
from ..logger import debug
from .base import IAnalytic1D
from .sympyana import SympyAnalytic1D


@debug("shapepy.analytic.elementar")
def polynomial(coefs: Iterable[Real]) -> IAnalytic1D:
    """
    Creates a polynomial from given coefficients

    It's an instance from the base class IAnalytic1D

    Parameters
    ----------
    coefs: Iterable[Real]
        The coefficients of the polynomial

    Return
    ------
    IAnalytic
        The function instance

    Example
    -------
    >>> polynomial([1])
    1
    >>> polynomial([1, 2])
    1 + 2 * t
    >>> polynomial([1, 2, 3])
    1 + 2 * t + 3 * t^2
    """
    coefs = map(default.finite, coefs)
    vart = SympyAnalytic1D.var
    expr = default.finite(0)
    for i, coef in enumerate(coefs):
        expr += coef * vart**i
    return SympyAnalytic1D(expr)
