"""
This file computes the intersection between two any curves

The curves can be analytic,
Defines the Geometric Intersection Curves class
that is the result of intersecting two curves

Also defines methods to find the intersection points
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Dict, Iterable, Set, Tuple, Union

from ..loggers import debug, get_logger
from ..rbool import (
    EmptyR1,
    SubSetR1,
    create_interval,
    create_single,
    extract_knots,
    from_any,
)
from ..scalar.nodes_sample import NodeSampleFactory
from ..scalar.reals import Real
from ..tools import Is
from .base import IGeometricCurve, IParametrizedCurve
from .piecewise import PiecewiseCurve
from .point import cross, inner
from .segment import Segment


def intersect(
    curvea: IGeometricCurve, curveb: IGeometricCurve
) -> GeometricIntersectionCurves:
    """
    Computes the intersection beteween two curves
    """
    return GeometricIntersectionCurves([curvea, curveb])


class GeometricIntersectionCurves:
    """
    Class that stores and computes the intersection between some curves

    It's a lazy evaluator: it only computes the intersections, which is
    a heavy tank when requested

    It stores inside 'curves' the a
    """

    def __init__(
        self,
        curves: Iterable[IGeometricCurve],
        pairs: Union[None, Iterable[Tuple[int, int]]] = None,
    ):
        curves = tuple(curves)
        if not all(Is.instance(curve, IGeometricCurve) for curve in curves):
            raise TypeError
        if pairs is None:
            pairs: Set[Tuple[int, int]] = set()
            for i in range(len(curves)):
                for j in range(i + 1, len(curves)):
                    pairs.add((i, j))
        else:
            pairs = ((i, j) if i < j else (j, i) for i, j in pairs)
            pairs = set(map(tuple, pairs))
        self.__pairs = pairs
        self.__curves = curves
        self.__all_knots = None
        self.__all_subsets = None

    def __str__(self) -> str:  # pragma: no cover  # Debug only
        intercurves = {id(curve): curve for curve in self.__curves}
        msgs = ["Curves:"]
        for i, curve in enumerate(intercurves.values()):
            msgs.append(f"    {i}: {id(curve)}: {curve}")
            if self.__all_subsets is not None:
                msgs.append(f"        knots: {self.__all_knots[id(curve)]}")
            if self.__all_subsets is not None:
                msgs.append(f"        subset: {self.__all_subsets[id(curve)]}")
        return "\n".join(msgs)

    @property
    def pairs(self) -> Iterable[Tuple[int, int]]:
        """
        Gives the pairs to be used to compute the intersection
        For example: suppose there are 4 curves and
        pairs = [(0, 1), (0, 2), (1, 3), (2, 3)]

        That means, only will be computed
        * curves[0] & curves[1]
        * curves[0] & curves[2]
        * curves[1] & curves[3]
        * curves[2] & curves[3]
        And these pairs will not be computed
        * curves[0] & curves[3]
        * curves[1] & curves[2]
        """
        return self.__pairs

    @property
    def curves(self) -> Tuple[IGeometricCurve, ...]:
        """
        Gives the curves that will be used to compute the intersection
        """
        return self.__curves

    @property
    def all_subsets(self) -> Dict[int, SubSetR1]:
        """
        A dictionnary that contains, for each curve,
        the parameters of that curve that are shared with other curve

        For example, if curves[0] intersects curves[1]
        with parameters ui, vj, that means
        * curves[0](ui) = curves[1](vj)
        And,
        * all_subsets[id(curves[0])] contains ui
        * all_subsets[id(curves[1])] contains vj
        """
        if self.__all_subsets is None:
            self.evaluate()
        return self.__all_subsets

    @property
    def all_knots(self) -> Dict[int, Set[Real]]:
        """
        A dictionnary that contais, for each curve,
        the knots that intersects any other curve.

        It's similar to all_subsets, but it stores the
        usual knots of the given curve,
        and all_subsets loses the information that a curve
        should break at some given parameter if
        another curve overlaps the first one
        """
        if self.__all_knots is None:
            self.evaluate()
        return self.__all_knots

    def evaluate(self):
        """
        Computes the intersection between all the curves
        """
        self.__all_knots = {}
        self.__all_subsets = {}
        for curve in self.curves:
            knots = curve.parametrize().knots
            self.__all_knots[id(curve)] = set(knots)
            self.__all_subsets[id(curve)] = EmptyR1()
        for i, j in self.pairs:
            self.__evaluate_two(self.curves[i], self.curves[j])

    def __evaluate_two(self, curvea: IGeometricCurve, curveb: IGeometricCurve):
        """
        Private function two compute the intersection between two curves
        """
        subseta, subsetb = self.__compute_two(curvea, curveb)
        if Is.instance(subseta, EmptyR1):
            return
        self.all_subsets[id(curvea)] |= subseta
        self.all_knots[id(curvea)] |= set(extract_knots(subseta))
        self.all_subsets[id(curveb)] |= subsetb
        self.all_knots[id(curveb)] |= set(extract_knots(subsetb))

    def __compute_two(
        self, curvea: IGeometricCurve, curveb: IGeometricCurve
    ) -> Tuple[SubSetR1, SubSetR1]:
        if curvea.box() & curveb.box() is None:
            return EmptyR1(), EmptyR1()
        if id(curvea) == id(curveb):  # Check if curves are equal
            curvea = curvea.parametrize()
            subset = create_interval(curvea.knots[0], curvea.knots[-1])
            return subset, subset
        return curve_and_curve(curvea, curveb)

    def __or__(
        self, other: GeometricIntersectionCurves
    ) -> GeometricIntersectionCurves:
        n = len(self.curves)
        newcurves = list(self.curves) + list(other.curves)
        newparis = list(self.pairs)
        for i, j in other.pairs:
            newparis.append((i + n, j + n))
        for i in range(len(self.curves)):
            for j in range(len(other.curves)):
                newparis.append((i, n + j))
        return GeometricIntersectionCurves(newcurves, newparis)

    def __bool__(self):
        return any(v != EmptyR1() for v in self.all_subsets.values())


def curve_and_curve(
    curvea: IGeometricCurve, curveb: IGeometricCurve
) -> Tuple[SubSetR1, SubSetR1]:
    """Computes the intersection between two curves"""
    return param_and_param(curvea.parametrize(), curveb.parametrize())


def param_and_param(
    curvea: IParametrizedCurve, curveb: IParametrizedCurve
) -> Tuple[SubSetR1, SubSetR1]:
    """Computes the intersection between two parametrized curves"""
    assert Is.instance(curvea, IParametrizedCurve)
    assert Is.instance(curveb, IParametrizedCurve)
    if curvea.box() & curveb.box() is None:
        return EmptyR1(), EmptyR1()
    if Is.instance(curvea, PiecewiseCurve):
        subseta, subsetb = EmptyR1(), EmptyR1()
        for segmenta in curvea:
            subb, suba = param_and_param(segmenta, curveb)
            subseta |= suba
            subsetb |= subb
        return subseta, subsetb
    if Is.instance(curveb, PiecewiseCurve):
        # pylint: disable=arguments-out-of-order
        return param_and_param(curveb, curvea)[::-1]
    return segment_and_segment(curvea, curveb)


def segment_is_linear(segment: Segment) -> bool:
    """Tells if the segment is a polynomial linear"""
    return segment.xfunc.degree <= 1 and segment.yfunc.degree <= 1


def segment_and_segment(
    curvea: Segment, curveb: Segment
) -> Tuple[SubSetR1, SubSetR1]:
    """Computes the intersection between two segment curves"""
    assert Is.instance(curvea, Segment)
    assert Is.instance(curveb, Segment)
    if curvea == curveb:
        return curvea.domain, curveb.domain
    if segment_is_linear(curvea) and segment_is_linear(curveb):
        return IntersectionSegments.lines(curvea, curveb)
    nptsa = max(curvea.xfunc.degree, curvea.yfunc.degree) + 4
    nptsb = max(curveb.xfunc.degree, curveb.yfunc.degree) + 4
    usample = [
        curvea.knots[0] + u * (curvea.knots[-1] - curvea.knots[0])
        for u in NodeSampleFactory.closed_linspace(nptsa)
    ]
    vsample = [
        curveb.knots[0] + u * (curveb.knots[-1] - curveb.knots[0])
        for u in NodeSampleFactory.closed_linspace(nptsb)
    ]
    pairs = []
    for ui in usample:
        pairs += [(ui, vj) for vj in vsample]
    for _ in range(3):
        pairs = IntersectionSegments.bezier_and_bezier(curvea, curveb, pairs)
        pairs.insert(0, (curvea.knots[0], curveb.knots[0]))
        pairs.insert(0, (curvea.knots[0], curveb.knots[-1]))
        pairs.insert(0, (curvea.knots[-1], curveb.knots[0]))
        pairs.insert(0, (curvea.knots[-1], curveb.knots[-1]))
        # Filter values by distance of points
        tol_norm = 1e-6
        pairs = IntersectionSegments.filter_distance(
            curvea, curveb, pairs, tol_norm
        )
        # Filter values by distance abs(ui-uj, vi-vj)
        tol_du = 1e-6
        pairs = IntersectionSegments.filter_parameters(pairs, tol_du)
    subseta = from_any({pair[0] for pair in pairs})
    subsetb = from_any({pair[1] for pair in pairs})
    return subseta, subsetb


class IntersectionSegments:
    """
    Defines the methods used to compute the intersection between curves
    """

    tol_du = 1e-9  # tolerance convergence
    tol_norm = 1e-9  # tolerance convergence
    max_denom = math.ceil(1 / tol_du)

    # pylint: disable=invalid-name, too-many-return-statements, too-many-locals
    @staticmethod
    @debug("shapepy.geometry.intersection")
    def lines(curvea: Segment, curveb: Segment) -> Tuple[SubSetR1, SubSetR1]:
        """Finds the intersection of two line segments"""
        empty = EmptyR1()
        logger = get_logger("shapepy.geometry.intersection")
        A0 = curvea(curvea.knots[0])
        A1 = curvea(curvea.knots[-1])
        B0 = curveb(curveb.knots[0])
        B1 = curveb(curveb.knots[-1])
        dA = A1 - A0
        dB = B1 - B0
        B0mA0 = B0 - A0
        dAxdB = cross(dA, dB)
        if dAxdB != 0:  # Lines are not parallel
            t0 = cross(B0mA0, dB) / dAxdB
            if t0 < 0 or 1 < t0:
                logger.debug("1) Empty, Empty")
                return empty, empty
            u0 = cross(B0mA0, dA) / dAxdB
            if u0 < 0 or 1 < u0:
                logger.debug("2) Empty, Empty")
                return empty, empty
            t0 = curvea.knots[0] + t0 * (curvea.knots[-1] - curvea.knots[0])
            u0 = curveb.knots[0] + u0 * (curveb.knots[-1] - curveb.knots[0])
            logger.debug("3) Single, Single")
            return create_single(t0), create_single(u0)
        # Lines are parallel
        if cross(dA, B0mA0) != 0:
            logger.debug("4) Empty, Empty")
            return empty, empty  # Parallel, but not colinear
        # Compute the projections
        dAodA = inner(dA, dA)
        dBodB = inner(dB, dB)
        t0 = inner(B0 - A0, dA) / dAodA
        t1 = inner(B1 - A0, dA) / dAodA
        if t1 < t0:
            t0, t1 = t1, t0
        if t1 < 0 or 1 < t0:
            return empty, empty

        u0 = inner(A0 - B0, dB) / dBodB
        u1 = inner(A1 - B0, dB) / dBodB
        if u1 < u0:
            u0, u1 = u1, u0
        t0 = min(max(0, t0), 1)
        t1 = min(max(0, t1), 1)
        u0 = min(max(0, u0), 1)
        u1 = min(max(0, u1), 1)
        t0 = curvea.knots[0] + t0 * (curvea.knots[-1] - curvea.knots[0])
        u0 = curveb.knots[0] + u0 * (curveb.knots[-1] - curveb.knots[0])
        t1 = curvea.knots[0] + t1 * (curvea.knots[-1] - curvea.knots[0])
        u1 = curveb.knots[0] + u1 * (curveb.knots[-1] - curveb.knots[0])
        if t0 == t1 or u0 == u1:
            logger.debug("6) Single, Single")
            return create_single(t0), create_single(u1)
        logger.debug("7) Interval, Interval")
        return create_interval(t0, t1), create_interval(u0, u1)

    # pylint: disable=too-many-locals
    @staticmethod
    def bezier_and_bezier(
        curvea: Segment, curveb: Segment, pairs: Tuple[Tuple[float]]
    ) -> Tuple[Tuple[float]]:
        """Finds all the pairs (u*, v*) such A(u*) = B(v*)

        Uses newton's method
        """
        dcurvea = curvea.derivate()
        ddcurvea = dcurvea.derivate()
        dcurveb = curveb.derivate()
        ddcurveb = dcurveb.derivate()

        # Start newton iteration
        for _ in range(20):  # Number of newton iteration
            new_pairs = set()
            for u, v in pairs:
                ssu = curvea(u)
                dsu = dcurvea(u)
                ddu = ddcurvea(u)
                oov = curveb(v)
                dov = dcurveb(v)
                ddv = ddcurveb(v)

                dif = ssu - oov
                vect0 = inner(dsu, dif)
                vect1 = -inner(dov, dif)
                mat00 = inner(dsu, dsu) + inner(ddu, dif)
                mat01 = -inner(dsu, dov)
                mat11 = inner(dov, dov) - inner(ddv, dif)
                deter = mat00 * mat11 - mat01**2
                if abs(deter) < 1e-6:
                    continue
                newu = u - (mat11 * vect0 - mat01 * vect1) / deter
                newv = v - (mat00 * vect1 - mat01 * vect0) / deter
                newu = min(curvea.knots[-1], max(curvea.knots[0], newu))
                newv = min(curveb.knots[-1], max(curveb.knots[0], newv))
                new_pairs.add((newu, newv))
            pairs = list(new_pairs)
            for i, (ui, vi) in enumerate(pairs):
                if Is.instance(ui, Fraction):
                    ui = ui.limit_denominator(10000)
                if Is.instance(vi, Fraction):
                    vi = vi.limit_denominator(10000)
                pairs[i] = (ui, vi)
        return pairs

    @staticmethod
    def filter_distance(
        curvea: Segment,
        curveb: Segment,
        pairs: Tuple[Tuple[float]],
        max_dist: float,
    ) -> Tuple[Tuple[float]]:
        """
        Filter the pairs values, since the intersection pair
        (0.5, 1) is almost the same as (1e-6, 0.99999)
        """
        pairs = list(pairs)
        index = 0
        while index < len(pairs):
            ui, vi = pairs[index]
            diff = curvea(ui) - curveb(vi)
            if abs(diff) < max_dist:
                index += 1
            else:
                pairs.pop(index)
        return tuple(pairs)

    @staticmethod
    def filter_parameters(
        pairs: Tuple[Tuple[float]], max_dist: float
    ) -> Tuple[Tuple[float]]:
        """
        Filter the parameters values, cause 0 is almost the same as 1e-6
        """
        pairs = list(pairs)
        index = 0
        while index < len(pairs):
            ui, vi = pairs[index]
            j = index + 1
            while j < len(pairs):
                uj, vj = pairs[j]
                dist2 = (ui - uj) ** 2 + (vi - vj) ** 2
                if dist2 < max_dist**2:
                    pairs.pop(j)
                else:
                    j += 1
            index += 1
        return tuple(pairs)
