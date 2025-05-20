"""
Define useful functions to be used in the other submodules
"""

from numbers import Real
from typing import Optional, Tuple

from ..bool1d import SubSetR1, infimum, supremum
from .base import IAnalytic1D
from .piecewise import PiecewiseAnalytic1D


def extract_knots(analytic: IAnalytic1D) -> Tuple[Real, ...]:
    """
    Extract the knots from the analytic function.

    If it's a piecewise, gives the knots
    Else, it gives the boundary of the domain
    """
    if isinstance(analytic, PiecewiseAnalytic1D):
        return analytic.knots
    return (infimum(analytic.domain), supremum(analytic.domain))


def is_continuous(
    analytic: IAnalytic1D, subdomain: Optional[SubSetR1] = None
) -> bool:
    """
    Tells if the analytic function is continuous on the given subdomain

    Needs more implementation.
    But for now, we suppose proper input from the user
    """
    if not isinstance(analytic, IAnalytic1D):
        raise TypeError
    return True


def limit(
    analytic: IAnalytic1D, node: Real, left: bool, derivate: int = 0
) -> Real:
    """
    Computes the limit for an analytic function

    limit_(t -> node) analytic(t)

    Parameters
    ----------
    analytic: IAnalytic1D
        The y coordinate
    node: Real
        The value to evaluate
    left: bool
        If it needs to approach from left or right
    derivate: int, default = 0
        If needs to take the derivate value

    """
    if not isinstance(analytic, PiecewiseAnalytic1D):
        return analytic.eval(node, derivate)
    try:
        index = analytic.knots.index(node)
    except ValueError:
        return analytic.eval(node, derivate)

    if left:
        analytic = analytic.analytics[index - 1]
    else:
        analytic = analytic.analytics[index]

    return analytic.eval(node, derivate)


def limit_uatan2(
    yanalytic: IAnalytic1D, xanalytic: IAnalytic1D, node: Real, left: bool
) -> Real:
    """
    Computes the expression:

    limit_(t -> node) uarctan2(yanalytic(t), xanalytic(t))

    Where

    * uarctan2 is equal to arctan2(yval, xval)/tau
    * arctan2 is the inverse of the tangent function

    Parameters
    ----------
    yanalytic: IAnalytic1D
        The y coordinate
    xanalytic: IAnalytic1D
        The x coordinate
    node: Real
        The value to evaluate
    left: bool
        If it needs to approach from left or right

    Return
    ------
    Real
        A value in the interval (-0.5, 0.5]
    """
    raise NotImplementedError
