"""
Implementation of a polynomial class
"""

from __future__ import annotations

from numbers import Real
from typing import Iterable, List, Union

from ..scalar.reals import Math
from ..tools import Is, To
from .base import BaseAnalytic


class Polynomial(BaseAnalytic):
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

    @property
    def degree(self) -> int:
        """
        Returns the degree of the polynomial, which is the
        highest power of t with a non-zero coefficient.
        If the polynomial is constant, returns 0.
        """
        return self.ncoefs - 1

    def __eq__(self, other: object) -> bool:
        if Is.instance(other, Polynomial):
            return tuple(self.clean()) == tuple(other.clean())
        if Is.real(other):
            cself = self.clean()
            return cself.degree == 0 and cself[0] == other
        return NotImplemented

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

    def clean(self) -> Polynomial:
        """
        Decreases the degree of the bezier curve if possible
        """
        if Is.real(self[0]):
            degree = max((i for i, v in enumerate(self) if v), default=0)
        else:
            degree = max((i for i, v in enumerate(self) if v @ v), default=0)
        return Polynomial(self[: degree + 1])

    def scale(self, amount: Real) -> Polynomial:
        """
        Transforms the polynomial p(t) into p(A*t) by
        scaling the argument of the polynomial by 'A'.

        p(t) = a0 + a1 * t + ... + ap * t^p
        p(A * t) = a0 + a1 * (A*t) + ... + ap * (A * t)^p
                = b0 + b1 * t + ... + bp * t^p

        Example
        -------
        >>> old_poly = Polynomial([0, 2, 0, 1])
        >>> print(old_poly)
        2 * t + t^3
        >>> new_poly = scale(poly, 2)
        >>> print(new_poly)
        4 * t + 8 * t^3
        """
        coefs = tuple(coef * amount**i for i, coef in enumerate(self))
        return Polynomial(coefs)

    def shift(self, amount: Real) -> Polynomial:
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
        newcoefs = list(self)
        for i, coef in enumerate(self):
            for j in range(i):
                value = Math.binom(i, j) * (amount ** (i - j))
                if (i + j) % 2:
                    value *= -1
                newcoefs[j] += coef * value
        return Polynomial(newcoefs)

    def integrate(self, times: int = 1) -> Polynomial:
        """
        Integrates the polynomial curve

        Example
        -------
        >>> poly = Polynomial([1, 2, 5])
        >>> print(poly)
        1 + 2 * t + 5 * t^2
        >>> ipoly = integrate(poly)
        >>> print(ipoly)
        t + t^2 + (5/3) * t^3
        """
        polynomial = self
        for _ in range(times):
            newcoefs = [0 * polynomial[0]]
            newcoefs += list(
                coef / (n + 1) for n, coef in enumerate(polynomial)
            )
            polynomial = Polynomial(newcoefs)
        return polynomial

    def derivate(self, times: int = 1) -> Polynomial:
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
        if self.degree < times:
            return Polynomial([0 * self[0]])
        coefs = (
            Math.factorial(n + times) // Math.factorial(n) * coef
            for n, coef in enumerate(self[times:])
        )
        return Polynomial(coefs)


def to_polynomial(coeficients: Iterable[Real]) -> Polynomial:
    """
    Creates a polynomial instance from given coefficients
    """
    return Polynomial(coeficients).clean()


To.polynomial = to_polynomial
