"""
Defines the Geometric Intersection Curves class
that is the result of intersecting two curves

Also defines methods to find the intersection points
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Dict, Iterable, Set, Tuple, Union

import rbool

from ..scalar.nodes_sample import NodeSampleFactory
from ..scalar.reals import Real
from ..tools import Is
from .base import IGeometricCurve
from .piecewise import PiecewiseCurve
from .segment import Segment


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
    def all_subsets(self) -> Dict[int, rbool.SubSetR1]:
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
        self.__all_knots = {id(c): set(c.knots) for c in self.curves}
        self.__all_subsets = {id(c): rbool.Empty() for c in self.curves}
        for i, j in self.pairs:
            self.__evaluate_two(self.curves[i], self.curves[j])

    def __evaluate_two(self, curvea: IGeometricCurve, curveb: IGeometricCurve):
        """
        Private function two compute the intersection between two curves
        """
        if id(curvea) == id(curveb):  # Check if curves are equal
            self.all_subsets[id(curvea)] |= [curvea.knots[0], curveb.knots[-1]]
            return
        if curvea.box() & curveb.box() is None:
            return
        if Is.piecewise(curvea) and Is.piecewise(curveb):
            subseta, subsetb = intersect_piecewises(curvea, curveb)
        elif Is.segment(curvea) and Is.segment(curveb):
            subseta, subsetb = segment_and_segment(curvea, curveb)
        else:
            raise NotImplementedError
        if subseta is rbool.Empty():
            return

        self.all_subsets[id(curvea)] |= subseta
        self.all_knots[id(curvea)] |= set(rbool.extract_knots(subseta))
        self.all_subsets[id(curveb)] |= subsetb
        self.all_knots[id(curveb)] |= set(rbool.extract_knots(subsetb))

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


def segment_and_segment(
    curvea: IGeometricCurve, curveb: IGeometricCurve
) -> Tuple[rbool.SubSetR1, rbool.SubSetR1]:
    """Computes the intersection between two geometric curves"""
    assert Is.segment(curvea)
    assert Is.segment(curveb)
    if curvea.box() & curveb.box() is None:
        return rbool.Empty(), rbool.Empty()
    if curvea == curveb:
        return rbool.Interval(0, 1), rbool.Interval(0, 1)
    if curvea.degree == 1 and curveb.degree == 1:
        subseta, subsetb = IntersectionSegments.lines(curvea, curveb)
        subseta &= [0, 1]
        subsetb &= [0, 1]
        return subseta, subsetb
    usample = list(NodeSampleFactory.closed_linspace(curvea.npts + 3))
    vsample = list(NodeSampleFactory.closed_linspace(curveb.npts + 3))
    pairs = []
    for ui in usample:
        pairs += [(ui, vj) for vj in vsample]
    for _ in range(3):
        pairs = IntersectionSegments.bezier_and_bezier(curvea, curveb, pairs)
        pairs.insert(0, (0, 0))
        pairs.insert(0, (0, 1))
        pairs.insert(0, (1, 0))
        pairs.insert(0, (1, 1))
        # Filter values by distance of points
        tol_norm = 1e-6
        pairs = IntersectionSegments.filter_distance(
            curvea, curveb, pairs, tol_norm
        )
        # Filter values by distance abs(ui-uj, vi-vj)
        tol_du = 1e-6
        pairs = IntersectionSegments.filter_parameters(pairs, tol_du)
    subseta = rbool.from_any({pair[0] for pair in pairs})
    subsetb = rbool.from_any({pair[1] for pair in pairs})
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
    def lines(
        curvea: Segment, curveb: Segment
    ) -> Tuple[rbool.SubSetR1, rbool.SubSetR1]:
        """Finds the intersection of two line segments"""
        assert curvea.degree == 1
        assert curveb.degree == 1
        empty = rbool.Empty()
        A0, A1 = curvea.ctrlpoints
        B0, B1 = curveb.ctrlpoints
        dA = A1 - A0
        dB = B1 - B0
        B0mA0 = B0 - A0
        dAxdB = dA ^ dB
        if dAxdB != 0:  # Lines are not parallel
            t0 = (B0mA0 ^ dB) / dAxdB
            if t0 < 0 or 1 < t0:
                return empty, empty
            u0 = (B0mA0 ^ dA) / dAxdB
            if u0 < 0 or 1 < u0:
                return empty, empty
            return rbool.SingleValue(t0), rbool.SingleValue(u0)
        # Lines are parallel
        if dA ^ B0mA0 != 0:
            return empty, empty  # Parallel, but not colinear
        # Compute the projections
        dAodA = dA @ dA
        dBodB = dB @ dB
        t0 = (B0 - A0) @ dA / dAodA
        t1 = (B1 - A0) @ dA / dAodA
        if t1 < t0:
            t0, t1 = t1, t0
        if t1 < 0 or 1 < t0:
            return empty, empty

        u0 = (A0 - B0) @ dB / dBodB
        u1 = (A1 - B0) @ dB / dBodB
        if u1 < u0:
            u0, u1 = u1, u0
        t0 = min(max(0, t0), 1)
        t1 = min(max(0, t1), 1)
        u0 = min(max(0, u0), 1)
        u1 = min(max(0, u1), 1)
        if t0 == t1 or u0 == u1:
            return rbool.SingleValue(t0), rbool.SingleValue(u1)
        return rbool.Interval(t0, t1), rbool.Interval(u0, u1)

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
                vect0 = dsu @ dif
                vect1 = -dov @ dif
                mat00 = dsu @ dsu + ddu @ dif
                mat01 = -dsu @ dov
                mat11 = dov @ dov - ddv @ dif
                deter = mat00 * mat11 - mat01**2
                if abs(deter) < 1e-6:
                    continue
                newu = u - (mat11 * vect0 - mat01 * vect1) / deter
                newv = v - (mat00 * vect1 - mat01 * vect0) / deter
                pair = (min(1, max(0, newu)), min(1, max(0, newv)))
                new_pairs.add(pair)
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


def intersect_piecewises(
    curvea: PiecewiseCurve,
    curveb: PiecewiseCurve,
) -> Tuple[rbool.SubSetR1, rbool.SubSetR1]:
    r"""Computes the intersection between two jordan curves

    Finds the values of (:math:`a^{\star}`, :math:`b^{\star}`,
    :math:`u^{\star}`, :math:`v^{\star}`) such

    .. math::
        S_{a^{\star}}(u^{\star}) == O_{b^{\star}}(v^{\star})

    It computes the intersection between each pair of segments
    from ``self`` and ``other`` and returns the matrix of coefficients

    .. math::

        \begin{bmatrix}
        a_0 & b_0 & u_0 & v_0 \\
        a_1 & b_1 & u_1 & v_1 \\
        \vdots & \vdots & \vdots & \vdots \\
        a_{n} & b_{n} & u_{n} & v_{n}
        \end{bmatrix}

    If two bezier curves are equal, then ``u_i = v_i = None``

    * ``0 <= a_i < len(self.segments)``
    * ``0 <= b_i < len(other.segments)``
    * ``0 <= u_i <= 1`` or ``None``
    * ``0 <= v_i <= 1`` or ``None``

    Parameters
    ----------
    other : JordanCurve
        The jordan curve which intersects ``self``
    equal_beziers : bool, default = True
        Flag to return (or not) when two segments are equal

        If the flag ``equal_beziers`` are inactive,
        then will remove when ``(ui, vi) == (None, None)``.

    end_points : bool, default = True
        Flag to return (or not) when jordans intersect at end points

        If the flag ``end_points`` are inactive,
        then will remove when ``(ui, vi)`` are
        ``(0, 0)``, ``(0, 1)``, ``(1, 0)`` or ``(1, 1)``

    :return: The matrix of coefficients ``[(ai, bi, ui, vi)]``
                or an empty tuple in case of non-intersection
    :rtype: tuple[(int, int, float, float)]


    Example use
    -----------
    >>> from shapepy import JordanCurve
    >>> vertices_a = [(0, 0), (2, 0), (2, 2), (0, 2)]
    >>> jordan_a = FactoryJordan.polygon(vertices_a)
    >>> vertices_b = [(1, 1), (3, 1), (3, 3), (1, 3)]
    >>> jordan_b = FactoryJordan.polygon(vertices_b)
    >>> jordan_a.intersection(jordan_b)
    ((1, 0, 1/2, 1/2), (2, 3, 1/2, 1/2))

    """
    assert Is.piecewise(curvea)
    assert Is.piecewise(curveb)

    subseta, subsetb = rbool.Empty(), rbool.Empty()
    for ai, sbezier in enumerate(curvea):
        for bj, obezier in enumerate(curveb):
            suba, subb = segment_and_segment(sbezier, obezier)
            suba = suba.scale(curvea.knots[ai + 1] - curvea.knots[ai])
            subseta |= suba.move(curvea.knots[ai])
            subb = subb.scale(curveb.knots[bj + 1] - curveb.knots[bj])
            subsetb |= subb.move(curveb.knots[bj])
    return subseta, subsetb
