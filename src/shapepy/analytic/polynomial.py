"""
Implementation of a polynomial class
"""

from __future__ import annotations

from numbers import Real
from typing import Iterable, Iterator, List, Union

from ..rbool import IntervalR1, SubSetR1, WholeR1, from_any, move, scale
from ..rbool.tools import is_continuous
from ..scalar.reals import Math
from ..tools import Is, To
from .base import IAnalytic


def scale_coefs(coefs: Iterable[Real], amount: Real) -> Iterator[Real]:
    """Computes the polynomial p(t/A) from the coefficients of p(t)"""
    if amount != 1:
        inv = 1 / amount
        coefs = (coef * inv**i for i, coef in enumerate(coefs))
    yield from coefs


def shift_coefs(coefs: Iterable[Real], amount: Real) -> Iterator[Real]:
    """Computes the polynomial p(t-a) from the coefficients of p(t)"""
    if amount != 0:
        coefs = list(coefs)
        for i, coef in enumerate(tuple(coefs)):
            for j in range(i):
                value = Math.binom(i, j) * (amount ** (i - j))
                if (i + j) % 2:
                    value *= -1
                coefs[j] += coef * value
    yield from coefs


class Polynomial(IAnalytic):
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

    def __init__(
        self, coefs: Iterable[Real], *, domain: Union[None, SubSetR1] = None
    ):
        domain = WholeR1() if domain is None else from_any(domain)
        if not is_continuous(domain):
            raise ValueError(f"Domain {domain} is not continuous")
        if not Is.iterable(coefs):
            raise TypeError("Expected an iterable of coefficients")
        coefs = tuple(coefs)
        if len(coefs) == 0:
            raise ValueError("Cannot receive an empty tuple")
        degree = max((i for i, v in enumerate(coefs) if v * v > 0), default=0)
        self.__coefs = coefs[: degree + 1]
        self.__domain = domain

    @property
    def domain(self) -> SubSetR1:
        return self.__domain

    @property
    def degree(self) -> int:
        """
        Returns the degree of the polynomial, which is the
        highest power of t with a non-zero coefficient.
        If the polynomial is constant, returns 0.
        """
        return len(self.__coefs) - 1

    def __iter__(self):
        yield from self.__coefs

    def __getitem__(self, index):
        return self.__coefs[index]

    def __eq__(self, other: object) -> bool:
        if not Is.instance(other, IAnalytic):
            if Is.finite(other):
                return self.degree == 0 and self[0] == other
            return NotImplemented
        return (
            Is.instance(other, Polynomial)
            and other.degree == self.degree
            and self.domain == other.domain
            and tuple(self) == tuple(other)
        )

    def __add__(self, other: Union[Real, Polynomial]) -> Polynomial:
        if not Is.instance(other, IAnalytic):
            coefs = list(self)
            coefs[0] += other
            return Polynomial(coefs, domain=self.domain)
        if not Is.instance(other, Polynomial):
            return NotImplemented
        coefs = [0] * (1 + max(self.degree, other.degree))
        for i, coef in enumerate(self):
            coefs[i] += coef
        for i, coef in enumerate(other):
            coefs[i] += coef
        return Polynomial(coefs, domain=self.domain)

    def __mul__(self, other: Union[Real, Polynomial]) -> Polynomial:
        if not Is.instance(other, IAnalytic):
            return Polynomial(
                (other * coef for coef in self), domain=self.domain
            )
        if not Is.instance(other, Polynomial):
            return NotImplemented
        coefs = [0 * self[0]] * (self.degree + other.degree + 1)
        for i, coefi in enumerate(self):
            for j, coefj in enumerate(other):
                coefs[i + j] += coefi * coefj
        return Polynomial(coefs, domain=self.domain & other.domain)

    def eval(self, node: Real, derivate: int = 0) -> Real:
        if node not in self.domain:
            raise ValueError(f"Node {node} not in {self.domain}")
        if derivate == 0:
            coefs = self.__coefs
        elif self.degree < derivate:
            coefs = (0 * self.__coefs[0],)
        else:
            coefs = tuple(
                Math.factorial(n + derivate) // Math.factorial(n) * coef
                for n, coef in enumerate(self.__coefs[derivate:])
            )
        node = To.real(node)
        if len(coefs) == 1:
            return coefs[0]
        if Is.infinity(node):
            return coefs[len(coefs) - 1] * (
                Math.NEGINF
                if self.degree % 2 and node == Math.NEGINF
                else Math.POSINF
            )
        result: Real = 0 * coefs[0]
        for coef in coefs[::-1]:
            result = node * result + coef
        return result

    def derivate(self, times=1):
        if self.degree < times:
            return Polynomial([0 * self[0]], domain=self.domain)
        coefs = (
            Math.factorial(n + times) // Math.factorial(n) * coef
            for n, coef in enumerate(self[times:])
        )
        return Polynomial(coefs, domain=self.domain)

    def integrate(self, domain):
        domain = from_any(domain)
        if domain not in self.domain:
            raise ValueError(
                f"Given domain {domain} is not subset of {self.domain}"
            )
        if not Is.instance(domain, IntervalR1):
            raise ValueError(f"Cannot integrate over {domain}")
        left, right = domain[0], domain[1]
        potencias = [1]
        result = 0
        for i, coef in enumerate(self):
            result += coef * sum(potencias) / (i + 1)
            potencias.append(right * potencias[-1])
            for j in range(i + 1):
                potencias[j] *= left
        return result * (right - left)

    def compose(self, function: IAnalytic) -> Polynomial:
        if not Is.instance(function, Polynomial):
            raise TypeError(f"Analytic {type(function)} is not suported")
        if function.degree != 1:
            raise ValueError("Only polynomials of degree = 1 are allowed")
        shift_amount, scale_amount = tuple(function)
        coefs = shift_coefs(scale_coefs(self, scale_amount), shift_amount)
        domain = move(scale(self.domain, scale_amount), shift_amount)
        return Polynomial(coefs, domain=domain)

    def __repr__(self):
        return str(self.domain) + ": " + self.__str__()

    def __str__(self):
        if self.degree == 0:
            return str(self[0])
        msgs: List[str] = []
        flag = False
        for i, coef in enumerate(self):
            if coef * coef == 0:
                continue
            msg = "- " if Is.real(coef) and coef < 0 else "+ " if flag else ""
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
