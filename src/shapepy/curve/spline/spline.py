from __future__ import annotations

from typing import Any, Iterable, Optional, Tuple, Union

import numpy as np
import sympy as sp

from ...analytic.polynomial import Polynomial
from ...core import Parameter, Scalar
from ...point import GeneralPoint, Point2D
from ..piecewise import PiecewiseClosedCurve, PiecewiseOpenCurve
from .knotvector import KnotVector


def inner(valsa: Iterable[Any], valsb: Iterable[Any]) -> Any:
    valsa = tuple(valsa)
    valsb = tuple(valsb)
    soma = valsa[0] * valsb[0]
    for k, vala in enumerate(valsa):
        if not k:
            continue
        soma += vala * valsb[k]
    return soma


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


def piecewise_spline_polynomials(
    knotvector: KnotVector,
) -> Tuple[Tuple[Polynomial, ...], ...]:
    """
    Given a knotvector U, with attributes like 'degree' and 'npts'
    there are 'm' intervals, given by (len(knots) - 1)
    Then, for each interval 'k', there are 'npts' polynomial functions

    returns a tuple of shape (m, npts) of Polynomial
    """
    matrix = local_speval_matrix(knotvector, knotvector.degree)
    degree = knotvector.degree
    npts = knotvector.npts
    nsegs = len(knotvector.spans)
    allpolys = [[Polynomial([0]) for _ in range(npts)] for _ in range(nsegs)]
    for k, span in enumerate(knotvector.spans):
        knot0, knot1 = knotvector.knots[k], knotvector.knots[k + 1]
        for y in range(degree + 1):
            i = y + span - degree
            poly = Polynomial(matrix[k, y])
            poly = poly.scale(1 / (knot1 - knot0))
            poly = poly.shift(knot0)
            allpolys[k][i] = poly
    return tuple(map(tuple, allpolys))


def compute_segments(
    knotvector: KnotVector, ctrlpoints: Iterable[Scalar]
) -> Tuple[Polynomial, ...]:
    ctrlpoints = tuple(ctrlpoints)
    if not isinstance(knotvector, KnotVector):
        raise TypeError
    if knotvector.npts != len(ctrlpoints):
        raise ValueError
    for point in ctrlpoints:
        float(point)  # check if it's scalar
    all_polynomials = piecewise_spline_polynomials(knotvector)
    result = tuple(inner(ctrlpoints, polys) for polys in all_polynomials)
    return result


class Spline:
    def __init__(self, knotvector: KnotVector, ctrlpoints: Iterable[Any]):
        if not isinstance(knotvector, KnotVector):
            raise TypeError
        ctrlpoints = tuple(ctrlpoints)
        if knotvector.npts != len(ctrlpoints):
            raise ValueError(f"{knotvector.npts} != {len(ctrlpoints)}")
        self.__knotvector = knotvector
        self.__ctrlpoints = ctrlpoints

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


class SplineOpenCurve(PiecewiseOpenCurve, Spline):
    """ """

    def __init__(
        self, knotvector: KnotVector, ctrlpoints: Iterable[GeneralPoint]
    ):
        if not isinstance(knotvector, KnotVector):
            raise TypeError
        ctrlpoints = list(ctrlpoints)
        for i, point in enumerate(ctrlpoints):
            if not isinstance(point, Point2D):
                ctrlpoints[i] = Point2D(point)
        xctrlpts = tuple(point[0] for point in ctrlpoints)
        yctrlpts = tuple(point[1] for point in ctrlpoints)
        xfuncs = compute_segments(knotvector, xctrlpts)
        yfuncs = compute_segments(knotvector, yctrlpts)
        functions = tuple(zip(xfuncs, yfuncs))
        Spline.__init__(self, knotvector, ctrlpoints)
        PiecewiseOpenCurve.__init__(self, functions)

    def __str__(self) -> str:
        return "SplineOpenCurve"

    def __repr__(self) -> str:
        return f"SplineOpenCurve({self.degree}, {self.npts})"

    def section(self, nodea: Parameter, nodeb: Parameter) -> SplineOpenCurve:
        if nodea == self.knots[0] and nodeb == self.knots[-1]:
            return self
        curve = super().section(nodea, nodeb)
        return open_spline_from_piecewise(curve)


class SplineClosedCurve(PiecewiseClosedCurve, Spline):
    """ """

    def __init__(
        self, knotvector: KnotVector, ctrlpoints: Iterable[GeneralPoint]
    ):
        if not isinstance(knotvector, KnotVector):
            raise TypeError
        ctrlpoints = list(ctrlpoints)
        for i, point in enumerate(ctrlpoints):
            if not isinstance(point, Point2D):
                ctrlpoints[i] = Point2D(point)
        xctrlpts = tuple(point[0] for point in ctrlpoints)
        yctrlpts = tuple(point[1] for point in ctrlpoints)
        xfuncs = compute_segments(knotvector, xctrlpts)
        yfuncs = compute_segments(knotvector, yctrlpts)
        functions = list(zip(xfuncs, yfuncs))
        Spline.__init__(self, knotvector, ctrlpoints)
        PiecewiseOpenCurve.__init__(self, functions)

    def section(
        self, nodea: Parameter, nodeb: Parameter
    ) -> Union[SplineOpenCurve, SplineClosedCurve]:
        if nodea == self.knots[0] and nodeb == self.knots[-1]:
            return self
        curve = super().section(nodea, nodeb)
        return open_spline_from_piecewise(curve)


def open_spline_from_piecewise(curve: PiecewiseOpenCurve) -> SplineOpenCurve:
    """
    Transform a polynomial piecewise curve into a Spline curve

    This function solves a linear system

    """
    if not isinstance(curve, PiecewiseOpenCurve):
        raise TypeError
    degree = 0
    nsegments = len(curve.functions)
    for xfunc, yfunc in curve.functions:
        if not isinstance(xfunc, Polynomial):
            raise TypeError
        if not isinstance(yfunc, Polynomial):
            raise TypeError
        degree = max(degree, xfunc.degree)
        degree = max(degree, xfunc.degree)
    knotvector = (
        (0,) * degree + tuple(range(nsegments + 1)) + (nsegments,) * degree
    )
    knotvector = KnotVector(knotvector, degree=degree)
    npts, knots = knotvector.npts, knotvector.knots
    matrixpolys = piecewise_spline_polynomials(knotvector)
    curvefuncts = tuple(curve.functions)
    stiffmatrix = np.zeros((npts, npts), dtype="object")
    forcevector = np.zeros((npts, len(curvefuncts[0])), dtype="object")
    for k, (ta, tb) in enumerate(zip(knots, knots[1:])):
        for i, funci in enumerate(matrixpolys[k]):
            for j, funcj in enumerate(curvefuncts[k]):
                forcevector[i, j] += (funci * funcj).defintegral(ta, tb)
            for j, funcj in enumerate(matrixpolys[k]):
                stiffmatrix[i, j] += (funci * funcj).defintegral(ta, tb)
    stiffmatrix = sp.Matrix(stiffmatrix)
    forcevector = sp.Matrix(forcevector)
    ctrlpoints = stiffmatrix.inv() @ forcevector
    ctrlpoints = tuple(map(tuple, ctrlpoints.tolist()))
    return SplineOpenCurve(knotvector, ctrlpoints)
