"""
Defines the most used analytical functions used on the package
"""

from numbers import Real
from typing import Iterable, Optional

from .. import default
from ..bool1d import ConverterR1, IntervalR1, SubSetR1, WholeR1
from ..loggers import debug
from .base import IAnalytic1D
from .piecewise import PiecewiseAnalytic1D
from .sympyana import SympyAnalytic1D


@debug("shapepy.analytic.elementar")
def polynomial(
    coefs: Iterable[Real], domain: Optional[SubSetR1] = None
) -> IAnalytic1D:
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
    domain = WholeR1() if domain is None else ConverterR1.from_any(domain)
    coefs = map(default.finite, coefs)
    vart = SympyAnalytic1D.var
    expr = default.finite(0)
    for i, coef in enumerate(coefs):
        expr += coef * vart**i
    return SympyAnalytic1D(expr, domain)


@debug("shapepy.analytic.elementar")
def piecewise(
    analytics: Iterable[IAnalytic1D], knots: Iterable[Real]
) -> IAnalytic1D:
    """
    Gives a piecewise analytical function that is the combination
    from the received analytics and the knots points

    Parameters
    ----------
    analytics: Iterable[IAnalytic1D]
        The parts of the analyticals
    knots: Iterable[Real]
        The divisions between the analytics

    Return
    ------
    IAnalytic1D
        The piecewise analytic function

    Example
    -------
    >>> polya = polynomial([1, 2])
    >>> polyb = polynomial([5, -1])
    >>> knots = ("-inf", 1, "+inf")
    >>> pieceana = piecewise([polya, polyb], knots)
    """
    knots = tuple(map(default.real, knots))
    parameters = {}
    for i, analytic in enumerate(analytics):
        right = i + 1 == len(analytics)
        subset = IntervalR1(knots[i], knots[i + 1], True, right)
        parameters[subset] = analytic.section(subset)
    return PiecewiseAnalytic1D(parameters)
