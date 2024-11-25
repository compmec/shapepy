"""
This file contains a class Polynomial that allows evaluating and
making operations with polynomials, like adding, multiplying, etc
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import Any, Iterable, Tuple, Union

from ..core import IAnalytic, Parameter, Scalar


@lru_cache
def factorial(n: int) -> int:
    return math.factorial(int(n))


@lru_cache
def binom(n: int, i: int) -> int:
    return math.comb(n, i)


@lru_cache
def keys(exp):
    if exp == 1:
        return set()
    return keys(exp // 2) | keys(exp - exp // 2) | {exp}


def polyderi(poly: Tuple[Scalar, ...], times: int) -> Tuple[Scalar, ...]:
    times = int(times)
    if times < 0:
        raise ValueError
    if times == 0:
        return poly
    if times >= len(poly):
        return (0 * sum(poly),)
    return tuple(
        coef * (factorial(n + times) // factorial(n))
        for n, coef in enumerate(poly[times:])
    )


def polyinte(poly: Tuple[Scalar, ...], times: int) -> Tuple[Scalar, ...]:
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


class Polynomial(IAnalytic):
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

    def __init__(self, coefs: Iterable[Any]):
        coefs = tuple(coefs)
        degree = max((i for i, coef in enumerate(coefs) if coef), default=0)
        self.__coefs = coefs[: degree + 1]

    @property
    def degree(self) -> int:
        """
        Gives the degree of the polynomial
        """
        return len(self.__coefs) - 1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Polynomial):
            other = Polynomial([other])
        if self.degree != other.degree:
            return False
        return all(ci == cj for ci, cj in zip(self, other))

    def __iter__(self):
        yield from self.__coefs

    def __getitem__(self, index):
        return self.__coefs[index]

    def __neg__(self) -> Polynomial:
        coefs = tuple(-coef for coef in self)
        return self.__class__(coefs)

    def __add__(self, other: Union[Any, Polynomial]) -> Polynomial:
        if not isinstance(other, Polynomial):
            other = Polynomial([other])
        coefs = [0] * (1 + max(self.degree, other.degree))
        for i, coef in enumerate(self):
            coefs[i] += coef
        for i, coef in enumerate(other):
            coefs[i] += coef
        return self.__class__(coefs)

    def __mul__(self, other: Union[Any, Polynomial]) -> Polynomial:
        if not isinstance(other, Polynomial):
            other = Polynomial([other])
        coefs = [0] * (1 + self.degree + other.degree)
        for i, ci in enumerate(self):
            for j, cj in enumerate(other):
                coefs[i + j] += ci * cj
        return self.__class__(coefs)

    def __divmod__(
        self, other: Union[Any, Polynomial]
    ) -> Tuple[Polynomial, Polynomial]:
        if not isinstance(other, Polynomial):
            coefs = (coef / other for coef in self)
            return Polynomial(coefs), Polynomial([0 * sum(self)])
        zero = 0 * (sum(self) + sum(other))
        qoly = Polynomial([zero])
        roly = self - other * qoly
        while roly.degree >= other.degree:
            coef = roly[-1] / other[-1]
            coefs = [0] * (roly.degree - other.degree) + [coef]
            qoly += Polynomial(coefs)
            roly = self - other * qoly
        return qoly, roly

    def __floordiv__(self, other: Union[Any, Polynomial]) -> Polynomial:
        return self.__divmod__(other)[0]

    def __mod__(self, other: Union[Any, Polynomial]) -> Polynomial:
        return self.__divmod__(other)[1]

    def __truediv__(self, other: Scalar) -> Polynomial:
        div, res = self.__divmod__(other)
        if res != 0:
            raise ValueError(f"Cannot divide {self} by {other}")
        return div

    def __pow__(self, exponent: int) -> Polynomial:
        exponent = int(exponent)
        if exponent < 0:
            raise ValueError
        if exponent == 0:
            return self.__class__([1 + 0 * sum(self)])
        needs = sorted(keys(exponent))
        cache = {1: self}
        for n in needs:
            cache[n] = cache[n // 2] * cache[n - n // 2]
        return cache[exponent]

    def __sub__(self, other: Union[Any, Polynomial]) -> Polynomial:
        return self.__add__(-other)

    def __rsub__(self, other: Any) -> Polynomial:
        return (-self).__add__(other)

    def __radd__(self, other: Any) -> Polynomial:
        return self.__add__(other)

    def __rmul__(self, other: Any) -> Polynomial:
        return self.__mul__(other)

    def __call__(self, node: Parameter) -> Any:
        return self.eval(node, 0)

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

    def __repr__(self) -> str:
        return str(self)

    def eval(self, node: Parameter, derivate: int = 0) -> Any:
        """
        Evaluates the polynomial at given node

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
        coefs = polyderi(self.__coefs, derivate)
        result = 0 * node
        for coef in coefs[::-1]:
            result = node * result + coef
        return result

    def derivate(self, times: int = 1) -> Polynomial:
        """
        Derivate the polynomial curve, giving a new one

        Example
        -------
        >>> poly = Polynomial([1, 2, 5])
        >>> print(poly)
        1 + 2 * x + 5 * x^2
        >>> dpoly = poly.derivate()
        >>> print(dpoly)
        2 + 10 * x
        """
        coefs = polyderi(self.__coefs, times)
        return self.__class__(coefs)

    def integrate(self, times: int = 1) -> Polynomial:
        """
        Integrate the polynomial curve, giving a new one

        Example
        -------
        >>> poly = Polynomial([2, 10])
        >>> print(poly)
        2 + 10 * x
        >>> ipoly = poly.integrate()
        >>> print(ipoly)
        2 * x + 5 * x^2
        """
        coefs = polyinte(self.__coefs, times)
        return self.__class__(coefs)

    def defintegral(self, lower: Parameter, upper: Parameter) -> Scalar:
        intself = self.integrate(1)
        return intself.eval(upper) - intself.eval(lower)

    def shift(self, amount: Parameter) -> Polynomial:
        """
        Transforms the polynomial p(x) into p(x-d) by
        translating the curve by 'd' to the right.

        p(x) = a0 + a1 * x + ... + ap * x^p
        p(x-d) = a0 + a1 * (x-d) + ... + ap * (x-d)^p
               = b0 + b1 * x + ... + bp * x^p

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
        coefs = tuple(coef * amount**i for i, coef in enumerate(self))
        return self.__class__(coefs)


def find_roots(poly: Polynomial) -> Tuple[Parameter, ...]:
    """
    Find all real roots from the polynomial.

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
    degree = poly.degree
    coefs = tuple(coef / poly[degree] for coef in poly)
    if poly.degree == 1:
        return (-coefs[0],)
    delta = coefs[degree - 1] ** 2 - 2 * degree * coefs[degree - 2] / (
        degree - 1
    )
    if delta < 0:  # No roots
        return tuple()
    liminf = (-coefs[degree - 1] - (degree - 1) * math.sqrt(delta)) / degree
    limsup = (-coefs[degree - 1] + (degree - 1) * math.sqrt(delta)) / degree
    root = -coefs[degree - 1]
    for _ in range(10):  # Newton's iteration
        numer = poly.eval(root, 0)
        if not numer:
            break
        denom = poly.eval(root, 1)
        if not denom:
            root = limsup
            continue
        root -= poly.eval(root) / denom
        root = max(liminf, min(limsup, root))

    doly = Polynomial((-root, 1))
    qoly, roly = divmod(poly, doly)
    if roly != 0:
        raise NotImplementedError
    return tuple(sorted(find_roots(qoly) + (root,)))
