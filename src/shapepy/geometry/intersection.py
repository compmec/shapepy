"""
Defines the Geometric Intersection Curves class
that is the result of intersecting two curves

Also defines methods to find the intersection points
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Tuple, Union

from ..scalar.nodes_sample import NodeSampleFactory
from ..tools import Is
from .piecewise import PiecewiseCurve
from .segment import Segment


def segment_and_segment(
    curvea: Segment, curveb: Segment
) -> Union[None, Tuple[Tuple[int]]]:
    """Computes the intersection between two Planar Curves

    Returns None if there's no intersection

    Returns tuple() if curves are equal

    Returns [(a0, b0), (a1, b1), ...]
    Which self(ai) == other(bi)
    """
    assert Is.segment(curvea)
    assert Is.segment(curveb)
    if curvea.box() & curveb.box() is None:
        return None
    if curvea == curveb:
        return tuple()
    if curvea.degree == 1 and curveb.degree == 1:
        params = IntersectionSegments.lines(curvea, curveb)
        return (params,) if len(params) != 0 else tuple()
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
    return tuple(pairs)


class IntersectionSegments:
    """
    Defines the methods used to compute the intersection between curves
    """

    tol_du = 1e-9  # tolerance convergence
    tol_norm = 1e-9  # tolerance convergence
    max_denom = math.ceil(1 / tol_du)

    @staticmethod
    def lines(curvea: Segment, curveb: Segment) -> Tuple[float]:
        """Finds the intersection of two line segments"""
        assert curvea.degree == 1
        assert curveb.degree == 1
        pta0, pta1 = curvea.ctrlpoints
        ptb0, ptb1 = curveb.ctrlpoints
        vector0 = pta1 - pta0
        vector1 = ptb1 - ptb0
        diff0 = ptb0 - pta0
        denom = vector0 ^ vector1
        if denom != 0:  # Lines are not parallel
            param0 = (diff0 ^ vector1) / denom
            param1 = (diff0 ^ vector0) / denom
            if param0 < 0 or 1 < param0:
                return tuple()
            if param1 < 0 or 1 < param1:
                return tuple()
            return param0, param1
        # Lines are parallel
        if vector0 ^ diff0 != 0:
            return tuple()  # Parallel, but not colinear
        return tuple()

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
) -> Tuple[Tuple[int, int, float, float]]:
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

    intersections = set()
    for ai, sbezier in enumerate(curvea):
        for bj, obezier in enumerate(curveb):
            inters = segment_and_segment(sbezier, obezier)
            if inters is None:
                continue
            if len(inters) == 0:  # Equal curves
                intersections.add((ai, bj, None, None))
            for ui, vj in inters:
                intersections.add((ai, bj, ui, vj))
    intersections = list(intersections)
    # Filter the values
    for ai, bi, ui, vi in tuple(intersections):
        if ui is None:
            intersections.remove((ai, bi, ui, vi))
    for ai, bi, ui, vi in tuple(intersections):
        if ui is None or (0 < ui < 1) or (0 < vi < 1):
            continue
        intersections.remove((ai, bi, ui, vi))
    return tuple(sorted(intersections))
