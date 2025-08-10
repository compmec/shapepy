"""
Some tools used in
"""

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

from ..scalar.reals import Math
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


def where_minimum_polynomial(
    polynomial: Polynomial, domain: SubSetR1 = Whole()
) -> SubSetR1:
    """
    Finds the value of t* such poly(t*) is minimal
    """
    assert Is.instance(polynomial, Polynomial)
    if polynomial.degree == 0:
        return domain
    if domain == Whole() and polynomial.degree % 2:
        return Empty()
    relation = {}
    domain_knots = tuple(extract_knots(domain))
    for knot in domain_knots:
        relation[knot] = polynomial(knot)
    critical = find_roots(derivate_analytic(polynomial), domain)
    critical_knots = set(extract_knots(critical))
    for knot in critical_knots:
        relation[knot] = polynomial(knot)
    minvalue = min(relation.values(), default=float("inf"))
    relation = {
        key: value
        for key, value in relation.items()
        if value == minvalue and key in domain
    }
    return unite(set(relation.keys()))


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
