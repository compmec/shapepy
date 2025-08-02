"""
Defines the Bezier class, that has the same basis as the Polynomial
"""

from __future__ import annotations

from functools import cache
from typing import Iterable, Tuple, Union

from ..tools import Is, To
from .polynomial import Polynomial, scale, shift
from .quadrature import inner
from .reals import Math, Rational, Real


@cache
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


@cache
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
    poly_coefs = tuple(inner(weights, bezier) for weights in matrix)
    return Polynomial(poly_coefs)


def polynomial2bezier(polynomial: Polynomial) -> Bezier:
    """
    Converts a Polynomial instance to a Bezier
    """
    matrix = inverse_caract_matrix(polynomial.degree)
    ctrlpoints = tuple(inner(weights, polynomial) for weights in matrix)
    return Bezier(ctrlpoints)


def clean(bezier: Bezier) -> Bezier:
    """
    Decreases the degree of the bezier curve if possible
    """
    return polynomial2bezier(bezier2polynomial(bezier))


class Bezier:
    """
    Defines the Bezier class, that allows evaluating and operating
    such as adding, subtracting, multiplying, etc
    """

    def __init__(self, ctrlpoints: Iterable[Real]):

        if not Is.iterable(ctrlpoints):
            raise TypeError("Expected an iterable of coefficients")
        ctrlpoints = tuple(ctrlpoints)
        if len(ctrlpoints) == 0:
            raise ValueError("Cannot receive an empty tuple")
        self.__ctrlpoints = ctrlpoints
        self.__polynomial = bezier2polynomial(self)

    @property
    def degree(self) -> int:
        """
        Returns the degree of the polynomial, which is the
        highest power of t with a non-zero coefficient.
        If the polynomial is constant, returns 0.
        """
        return len(self.__ctrlpoints) - 1

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Bezier):
            return self.__polynomial == bezier2polynomial(value)
        if isinstance(value, Polynomial):
            return self.__polynomial == value
        if Is.real(value):
            return all(ctrlpoint == value for ctrlpoint in self)
        return NotImplemented

    def __iter__(self):
        yield from self.__ctrlpoints

    def __getitem__(self, index):
        return self.__ctrlpoints[index]

    def __neg__(self) -> Polynomial:
        return self.__class__(-coef for coef in self)

    def __add__(self, other: Union[Real, Polynomial, Bezier]) -> Bezier:
        if Is.instance(other, Bezier):
            other = bezier2polynomial(other)
        sumpoly = self.__polynomial + other
        return polynomial2bezier(sumpoly)

    def __mul__(self, other: Union[Real, Polynomial]) -> Bezier:
        if Is.instance(other, Bezier):
            other = bezier2polynomial(other)
        mulpoly = self.__polynomial * other
        return polynomial2bezier(mulpoly)

    def __pow__(self, exponent: int) -> Polynomial:
        poly = bezier2polynomial(self)
        return polynomial2bezier(poly**exponent)

    def __sub__(self, other: Union[Real, Polynomial]) -> Polynomial:
        return self.__add__(-other)

    def __rsub__(self, other: Real) -> Polynomial:
        return (-self).__add__(other)

    def __radd__(self, other: Real) -> Polynomial:
        return self.__add__(other)

    def __rmul__(self, other: Real) -> Polynomial:
        return self.__mul__(other)

    def __call__(self, node: Real) -> Real:
        return self.__polynomial(node)

    def __str__(self):
        return str(self.__polynomial)

    def __repr__(self) -> str:
        return repr(self.__polynomial)


def split(bezier: Bezier, nodes: Iterable[Real]) -> Iterable[Bezier]:
    """
    Splits the bezier curve into segments
    """
    nodes = (node for node in nodes if 0 < node < 1)
    nodes = tuple([0] + sorted(nodes) + [1])
    poly = bezier2polynomial(bezier)
    for knota, knotb in zip(nodes, nodes[1:]):
        newpoly = scale(shift(poly, -knota), knotb - knota)
        yield polynomial2bezier(newpoly)
