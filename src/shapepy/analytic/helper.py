"""
This file contains helper functions,
used to check if two analytic functions are equal
"""
from typing import Union

from ..core import IAnalytic, Parameter
from .polynomial import Polynomial
from .trigonometric import Trignomial


def check_shifted_analytic(
    analya: IAnalytic, analyb: IAnalytic
) -> Union[None, Parameter]:
    """
    Given two analytic functions a(t) and b(t),
    we want to find a value 'u' such b(t-u) = a(t) for all t
    If this value 'u' doesn't exist, returns None
    """
    if type(analya) is not type(analyb):
        return None
    if isinstance(analya, Trignomial):
        raise NotImplementedError
    if isinstance(analya, Polynomial) and isinstance(analyb, Polynomial):
        return check_shifted_polynomial(analya, analyb)
    raise NotImplementedError


def check_shifted_polynomial(
    polya: Polynomial, polyb: Polynomial
) -> Union[None, Parameter]:
    """
    Checks if two polynomial functions p(t) and q(t) are equal
    or if there's a value 'u' such q(t-u) = p(t) for all t
    If that's the case, then the function returns 'u'
    If it's not, then returns None
    """
    if not isinstance(polya, Polynomial) or not isinstance(polyb, Polynomial):
        raise TypeError

    degree = polya.degree
    if not degree or polyb.degree != degree or polya[degree] != polyb[degree]:
        return None

    param = polyb[degree - 1] - polya[degree - 1]
    param /= degree * polyb[degree]
    if polya.eval(0) != polyb.eval(-param):
        return None
    return -param
