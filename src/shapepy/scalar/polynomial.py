"""
Implementation of a polynomial class
"""

from __future__ import annotations

from numbers import Real
from typing import Iterable, List, Union

from ..tools import Is, pow_keys
from .reals import Math


class Polynomial:
    """
    Defines a polynomial with coefficients

    p(t) = a0 + a1 * t + a2 * t^2 + ... + ap * t^p

    By receiving the coefficients

    coefs = [a0, a1, a2, ..., ap]

    This class allows evaluating, adding, multiplying, etc

    Example
    -------
    >>> poly = Polynomial([3, 2])
    >>> print(poly)
    3 + 2 * t
    >>> poly(0)
    3
    >>> poly(1)
    5
    """

    def __init__(self, coefs: Iterable[Real]):
        if not Is.iterable(coefs):
            raise TypeError("Expected an iterable of coefficients")
        coefs = tuple(coefs)
        if len(coefs) == 0:
            raise ValueError("Cannot receive an empty tuple")
        if Is.real(coefs[0]):
            degree = max((i for i, v in enumerate(coefs) if v), default=0)
        else:
            degree = max((i for i, v in enumerate(coefs) if v @ v), default=0)
        coefs = coefs[: degree + 1]
        self.__coefs = tuple(coefs[: degree + 1])

    @property
    def degree(self) -> int:
        """
        Returns the degree of the polynomial, which is the
        highest power of t with a non-zero coefficient.
        If the polynomial is constant, returns 0.
        """
        return len(self.__coefs) - 1

    def __eq__(self, value: object) -> bool:
        if Is.instance(value, Polynomial):
            return tuple(self) == tuple(value)
        if Is.real(value):
            return self.degree == 0 and value == self[0]
        return NotImplemented

    def __iter__(self):
        yield from self.__coefs

    def __getitem__(self, index):
        return self.__coefs[index]

    def __neg__(self) -> Polynomial:
        return self.__class__(-coef for coef in self)

    def __add__(self, other: Union[Real, Polynomial]) -> Polynomial:
        if not Is.instance(other, Polynomial):
            coefs = list(self)
            coefs[0] += other
            return self.__class__(coefs)
        coefs = [0] * (1 + max(self.degree, other.degree))
        for i, coef in enumerate(self):
            coefs[i] += coef
        for i, coef in enumerate(other):
            coefs[i] += coef
        return self.__class__(coefs)

    def __mul__(self, other: Union[Real, Polynomial]) -> Polynomial:
        if Is.instance(other, Polynomial):
            coefs = [0 * self[0]] * (self.degree + other.degree + 1)
            for i, coefi in enumerate(self):
                for j, coefj in enumerate(other):
                    coefs[i + j] += coefi * coefj
        else:
            coefs = tuple(other * coef for coef in self)
        return self.__class__(coefs)

    def __matmul__(self, other: Union[Real, Polynomial]) -> Polynomial:
        if not isinstance(other, Polynomial):
            return self.__class__((coef @ other for coef in self))
        coefs = [0 * (self[0] @ self[0])] * (self.degree + other.degree + 1)
        for i, coefi in enumerate(self):
            for j, coefj in enumerate(other):
                coefs[i + j] += coefi @ coefj
        return self.__class__(coefs)

    def __pow__(self, exponent: int) -> Polynomial:
        if not Is.integer(exponent) or exponent < 0:
            raise ValueError
        if not Is.finite(self[0]):
            raise ValueError
        if exponent == 0:
            return self.__class__([1 + 0 * self[0]])
        cache = {1: self}
        for n in pow_keys(exponent):
            cache[n] = cache[n // 2] * cache[n - n // 2]
        return cache[exponent]

    def __sub__(self, other: Union[Real, Polynomial]) -> Polynomial:
        return self.__add__(-other)

    def __rsub__(self, other: Real) -> Polynomial:
        return (-self).__add__(other)

    def __radd__(self, other: Real) -> Polynomial:
        return self.__add__(other)

    def __rmul__(self, other: Real) -> Polynomial:
        return self.__mul__(other)

    def __call__(self, node: Real) -> Real:
        if self.degree == 0:
            return self[0]
        result: Real = 0 * self[0]
        for coef in self[::-1]:
            result = node * result + coef
        return result

    def __str__(self):
        if self.degree == 0:
            return str(self[0])
        msgs: List[str] = []
        if not Is.real(self[0]):
            msgs.append(f"({self[0]})")
            if self.degree > 0:
                msgs.append(f"({self[1]}) * t")
            for i, coef in enumerate(self[2:]):
                msgs.append(f"({coef}) * t^{i+2}")
            return " + ".join(msgs)
        flag = False
        for i, coef in enumerate(self):
            if coef == 0:
                continue
            msg = "- " if coef < 0 else "+ " if flag else ""
            flag = True
            coef = abs(coef)
            if coef != 1 or i == 0:
                msg += str(coef)
            if i > 0:
                if coef != 1:
                    msg += " * "
                msg += "t"
            if i > 1:
                msg += f"^{i}"
            msgs.append(msg)
        return " ".join(msgs)

    def __repr__(self) -> str:
        return str(self)


def scale(polynomial: Polynomial, amount: Real) -> Polynomial:
    """
    Transforms the polynomial p(t) into p(A*t) by
    scaling the argument of the polynomial by 'A'.

    p(t) = a0 + a1 * t + ... + ap * t^p
    p(A * t) = a0 + a1 * (A*t) + ... + ap * (A * t)^p
             = b0 + b1 * t + ... + bp * t^p

    Example
    -------
    >>> old_poly = Polynomial([0, 0, 0, 1])
    >>> print(old_poly)
    t^3
    >>> new_poly = scale(poly, 1)  # transform to (t-1)^3
    >>> print(new_poly)
    - 1 + 3 * t - 3 * t^2 + t^3
    """
    coefs = tuple(coef * amount**i for i, coef in enumerate(polynomial))
    return Polynomial(coefs)


def shift(polynomial: Polynomial, amount: Real) -> Polynomial:
    """
    Transforms the polynomial p(t) into p(t-d) by
    translating the polynomial by 'd' to the right.

    p(t) = a0 + a1 * t + ... + ap * t^p
    p(t-d) = a0 + a1 * (t-d) + ... + ap * (t-d)^p
            = b0 + b1 * t + ... + bp * t^p

    Example
    -------
    >>> old_poly = Polynomial([0, 0, 0, 1])
    >>> print(old_poly)
    t^3
    >>> new_poly = shift(poly, 1)  # transform to (t-1)^3
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
    return Polynomial(newcoefs)


def derivate(polynomial: Polynomial, times: int = 1) -> Polynomial:
    """
    Derivate the polynomial curve, giving a new one

    Example
    -------
    >>> poly = Polynomial([1, 2, 5])
    >>> print(poly)
    1 + 2 * t + 5 * t^2
    >>> dpoly = poly.derivate()
    >>> print(dpoly)
    2 + 10 * t
    """
    if polynomial.degree < times:
        return Polynomial([0 * polynomial[0]])
    coefs = (
        Math.factorial(n + times) // Math.factorial(n) * coef
        for n, coef in enumerate(polynomial[times:])
    )
    return Polynomial(coefs)


def integrate(polynomial: Polynomial) -> Polynomial:
    """
    Integrates the polynomial curve on the interval

    Example
    -------
    >>> poly = Polynomial([1, 2, 5])
    >>> print(poly)
    1 + 2 * t + 5 * t^2
    >>> dpoly = integrate(poly)
    >>> print(dpoly)
    t + t^2 + (5/3) * t^3
    """
    newcoefs = [0 * polynomial[0]]
    newcoefs += list(coef / (n + 1) for n, coef in enumerate(polynomial))
    return Polynomial(newcoefs)
