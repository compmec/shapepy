"""
Some tools used in
"""

from typing import Union

import numpy as np
from rbool import (
    Empty,
    SingleValue,
    SubSetR1,
    Whole,
    extract_knots,
    from_any,
    unite,
)

from ..loggers import debug
from ..scalar.reals import Math, Real
from ..tools import Is, NotExpectedError, To
from .base import IAnalytic, derivate_analytic
from .bezier import Bezier, bezier2polynomial
from .polynomial import Polynomial


def find_polynomial_roots(
    polynomial: Polynomial, domain: SubSetR1 = Whole()
) -> SubSetR1:
    """
    Finds all the values of t* such p(t*) = 0 inside given domain
    """
    assert Is.instance(polynomial, Polynomial)
    polynomial = polynomial.clean()
    domain &= polynomial.domain
    if polynomial.degree == 0:
        return domain if polynomial[0] == 0 else Empty()
    if polynomial.degree == 1:
        numerator = -To.rational(1, 1) * polynomial[0]
        return SingleValue(numerator / polynomial[1])
    if polynomial.degree == 2:
        c, b, a = polynomial
        delta = b * b - 4 * a * c
        if delta < 0:
            return Empty()
        sqrtdelta = Math.sqrt(delta)
        half = To.rational(1, 2)
        x0 = half * (-b - sqrtdelta) / a
        x1 = half * (-b + sqrtdelta) / a
        return from_any({x0, x1})
    roots = np.roots(tuple(polynomial)[::-1])
    roots = (To.real(np.real(r)) for r in roots if abs(np.imag(r)) < 1e-15)
    return from_any(set(roots))


def where_minimum_polynomial(
    polynomial: Polynomial, domain: SubSetR1 = Whole()
) -> SubSetR1:
    """
    Finds the value of t* such poly(t*) is minimal
    """
    assert Is.instance(polynomial, Polynomial)
    domain &= polynomial.domain
    if polynomial.degree == 0:
        return domain
    if domain == Whole() and polynomial.degree % 2:
        return Empty()
    relation = {knot: polynomial(knot) for knot in extract_knots(domain)}
    critical = find_roots(derivate_analytic(polynomial), domain)
    for knot in extract_knots(critical):
        relation[knot] = polynomial(knot)
    minvalue = min(relation.values(), default=float("inf"))
    relation = {
        key: value
        for key, value in relation.items()
        if value == minvalue and key in domain
    }
    return unite(set(relation.keys()))


def find_minimum_polynomial(
    polynomial: Polynomial, domain: SubSetR1 = Whole()
) -> Union[Real, None]:
    """
    Finds the minimal value of p(t) in the given domain

    If the minimal does not exist, returns None

    If the polynomial goes to -inf, returns -inf
    """
    assert Is.instance(polynomial, Polynomial)
    if polynomial.degree == 0:
        return polynomial[0]
    if domain == Whole() and polynomial.degree % 2:
        return Math.NEGINF
    relation = {}
    relation = {knot: polynomial(knot) for knot in extract_knots(domain)}
    critical = find_roots(derivate_analytic(polynomial), domain)
    for knot in extract_knots(critical):
        relation[knot] = polynomial(knot)
    return min(
        (val for key, val in relation.items() if key in domain), default=None
    )


@debug("shapepy.analytic.tools")
def find_roots(analytic: IAnalytic, domain: SubSetR1 = Whole()) -> SubSetR1:
    """
    Finds the values of roots of the Analytic function
    """
    assert Is.instance(analytic, IAnalytic)
    domain = from_any(domain)
    if Is.instance(analytic, Polynomial):
        return find_polynomial_roots(analytic, domain)
    if Is.instance(analytic, Bezier):
        return find_roots(bezier2polynomial(analytic), domain)
    raise NotExpectedError


@debug("shapepy.analytic.tools")
def where_minimum(analytic: IAnalytic, domain: SubSetR1 = Whole()) -> SubSetR1:
    """
    Finds the parameters (t*) such the analytic function is minimum
    """
    assert Is.instance(analytic, IAnalytic)
    domain = from_any(domain)
    if Is.instance(analytic, Polynomial):
        return where_minimum_polynomial(analytic, domain)
    if Is.instance(analytic, Bezier):
        return where_minimum(bezier2polynomial(analytic), domain)
    raise NotExpectedError


@debug("shapepy.analytic.tools")
def find_minimum(analytic: IAnalytic, domain: SubSetR1 = Whole()) -> SubSetR1:
    """
    Finds the minimal value for the given analytic in the given domain
    """
    assert Is.instance(analytic, IAnalytic)
    domain = from_any(domain)
    if Is.instance(analytic, Polynomial):
        return find_minimum_polynomial(analytic, domain)
    if Is.instance(analytic, Bezier):
        return find_minimum(bezier2polynomial(analytic), domain)
    raise NotExpectedError
