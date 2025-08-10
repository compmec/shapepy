"""
Defines the Bezier class, that has the same basis as the Polynomial
"""

from __future__ import annotations

from copy import copy
from functools import lru_cache
from typing import Iterable, Tuple, Union

from ..scalar.quadrature import inner
from ..scalar.reals import Math, Rational, Real
from ..tools import Is, To
from .base import BaseAnalytic
from .polynomial import Polynomial


@lru_cache(maxsize=None)
def bezier_caract_matrix(degree: int) -> Tuple[Tuple[Rational, ...], ...]:
    """Returns the matrix [M] with the polynomial coefficients

    [M]_{ij} = coef(x^{degree-j} from B_{i,p}(x))

    p = degree

    B_{i, p} = binom(p, i) * (1-u)^{p-i} * u^i
             = binom(p, i) * sum_{j=0}^{p-i} (-1)^{} * u^{i+(p-i)}

    """
    if not Is.integer(degree) or degree < 0:
        raise ValueError("Degree must be a non-negative integer")
    matrix = [[0] * (degree + 1) for _ in range(degree + 1)]
    for i in range(degree + 1):
        for j in range(degree - i + 1):
            val = Math.binom(degree, i) * Math.binom(degree - i, j)
            matrix[degree - j][i] = -val if (degree + i + j) % 2 else val
    return tuple(map(tuple, matrix))


@lru_cache(maxsize=None)
def inverse_caract_matrix(degree: int) -> Tuple[Tuple[Rational, ...], ...]:
    """
    Returns the inverse matrix of the caract bezier matrix
    """
    if not Is.integer(degree) or degree < 0:
        raise ValueError("Degree must be a non-negative integer")
    matrix = [[0] * (degree + 1) for _ in range(degree + 1)]
    for i in range(degree + 1):
        for j in range(degree - i + 1):
            val = To.rational(Math.binom(degree - j, i), Math.binom(degree, i))
            matrix[degree - j][i] = val
    return tuple(map(tuple, matrix))


def bezier2polynomial(bezier: Bezier) -> Polynomial:
    """
    Converts a Bezier instance to Polynomial
    """
    matrix = bezier_caract_matrix(bezier.degree)
    poly_coefs = (inner(weights, bezier) for weights in matrix)
    return To.polynomial(poly_coefs)


def polynomial2bezier(polynomial: Polynomial) -> Bezier:
    """
    Converts a Polynomial instance to a Bezier
    """
    matrix = inverse_caract_matrix(polynomial.degree)
    ctrlpoints = tuple(inner(weights, polynomial) for weights in matrix)
    return Bezier(ctrlpoints)


class Bezier(BaseAnalytic):
    """
    Defines the Bezier class, that allows evaluating and operating
    such as adding, subtracting, multiplying, etc
    """

    def __init__(self, coefs: Iterable[Real]):
        super().__init__(coefs)
        self.__polynomial = bezier2polynomial(self)

    @property
    def degree(self) -> int:
        """
        Returns the degree of the polynomial, which is the
        highest power of t with a non-zero coefficient.
        If the polynomial is constant, returns 0.
        """
        return self.ncoefs - 1

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Bezier):
            return self.__polynomial == bezier2polynomial(value)
        if isinstance(value, Polynomial):
            return self.__polynomial == value
        if Is.real(value):
            return all(ctrlpoint == value for ctrlpoint in self)
        return NotImplemented

    def __add__(self, other: Union[Real, Polynomial, Bezier]) -> Bezier:
        if Is.instance(other, Bezier):
            other = bezier2polynomial(other)
        sumpoly = self.__polynomial + other
        return polynomial2bezier(sumpoly)

    def __mul__(self, other: Union[Real, Polynomial, Bezier]) -> Bezier:
        if Is.instance(other, Bezier):
            other = bezier2polynomial(other)
        mulpoly = self.__polynomial * other
        return polynomial2bezier(mulpoly)

    def __matmul__(self, other: Union[Real, Polynomial, Bezier]) -> Bezier:
        if Is.instance(other, Bezier):
            other = bezier2polynomial(other)
        matmulpoly = self.__polynomial @ other
        return polynomial2bezier(matmulpoly)

    def __call__(self, node: Real, derivate: int = 0) -> Real:
        return self.__polynomial(node, derivate)

    def __str__(self):
        return str(self.__polynomial)

    def clean(self) -> Bezier:
        """
        Decreases the degree of the bezier curve if possible
        """
        return polynomial2bezier(bezier2polynomial(self).clean())

    def scale(self, amount: Real) -> Bezier:
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
        return polynomial2bezier(bezier2polynomial(self).scale(amount))

    def shift(self, amount: Real) -> Bezier:
        """
        Transforms the bezier p(t) into p(t-d) by
        translating the bezier by 'd' to the right.
        """
        return polynomial2bezier(bezier2polynomial(self).shift(amount))

    def integrate(self, times: int = 1) -> Bezier:
        """
        Integrates the bezier analytic

        Example
        -------
        >>> poly = Polynomial([1, 2, 5])
        >>> print(poly)
        1 + 2 * t + 5 * t^2
        >>> ipoly = integrate(poly)
        >>> print(ipoly)
        t + t^2 + (5/3) * t^3
        """
        return polynomial2bezier(bezier2polynomial(self).integrate(times))

    def derivate(self, times: int = 1) -> Bezier:
        """
        Derivate the bezier curve, giving a new one
        """
        return polynomial2bezier(bezier2polynomial(self).derivate(times))


def split(bezier: Bezier, nodes: Iterable[Real]) -> Iterable[Bezier]:
    """
    Splits the bezier curve into segments
    """
    nodes = (node for node in nodes if 0 < node < 1)
    nodes = tuple([0] + sorted(nodes) + [1])
    poly = bezier2polynomial(bezier)
    for knota, knotb in zip(nodes, nodes[1:]):
        newpoly = copy(poly).shift(-knota).scale(knotb - knota)
        yield polynomial2bezier(newpoly)


def to_bezier(coefs: Iterable[Real]) -> Bezier:
    """
    Creates a Bezier instance
    """
    return Bezier(coefs).clean()


To.bezier = to_bezier
