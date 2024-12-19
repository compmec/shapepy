"""
This file contains a class Polynomial that allows evaluating and
making operations with polynomials, like adding, multiplying, etc
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Iterable, Optional, Tuple, Union

import numpy as np

from ..core import IAnalytic, Math, Parameter, Scalar
from .base import BaseAnalytic
from .utils import binom, divisors, factorial, gcd, lcm


def polyderi(poly: Tuple[Scalar, ...], times: int) -> Tuple[Scalar, ...]:
    """
    Computes the coefficients of a polynomial,
     such is the derivated of given polynomial
    """
    times = int(times)
    if times < 0:
        raise ValueError
    if times == 0:
        return poly
    if times >= len(poly):
        return (0 * poly[0],)
    return tuple(
        (factorial(n + times) // factorial(n)) * coef
        for n, coef in enumerate(poly[times:])
    )


def polyinte(poly: Tuple[Scalar, ...], times: int) -> Tuple[Scalar, ...]:
    """
    Computes the coefficients of a polynomial,
     such is the integration of given polynomial.

    The constant terms of integration is assumed zero
    """
    times = int(times)
    if times < 0:
        raise ValueError
    if times == 0:
        return poly
    zero = 0 * sum(poly)
    numbs = tuple(
        factorial(n + times) // factorial(n) for n in range(len(poly))
    )
    coefs = (coef / numb for numb, coef in zip(numbs, poly))
    return tuple(times * [zero] + list(coefs))


class Polynomial(BaseAnalytic):
    """
    Defines a polynomial with coefficients

    p(x) = a0 + a1 * x + a2 * x^2 + ... + ap * x^p

    By receiving the coefficients

    coefs = [a0, a1, a2, ..., ap]

    This class allows evaluating, adding, multiplying, etc

    Example
    -------
    >>> poly = Polynomial([3, 2])
    >>> poly(0)
    3
    >>> poly(1)
    5
    """

    @classmethod
    def from_roots(cls, roots: Iterable[Parameter]) -> Polynomial:
        """
        Returns a polynomial p(t) such has the given roots.
        It's degree is the number of roots


        Parameters
        ----------
        roots: Iterable[Parameter]
            The roots of the polynomial
        """
        poly = cls([1])
        for root in roots:
            poly *= cls([-root, 1])
        return poly

    def __init__(self, coefs: Iterable[Any]):
        coefs = tuple(coefs)
        degree = max((i for i, coef in enumerate(coefs) if coef), default=0)
        super().__init__(coefs[: degree + 1])

    @property
    def degree(self) -> int:
        """
        Gives the degree of the polynomial
        """
        return len(self) - 1

    def __neg__(self) -> Polynomial:
        coefs = tuple(-coef for coef in self)
        return self.__class__(coefs)

    def __add__(self, other: Union[Any, Polynomial]) -> Polynomial:
        if isinstance(other, IAnalytic):
            if not isinstance(other, self.__class__):
                raise TypeError(f"Cannot add {self} with {other}")
        if not isinstance(other, Polynomial):
            other = Polynomial([other])
        coefs = [0] * (1 + max(self.degree, other.degree))
        for i, coef in enumerate(self):
            coefs[i] += coef
        for i, coef in enumerate(other):
            coefs[i] += coef
        return self.__class__(coefs)

    def __mul__(self, other: Union[Any, Polynomial]) -> Polynomial:
        if isinstance(other, IAnalytic):
            if not isinstance(other, self.__class__):
                raise TypeError(f"Cannot multiply {self} by {other}")
        if not isinstance(other, Polynomial):
            other = Polynomial([other])
        coefs = [0 * self[0] for _ in range(1 + self.degree + other.degree)]
        for i, coefi in enumerate(self):
            for j, coefj in enumerate(other):
                coefs[i + j] += coefi * coefj
        return self.__class__(coefs)

    def __divmod__(
        self, other: Union[Any, Polynomial]
    ) -> Tuple[Polynomial, Polynomial]:
        if isinstance(other, IAnalytic):
            if not isinstance(other, self.__class__):
                raise TypeError(f"Cannot divide {self} by {other}")
        if not isinstance(other, Polynomial):
            coefs = (coef / other for coef in self)
            return Polynomial(coefs), Polynomial([0 * sum(self)])
        zero = 0 * (sum(self) + sum(other))
        qoly = Polynomial([zero])
        roly = self - other * qoly
        while roly.degree >= other.degree:
            coef = roly[-1] / other[-1]
            qcoefs = [0] * (roly.degree - other.degree) + [coef]
            qoly += Polynomial(qcoefs)
            rcoefs = tuple(self - other * qoly)
            # Needed for float precision problems
            roly = Polynomial(rcoefs[: roly.degree])
        return qoly, roly

    def __str__(self):
        msgs = []
        if self.degree == 0:
            return str(self[0])
        flag = False
        for i, coef in enumerate(self):
            if coef == 0:
                continue
            if coef < 0:
                msg = "- "
            elif flag:
                msg = "+ "
            else:
                msg = ""
            flag = True
            coef = abs(coef)
            if coef != 1 or i == 0:
                msg += str(coef)
            if i > 0:
                if coef != 1:
                    msg += " * "
                msg += "x"
            if i > 1:
                msg += f"^{i}"
            msgs.append(msg)
        return " ".join(msgs)

    def eval(self, node: Parameter, derivate: int = 0) -> Any:
        """
        Evaluates the polynomial p(t) at given node t

        Parameters
        ----------
        node: Parameter
            The value of t to compute p(t)
        derivate: int
            Number of times to derivate the polynomial

        Example
        -------
        >>> poly = Polynomial([1, 2])
        >>> poly.eval(0)
        1
        >>> poly.eval(1)
        3
        >>> poly.eval(1, 1)
        2
        >>> poly.eval(1, 2)
        0
        """
        coefs = polyderi(tuple(self), derivate)
        result = 0 * node * self[0]
        for coef in coefs[::-1]:
            result = node * result + coef
        return result

    def derivate(self, times: int = 1) -> Polynomial:
        """
        Derivate the polynomial p(t), giving a new one polynomial

        Parameters
        ----------
        times: int, default = 1
            How many times to derivate p(t)
        return: Polynomial
            The derivated polynomial

        :raises ValueError: If ``times`` is negative

        Example
        -------
        >>> poly = Polynomial([1, 2, 5])
        >>> print(poly)
        1 + 2 * x + 5 * x^2
        >>> dpoly = poly.derivate()
        >>> print(dpoly)
        2 + 10 * x
        """
        coefs = polyderi(tuple(self), times)
        return self.__class__(coefs)

    def integrate(self, times: int = 1) -> Polynomial:
        """
        Integrate the polynomial curve, giving a new one

        Parameters
        ----------
        times: int, default = 1
            Number of times to integrate the polynomial
        return: Polynomial
            The integrated polynomial

        :raises ValueError: If ``times`` is negative

        Example
        -------
        >>> poly = Polynomial([2, 10])
        >>> print(poly)
        2 + 10 * x
        >>> ipoly = poly.integrate()
        >>> print(ipoly)
        2 * x + 5 * x^2
        """
        coefs = polyinte(tuple(self), times)
        return self.__class__(coefs)

    def defintegral(self, lower: Parameter, upper: Parameter) -> Scalar:
        """
        Evaluates the defined integral of the polynomial

        Parameters
        ----------
        lower: Parameter
            The lower bound of integration
        upper: Parameter
            The upper bound of integration
        return: Scalar
            The value of the defined integral

        Example
        -------
        >>> poly = Polynomial([2, 10])
        >>> print(poly)
        2 + 10 * x
        >>> ipoly = poly.integrate()
        >>> print(ipoly)
        2 * x + 5 * x^2
        """
        intself = self.integrate(1)
        return intself.eval(upper) - intself.eval(lower)

    def shift(self, amount: Parameter) -> Polynomial:
        """
        Computes the polynomial q(x) = p(x-d) by
        translating the polynomial by 'd' to the right.

        p(x) = a0 + a1 * x + ... + ap * x^p
        q(x) = b0 + b1 * x + ... + bp * x^p
             = a0 + a1 * (x-d) + ... + ap * (x-d)^p

        Parameters
        ----------
        amount: Parameter
            The quantity to shift the function

        Example
        -------
        >>> old_poly = Polynomial([0, 0, 0, 1])
        >>> print(old_poly)
        x^3
        >>> new_poly = poly.shift(1)  # transform to (x-1)^3
        >>> print(new_poly)
        - 1 + 3 * x - 3 * x^2 + x^3
        """
        newcoefs = list(self)
        for i, coef in enumerate(self):
            for j in range(i):
                value = binom(i, j) * (amount ** (i - j))
                if (i + j) % 2:
                    value *= -1
                newcoefs[j] += coef * value
        return self.__class__(tuple(newcoefs))

    def scale(self, amount: Scalar) -> Polynomial:
        """
        Computes the polynomial q(x) = p(s*x) by
        scaling the polynomial by 's'.

        p(x) = a0 + a1 * x + ... + ap * x^p
        q(x) = b0 + b1 * x + ... + bp * x^p
             = a0 + a1 * (s*x) + ... + ap * (s*x)^p

        Parameters
        ----------
        amount: Parameter
            The quantity to scale the t-axis

        Example
        -------
        >>> old_poly = Polynomial([0, -1, 0, 1])
        >>> print(old_poly)
        - x + x^3
        >>> new_poly = poly.scale(2)  # transform to (2*x)^3
        >>> print(new_poly)
        - 2 * x + 8 * x^3
        """
        coefs = tuple(coef * amount**i for i, coef in enumerate(self))
        return self.__class__(coefs)

    def roots(
        self,
        inflim: Optional[Parameter] = None,
        suplim: Optional[Parameter] = None,
    ) -> Iterable[Parameter]:
        """
        Computes the roots of the polynomial that are
        inside the given interval

        If no interval is given, then it computes in the entire domain

        Parameters
        ----------
        inflim: Optional[Parameter], default = None
            The lower bound of research
        suplim: Optional[Parameter], default = None
            The upper bound of research

        Example
        -------
        >>> poly = Polynomial.from_roots([1, 1, 2, 3, -4])
        >>> poly.roots()
        (-4, 1, 1, 2, 3)
        >>> poly.roots(0, 2)
        (1, 1, 2)
        """
        nodes = find_roots(self)
        if inflim is not None:
            nodes = (node for node in nodes if inflim <= node)
        if suplim is not None:
            nodes = (node for node in nodes if node <= suplim)
        return tuple(sorted(nodes))


def integer_polynomial(poly: Polynomial) -> Polynomial:
    """
    Transform a polynomial into another one, only by scaling

    Example
    -------
    4 + 4*x + 8*x^2 -> 1 + x + 2*x^2
    """
    denoms = tuple(
        1 if isinstance(coef, int) else coef.denominator for coef in poly
    )
    denom = lcm(*denoms)
    coefs = tuple(int(denom * coef) for coef in poly)
    denom = gcd(*coefs)
    coefs = tuple(coef // denom for coef in coefs)
    return Polynomial(coefs)


def find_rational_roots(poly: Polynomial) -> Tuple[Fraction, ...]:
    """
    Find all the rational roots by using
    the rational roots theorem:

    If the coefficients of the polynomial are integers,
    then it may have rational roots made by (p/q),
    where (p, q) are the divisors of the the coefficients
    """
    if not isinstance(poly, Polynomial):
        raise TypeError
    if poly.degree == 0:
        raise ValueError
    if poly.degree == 1:
        return (-poly[0] / poly[1],)
    if not poly[0]:
        poly = Polynomial(tuple(poly)[1:])
        other_roots = find_rational_roots(poly)
        return tuple(sorted(other_roots + (0,)))
    if not all(isinstance(coef, (int, Fraction)) for coef in poly):
        return tuple()
    poly = integer_polynomial(poly)
    const = abs(poly[0])
    last = abs(poly[-1])
    constdivs = tuple(divisors(const))
    lastdivs = tuple(divisors(last))
    roots = set()
    for numi in constdivs:
        for denj in lastdivs:
            frac = Fraction(numi, denj)
            if not poly.eval(frac):
                roots.add(frac)
            if not poly.eval(-frac):
                roots.add(-frac)
    roots = tuple(sorted(roots))
    poly = simplify_poly_by_roots(poly, roots)
    if len(roots) > 0 and poly.degree > 0:
        roots = roots + find_rational_roots(poly)
    return tuple(sorted(roots))


def find_numerical_roots(poly: Polynomial) -> Tuple[float]:
    """
    Find numerically all the roots of a polynomial using Newton's method
    """
    if not isinstance(poly, Polynomial):
        raise TypeError
    if poly.degree == 0:
        raise ValueError
    if poly.degree == 1:
        return (-poly[0] / poly[1],)
    degree = poly.degree

    coefs = tuple(coef / poly[degree] for coef in poly)
    if poly.degree == 1:
        return (-coefs[0],)
    delta = coefs[degree - 1] ** 2 - 2 * degree * coefs[degree - 2] / (
        degree - 1
    )
    if delta < 0:
        return tuple()

    liminf = (-coefs[degree - 1] - (degree - 1) * Math.sqrt(delta)) / degree
    limsup = (-coefs[degree - 1] + (degree - 1) * Math.sqrt(delta)) / degree
    maxabs = max(abs(liminf), abs(limsup))
    roots = list(np.linspace(-maxabs, maxabs, 2 * degree + 1))
    for _ in range(3):  # Filter roots three times
        for i, root in enumerate(roots):
            for _ in range(10):  # Newton's iteration
                numer = poly.eval(root, 0)
                if not numer:
                    break
                denom = poly.eval(root, 1)
                if not denom:
                    root = 0
                    continue
                root -= numer / denom
            roots[i] = root
        roots = tuple(set(roots))
        values = tuple(map(poly.eval, roots))
        minval = min(map(abs, values))
        roots = [r for r, v in zip(roots, values) if abs(v) == minval]
    if minval > 1e-12:
        raise ValueError(f"Roots {roots} found are not valid: {values}")
    poly = simplify_poly_by_roots(poly, roots)
    if poly.degree:
        roots += list(find_numerical_roots(poly))
    return tuple(sorted(roots))


def find_roots(poly: Polynomial) -> Tuple[Parameter, ...]:
    """
    Find all real roots from the polynomial.

    It finds at first all the rational roots.
    For the remaining, it finds using numerical method

    Example
    -------
    >>> find_roots(Polynomial([-1, 1]))  # x - 1
    (1, )
    >>> find_roots(Polynomial([-2, 1]))  # x - 2
    (2, )
    >>> find_roots(Polynomial([1, -2, 1]))  # x^2 - 2x + 1
    (1, 1)
    >>> find_roots(Polynomial([3, -4, 1]))  # x^2 - 4x + 3
    (1, 3)
    >>> find_roots(Polynomial([1, 0, 1]))  # x^2 + 1
    ()
    """
    if not isinstance(poly, Polynomial):
        raise TypeError
    if poly.degree == 0:
        raise ValueError
    rational_roots = find_rational_roots(poly)
    if rational_roots:
        if len(rational_roots) == poly.degree:
            return rational_roots
        poly = simplify_poly_by_roots(poly, rational_roots)
    numerical_roots = find_numerical_roots(poly)
    return tuple(sorted(numerical_roots + rational_roots))


def simplify_poly_by_roots(
    poly: Polynomial, roots: Iterable[Parameter]
) -> Polynomial:
    """
    Divide the polynomial for the roots.

    This function doesn't check if the polynomial
    has indeed that root
    """
    for root in roots:
        poly //= Polynomial((-root, 1))
    return poly
