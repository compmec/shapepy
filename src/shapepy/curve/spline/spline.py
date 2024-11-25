from __future__ import annotations

from typing import Any, Iterable, Optional, Tuple

import numpy as np

from ...analytic.polynomial import Polynomial, binom
from ...core import Parameter
from .knotvector import KnotVector


def local_speval_matrix(
    knotvector: KnotVector, reqdegree: Optional[int] = None
) -> np.ndarray:
    """
    Given a knotvector, it has properties like
        - number of points: npts
        - polynomial degree: degree
        - knots: A list of non-repeted knots
        - spans: The span of each knot
    This function returns a matrix of size
        (m) x (j+1) x (j+1)
    which
        - m is the number of segments: len(knots)-1
        - j is the requested degree
    """
    knotvector = KnotVector(knotvector)
    if reqdegree is None:
        reqdegree = knotvector.degree
    elif reqdegree < 0:
        raise ValueError(f"reqdegree must be in [0, {knotvector.degree}]")
    knots = knotvector.knots
    spans = knotvector.spans
    j = reqdegree

    matrix = np.zeros((len(knots) - 1, j + 1, j + 1), dtype="object")
    if j == 0:
        one = knotvector.knots[-1] - knotvector.knots[0]
        matrix.fill(one / one)
        return matrix
    matrix_less1 = local_speval_matrix(knotvector, j - 1)
    for y in range(j):
        for z, sz in enumerate(spans):
            i = y + sz - j + 1
            denom = knotvector[i + j] - knotvector[i]
            matrix_less1[z, y, :] /= denom

            a0 = knots[z] - knotvector[i]
            a1 = knots[z + 1] - knots[z]
            b0 = knotvector[i + j] - knots[z]
            b1 = knots[z] - knots[z + 1]

            matrix[z, y, :-1] += b0 * matrix_less1[z, y]
            matrix[z, y, 1:] += b1 * matrix_less1[z, y]
            matrix[z, y + 1, :-1] += a0 * matrix_less1[z, y]
            matrix[z, y + 1, 1:] += a1 * matrix_less1[z, y]

    return matrix


def local_to_global_matrix(knots: Tuple[Parameter, ...], matrix: np.ndarray):
    matrix3d = 0 * np.copy(matrix)
    degree = matrix.shape[2] - 1
    for i, (ta, tb) in enumerate(zip(knots, knots[1:])):
        delta = tb - ta
        for j in range(degree + 1):
            line = matrix[i, :, j] / delta**j
            for k in range(j + 1):
                val = binom(j, k) * line * ta ** (j - k)
                if (j + k) % 2:
                    val *= -1
                matrix3d[i, :, k] += val
    return matrix3d


def global_speval_matrix(
    knotvector: KnotVector, reqdegree: Optional[int] = None
):
    local_matrix = local_speval_matrix(knotvector, reqdegree)
    global_matrix = local_to_global_matrix(knotvector.knots, local_matrix)
    return global_matrix


def compute_segments(
    knotvector: KnotVector, ctrlpoints: Tuple[Any, ...]
) -> Tuple[Polynomial, ...]:
    if not isinstance(knotvector, KnotVector):
        raise TypeError
    ctrlpoints = tuple(ctrlpoints)
    if knotvector.npts != len(ctrlpoints):
        raise ValueError
    matrix3d = global_speval_matrix(knotvector, knotvector.degree)
    shape = len(knotvector.knots) - 1, knotvector.degree + 1
    allcoefs = np.zeros(shape, dtype="object")
    for j, span in enumerate(knotvector.spans):
        for y in range(knotvector.degree + 1):
            i = y + span - knotvector.degree
            coefs = matrix3d[j, y]
            for k, ck in enumerate(coefs):
                allcoefs[j, k] += ck * ctrlpoints[i]
    return tuple(map(Polynomial, allcoefs))


class Spline:

    def __init__(self, knotvector: KnotVector, ctrlpoints: Iterable[Any]):
        if not isinstance(knotvector, KnotVector):
            raise TypeError
        ctrlpoints = tuple(ctrlpoints)
        if knotvector.npts != len(ctrlpoints):
            raise ValueError
        self.__knotvector = knotvector
        self.__ctrlpoints = ctrlpoints
        self.__segments = compute_segments(knotvector, ctrlpoints)

    @property
    def degree(self) -> int:
        return self.knotvector.degree

    @property
    def npts(self) -> int:
        return self.knotvector.npts

    @property
    def knots(self) -> Tuple[Parameter, ...]:
        return self.knotvector.knots

    @property
    def knotvector(self) -> KnotVector:
        return self.__knotvector

    @property
    def ctrlpoints(self) -> Tuple[Any, ...]:
        return self.__ctrlpoints

    @property
    def segments(self) -> Tuple[Polynomial, ...]:
        return self.__segments

    def eval(self, node: Parameter, derivate: int = 0) -> Any:
        if node < self.knots[0] or self.knots[-1] < node:
            raise ValueError
        for index, knot in enumerate(self.knots[1:]):
            if node < knot:
                break
        segment = self.__segments[index]
        return segment.eval(node, derivate)


class SplineOpenCurve(Spline):
    """ """


class SplineClosedCurve(Spline):
    """ """
