"""
Defines the Bezier class, that has the same basis as the Polynomial
"""

from __future__ import annotations

from functools import lru_cache
from typing import Iterable, Tuple, Union

from ..rbool import SubSetR1
from ..scalar.quadrature import inner
from ..scalar.reals import Math, Rational, Real
from ..tools import Is, To
from .polynomial import Polynomial, scale_coefs, shift_coefs


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


def bezier2polynomial(coefs: Iterable[Real]) -> Iterable[Real]:
    """
    Converts a Bezier instance to Polynomial
    """
    coefs = tuple(coefs)
    matrix = bezier_caract_matrix(len(coefs) - 1)
    return (inner(weights, coefs) for weights in matrix)


def polynomial2bezier(coefs: Iterable[Real]) -> Iterable[Real]:
    """
    Converts a Polynomial instance to a Bezier
    """
    coefs = tuple(coefs)
    matrix = inverse_caract_matrix(len(coefs) - 1)
    return (inner(weights, coefs) for weights in matrix)


class Bezier(Polynomial):
    """
    Defines the Bezier class, that allows evaluating and operating
    such as adding, subtracting, multiplying, etc
    """

    def __init__(
        self,
        coefs: Iterable[Real],
        reparam: Tuple[Real, Real] = (0, 1),
        *,
        domain: Union[None, SubSetR1] = None,
    ):
        coefs = tuple(bezier2polynomial(coefs))
        knota, knotb = reparam
        coefs = shift_coefs(scale_coefs(coefs, knotb - knota), knota)
        super().__init__(coefs, domain=domain)
