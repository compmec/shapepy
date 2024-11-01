"""
This file contains a class Polynomial that allows evaluating and
making operations with polynomials, like adding, multiplying, etc
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import Any, Iterable, List, Tuple, Union

from ...core import Parameter, Scalar


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


def polymult(
    poly: Tuple[Scalar, ...], qoly: Tuple[Scalar, ...]
) -> Tuple[Scalar, ...]:
    """
    Multiplies two polynomials
    """
    woly: List[Scalar] = [0] * (len(poly) + len(qoly) - 1)
    for i, pi in enumerate(poly):
        for j, qj in enumerate(qoly):
            woly[i + j] += pi * qj
    return tuple(woly)


def polypow(poly: Tuple[Scalar, ...], exp: int) -> Tuple[Scalar, ...]:
    exp = int(exp)
    if exp < 0:
        raise ValueError
    if exp == 0:
        return (1 + 0 * sum(poly),)
    poly = tuple(poly)
    needs = sorted(keys(exp))
    cache = {1: poly}
    for n in needs:
        cache[n] = polymult(cache[n // 2], cache[n - n // 2])
    return cache[exp]


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


class Polynomial:
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
        self.__coefs = tuple(coefs)

    @property
    def degree(self) -> int:
        """
        Gives the degree of the polynomial
        """
        return len(self.__coefs) - 1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Polynomial):
            return False
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
        if isinstance(other, Polynomial):
            coefs = [0] * (1 + max(self.degree, other.degree))
            for i, coef in enumerate(self):
                coefs[i] += coef
            for i, coef in enumerate(other):
                coefs[i] += coef
        else:
            coefs = list(self)
            coefs[0] += other
        return self.__class__(tuple(coefs))

    def __mul__(self, other: Union[Any, Polynomial]) -> Polynomial:
        if isinstance(other, Polynomial):
            coefs = polymult(tuple(self), tuple(other))
        else:
            coefs = tuple(other * coef for coef in self)
        return self.__class__(coefs)

    def __truediv__(self, other: Scalar) -> Polynomial:
        coefs = tuple(coef / other for coef in self)
        return self.__class__(coefs)

    def __pow__(self, other: int) -> Polynomial:
        coefs = polypow(self.__coefs, other)
        return self.__class__(coefs)

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
        if all(coef == 0 for coef in self):
            return "0"
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
        if len(coefs) == 1:
            return coefs[0]
        result = 0 * coefs[0]
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
