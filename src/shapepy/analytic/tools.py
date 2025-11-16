"""
Some tools used in
"""

from typing import Union

import numpy as np

from ..loggers import debug
from ..rbool import (
    EmptyR1,
    IntervalR1,
    SingleR1,
    SubSetR1,
    WholeR1,
    extract_knots,
    from_any,
    move,
    scale,
    unite,
)
from ..scalar.reals import Math, Real
from ..tools import Is, NotExpectedError, To
from .base import IAnalytic
from .polynomial import Polynomial


@debug("shapepy.analytic.tools")
def find_roots(analytic: IAnalytic, domain: SubSetR1 = WholeR1()) -> SubSetR1:
    """
    Finds the values of roots of the Analytic function
    """
    assert Is.instance(analytic, IAnalytic)
    domain = from_any(domain)
    if Is.instance(analytic, Polynomial):
        return PolynomialFunctions.find_roots(analytic, domain)
    raise NotExpectedError(f"Invalid analytic: {type(analytic)}")


@debug("shapepy.analytic.tools")
def where_minimum(
    analytic: IAnalytic, domain: SubSetR1 = WholeR1()
) -> SubSetR1:
    """
    Finds the parameters (t*) such the analytic function is minimum
    """
    assert Is.instance(analytic, IAnalytic)
    domain = from_any(domain)
    if Is.instance(analytic, Polynomial):
        return PolynomialFunctions.where_minimum(analytic, domain)
    raise NotExpectedError(f"Invalid analytic: {type(analytic)}")


@debug("shapepy.analytic.tools")
def find_minimum(
    analytic: IAnalytic, domain: SubSetR1 = WholeR1()
) -> SubSetR1:
    """
    Finds the minimal value for the given analytic in the given domain
    """
    assert Is.instance(analytic, IAnalytic)
    domain = from_any(domain)
    if Is.instance(analytic, Polynomial):
        return PolynomialFunctions.find_minimum(analytic, domain)
    raise NotExpectedError(f"Invalid analytic: {type(analytic)}")


@debug("shapepy.analytic.tools")
def derivate_analytic(analytic: IAnalytic, times: int = 1) -> IAnalytic:
    """
    Derivate the analytic curve, giving a new one[]
    """
    if Is.instance(analytic, Polynomial):
        return PolynomialFunctions.derivate(analytic, times)
    raise NotExpectedError(f"Invalid analytic: {type(analytic)}")


@debug("shapepy.analytic.tools")
def integrate_analytic(analytic: IAnalytic, domain: SubSetR1) -> IAnalytic:
    """
    Derivate the analytic curve, giving a new one[]
    """
    if domain not in analytic.domain:
        raise ValueError(
            f"Given domain {domain} is not subset of {analytic.domain}"
        )
    if Is.instance(analytic, Polynomial):
        return PolynomialFunctions.integrate(analytic, domain)
    raise NotExpectedError(f"Invalid analytic: {type(analytic)}")


def shift_domain(analytic: IAnalytic, amount: Real) -> IAnalytic:
    """
    Transforms the analytic p(t) into p(t-d) by
    translating the analytic by 'd' to the right.

    Example
    -------
    >>> old_poly = Polynomial([0, 0, 0, 1])
    >>> print(old_poly)
    t^3
    >>> new_poly = shift_domain(poly, 1)  # transform to (t-1)^3
    >>> print(new_poly)
    - 1 + 3 * t - 3 * t^2 + t^3
    """
    amount = To.finite(amount)
    if Is.instance(analytic, Polynomial):
        return PolynomialFunctions.shift_domain(analytic, amount)
    raise NotExpectedError(f"Invalid analytic: {type(analytic)}")


def scale_domain(analytic: IAnalytic, amount: Real) -> IAnalytic:
    """
    Transforms the analytic p(t) into p(A*t) by
    scaling the argument of the analytic by 'A'.

    Example
    -------
    >>> old_poly = Polynomial([0, 2, 0, 1])
    >>> print(old_poly)
    2 * t + t^3
    >>> new_poly = scale_domain(poly, 2)
    >>> print(new_poly)
    4 * t + 8 * t^3
    """
    amount = To.finite(amount)
    if Is.instance(analytic, Polynomial):
        return PolynomialFunctions.scale_domain(analytic, amount)
    raise NotExpectedError(f"Invalid analytic: {type(analytic)}")


class PolynomialFunctions:
    """Static class that stores static functions used for the generics
    functions above. This class specifics for Polynomial"""

    @staticmethod
    def find_roots(polynomial: Polynomial, domain: SubSetR1) -> SubSetR1:
        """
        Finds all the values of t* such p(t*) = 0 inside given domain
        """
        assert Is.instance(polynomial, Polynomial)
        domain &= polynomial.domain
        if polynomial.degree == 0:
            return domain if polynomial[0] == 0 else EmptyR1()
        if polynomial.degree == 1:
            numerator = -To.rational(1, 1) * polynomial[0]
            return SingleR1(numerator / polynomial[1])
        if polynomial.degree == 2:
            c, b, a = polynomial
            delta = b * b - 4 * a * c
            if delta < 0:
                return EmptyR1()
            sqrtdelta = Math.sqrt(delta)
            half = To.rational(1, 2)
            x0 = half * (-b - sqrtdelta) / a
            x1 = half * (-b + sqrtdelta) / a
            return from_any({x0, x1})
        roots = np.roots(tuple(polynomial)[::-1])
        roots = (To.real(np.real(r)) for r in roots if abs(np.imag(r)) < 1e-15)
        return from_any(set(roots))

    @staticmethod
    def where_minimum(polynomial: Polynomial, domain: SubSetR1) -> SubSetR1:
        """
        Finds the value of t* such poly(t*) is minimal
        """
        assert Is.instance(polynomial, Polynomial)
        domain &= polynomial.domain
        if polynomial.degree == 0:
            return domain
        if domain == WholeR1() and polynomial.degree % 2:
            return EmptyR1()
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

    @staticmethod
    def find_minimum(
        polynomial: Polynomial, domain: SubSetR1
    ) -> Union[Real, None]:
        """
        Finds the minimal value of p(t) in the given domain

        If the minimal does not exist, returns None

        If the polynomial goes to -inf, returns -inf
        """
        assert Is.instance(polynomial, Polynomial)
        if polynomial.degree == 0:
            return polynomial[0]
        if domain == WholeR1() and polynomial.degree % 2:
            return Math.NEGINF
        relation = {}
        relation = {knot: polynomial(knot) for knot in extract_knots(domain)}
        critical = find_roots(derivate_analytic(polynomial), domain)
        for knot in extract_knots(critical):
            relation[knot] = polynomial(knot)
        return min(
            (val for key, val in relation.items() if key in domain),
            default=None,
        )

    @staticmethod
    def derivate(polynomial: Polynomial, times: int = 1) -> Polynomial:
        """
        Derivate the polynomial curve, giving a new one

        Example
        -------
        >>> poly = Polynomial([1, 2, 5])
        >>> print(poly)
        1 + 2 * t + 5 * t^2
        >>> dpoly = derivate(poly)
        >>> print(dpoly)
        2 + 10 * t
        """
        if polynomial.degree < times:
            return Polynomial([0 * polynomial[0]], polynomial.domain)
        coefs = (
            Math.factorial(n + times) // Math.factorial(n) * coef
            for n, coef in enumerate(polynomial[times:])
        )
        return Polynomial(coefs, polynomial.domain)

    @staticmethod
    def integrate(polynomial: Polynomial, domain: SubSetR1) -> Polynomial:
        """
        Derivate the polynomial curve, giving a new one

        Example
        -------
        >>> poly = Polynomial([1, 2, 5])
        >>> print(poly)
        1 + 2 * t + 5 * t^2
        >>> dpoly = derivate(poly)
        >>> print(dpoly)
        2 + 10 * t
        """
        domain = from_any(domain)
        if domain not in polynomial.domain:
            raise ValueError(
                f"Given domain {domain} is not subset of {polynomial.domain}"
            )
        if not Is.instance(domain, IntervalR1):
            raise ValueError(f"Cannot integrate over {domain}")
        left, right = domain[0], domain[1]
        potencias = [1]
        result = 0
        for i, coef in enumerate(polynomial):
            result += coef * sum(potencias) / (i + 1)
            potencias.append(right * potencias[-1])
            for j in range(i + 1):
                potencias[j] *= left
        return result * (right - left)

    @staticmethod
    def shift_domain(polynomial: Polynomial, amount: Real) -> Polynomial:
        """
        Transforms the analytic p(t) into p(t-d) by
        translating the analytic by 'd' to the right.

        Example
        -------
        >>> old_poly = Polynomial([0, 0, 0, 1])
        >>> print(old_poly)
        t^3
        >>> new_poly = shift_domain(poly, 1)  # transform to (t-1)^3
        >>> print(new_poly)
        - 1 + 3 * t - 3 * t^2 + t^3
        """
        newcoefs = list(polynomial)
        for i, coef in enumerate(polynomial):
            for j in range(i):
                value = Math.binom(i, j) * (amount ** (i - j))
                if (i + j) % 2:
                    value *= -1
                newcoefs[j] += coef * value
        return Polynomial(newcoefs, move(polynomial.domain, amount))

    @staticmethod
    def scale_domain(polynomial: Polynomial, amount: Real) -> Polynomial:
        """
        Transforms the analytic p(t) into p(A*t) by
        scaling the argument of the analytic by 'A'.

        Example
        -------
        >>> old_poly = Polynomial([0, 2, 0, 1])
        >>> print(old_poly)
        2 * t + t^3
        >>> new_poly = scale_domain(poly, 2)
        >>> print(new_poly)
        4 * t + 8 * t^3
        """
        inv = 1 / amount
        coefs = tuple(coef * inv**i for i, coef in enumerate(polynomial))
        return Polynomial(coefs, scale(polynomial.domain, amount))
