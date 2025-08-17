"""
This modules contains the methods to compute the boolean
operations between the SubSetR2 instances
"""

from __future__ import annotations

from copy import copy
from fractions import Fraction
from typing import Iterable, Tuple, Union

from shapepy.geometry.jordancurve import JordanCurve

from ..geometry.intersection import GeometricIntersectionCurves
from ..geometry.unparam import USegment
from ..loggers import debug
from ..tools import CyclicContainer, Is
from .base import EmptyShape, SubSetR2, WholeShape
from .shape import (
    ConnectedShape,
    DisjointShape,
    SimpleShape,
    shape_from_jordans,
)


@debug("shapepy.bool2d.boolean")
def unite(subsets: Iterable[SubSetR2]) -> SubSetR2:
    """
    Computes the union of given subsets

    Parameters
    ----------
    subsets: SubSetR2
        The subsets to be united

    Return
    ------
    SubSetR2
        The united subset
    """
    subsets = tuple(subsets)
    assert len(subsets) == 2
    assert Is.instance(subsets[0], SubSetR2)
    assert Is.instance(subsets[1], SubSetR2)
    if Is.instance(subsets[1], WholeShape):
        return WholeShape()
    if Is.instance(subsets[1], EmptyShape):
        return copy(subsets[0])
    if subsets[1] in subsets[0]:
        return copy(subsets[0])
    if subsets[0] in subsets[1]:
        return copy(subsets[1])
    new_jordans = FollowPath.or_shapes(subsets[0], subsets[1])
    if len(new_jordans) == 0:
        return WholeShape()
    return shape_from_jordans(new_jordans)


@debug("shapepy.bool2d.boolean")
def intersect(subsets: Iterable[SubSetR2]) -> SubSetR2:
    """
    Computes the intersection of given subsets

    Parameters
    ----------
    subsets: SubSetR2
        The subsets to be intersected

    Return
    ------
    SubSetR2
        The intersection subset
    """
    subsets = tuple(subsets)
    assert len(subsets) == 2
    assert Is.instance(subsets[0], SubSetR2)
    assert Is.instance(subsets[1], SubSetR2)
    if Is.instance(subsets[1], WholeShape):
        return copy(subsets[0])
    if Is.instance(subsets[1], EmptyShape):
        return EmptyShape()
    if subsets[1] in subsets[0]:
        return copy(subsets[1])
    if subsets[0] in subsets[1]:
        return copy(subsets[0])
    new_jordans = FollowPath.and_shapes(subsets[0], subsets[1])
    if len(new_jordans) == 0:
        return EmptyShape()
    return shape_from_jordans(new_jordans)


class FollowPath:
    """
    Class responsible to compute the final jordan curve
    result from boolean operation between two simple shapes

    """

    @staticmethod
    def split_on_intersection(
        all_group_jordans: Iterable[Iterable[JordanCurve]],
    ):
        """
        Find the intersections between two jordan curves and call split on the
        nodes which intersects
        """
        intersection = GeometricIntersectionCurves([])
        all_group_jordans = tuple(map(tuple, all_group_jordans))
        for i, jordansi in enumerate(all_group_jordans):
            for j in range(i + 1, len(all_group_jordans)):
                jordansj = all_group_jordans[j]
                for jordana in jordansi:
                    for jordanb in jordansj:
                        intersection |= jordana.piecewise & jordanb.piecewise
        intersection.evaluate()
        for jordans in all_group_jordans:
            for jordan in jordans:
                split_knots = intersection.all_knots[id(jordan.piecewise)]
                jordan.piecewise.split(split_knots)

    @staticmethod
    def pursue_path(
        index_jordan: int, index_segment: int, jordans: Tuple[JordanCurve]
    ) -> CyclicContainer[Tuple[int, int]]:
        """
        Given a list of jordans, it returns a matrix of integers like
        [(a1, b1), (a2, b2), (a3, b3), ..., (an, bn)] such
            End point of jordans[a_{i}].segments[b_{i}]
            Start point of jordans[a_{i+1}].segments[b_{i+1}]
        are equal

        The first point (a1, b1) = (index_jordan, index_segment)

        The end point of jordans[an].segments[bn] is equal to
        the start point of jordans[a1].segments[b1]

        We suppose there's no triple intersection
        """
        matrix = []
        all_segments = [tuple(jordan.piecewise) for jordan in jordans]
        while True:
            index_segment %= len(all_segments[index_jordan])
            segment = all_segments[index_jordan][index_segment]
            if (index_jordan, index_segment) in matrix:
                break
            matrix.append((index_jordan, index_segment))
            last_point = segment.ctrlpoints[-1]
            possibles = []
            for i, jordan in enumerate(jordans):
                if i == index_jordan:
                    continue
                if last_point in jordan:
                    possibles.append(i)
            if len(possibles) == 0:
                index_segment += 1
                continue
            index_jordan = possibles[0]
            for j, segj in enumerate(all_segments[index_jordan]):
                if segj.ctrlpoints[0] == last_point:
                    index_segment = j
                    break
        return CyclicContainer(matrix)

    @staticmethod
    def indexs_to_jordan(
        jordans: Tuple[JordanCurve],
        matrix_indexs: CyclicContainer[Tuple[int, int]],
    ) -> JordanCurve:
        """
        Given 'n' jordan curves, and a matrix of integers
        [(a0, b0), (a1, b1), ..., (am, bm)]
        Returns a myjordan (JordanCurve instance) such
        len(myjordan.segments) = matrix_indexs.shape[0]
        myjordan.segments[i] = jordans[ai].segments[bi]
        """
        beziers = []
        for index_jordan, index_segment in matrix_indexs:
            new_bezier = jordans[index_jordan].piecewise[index_segment]
            new_bezier = copy(new_bezier)
            beziers.append(USegment(new_bezier))
        new_jordan = JordanCurve(beziers)
        return new_jordan

    @staticmethod
    def follow_path(
        jordans: Tuple[JordanCurve], start_indexs: Tuple[Tuple[int]]
    ) -> Tuple[JordanCurve]:
        """
        Returns a list of jordan curves which is the result
        of the intersection between 'jordansa' and 'jordansb'
        """
        assert all(map(Is.jordan, jordans))
        bez_indexs = []
        for ind_jord, ind_seg in start_indexs:
            indices_matrix = FollowPath.pursue_path(ind_jord, ind_seg, jordans)
            if indices_matrix not in bez_indexs:
                bez_indexs.append(indices_matrix)
        new_jordans = []
        for indices_matrix in bez_indexs:
            jordan = FollowPath.indexs_to_jordan(jordans, indices_matrix)
            new_jordans.append(jordan)
        return tuple(new_jordans)

    @staticmethod
    def midpoints_one_shape(
        shapea: Union[SimpleShape, ConnectedShape, DisjointShape],
        shapeb: Union[SimpleShape, ConnectedShape, DisjointShape],
        closed: bool,
        inside: bool,
    ) -> Iterable[Tuple[int, int]]:
        """
        Returns a matrix [(a0, b0), (a1, b1), ...]
        such the middle point of
            shapea.jordans[a0].segments[b0]
        is inside/outside the shapeb

        If parameter ``closed`` is True, consider a
        point in boundary is inside.
        If ``closed=False``, a boundary point is outside

        """
        for i, jordan in enumerate(shapea.jordans):
            for j, segment in enumerate(jordan.piecewise):
                mid_point = segment(Fraction(1, 2))
                wind = shapeb.winding(mid_point)
                mid_point_in = (wind > 0 and closed) or wind == 1
                if not inside ^ mid_point_in:
                    yield (i, j)

    @staticmethod
    def midpoints_shapes(
        shapea: SubSetR2, shapeb: SubSetR2, closed: bool, inside: bool
    ) -> Tuple[Tuple[int, int]]:
        """
        This function computes the indexes of the midpoints from
        both shapes, shifting the indexs of shapeb.jordans
        """
        indexsa = FollowPath.midpoints_one_shape(
            shapea, shapeb, closed, inside
        )
        indexsb = FollowPath.midpoints_one_shape(  # pylint: disable=W1114
            shapeb, shapea, closed, inside
        )
        indexsa = list(indexsa)
        njordansa = len(shapea.jordans)
        for indjorb, indsegb in indexsb:
            indexsa.append((njordansa + indjorb, indsegb))
        return tuple(indexsa)

    @staticmethod
    def or_shapes(shapea: SubSetR2, shapeb: SubSetR2) -> Tuple[JordanCurve]:
        """
        Computes the set of jordan curves that defines the boundary of
        the union between the two base shapes
        """
        assert Is.instance(shapea, SubSetR2)
        assert Is.instance(shapeb, SubSetR2)
        FollowPath.split_on_intersection([shapea.jordans, shapeb.jordans])
        indexs = FollowPath.midpoints_shapes(
            shapea, shapeb, closed=True, inside=False
        )
        all_jordans = tuple(shapea.jordans) + tuple(shapeb.jordans)
        new_jordans = FollowPath.follow_path(all_jordans, indexs)
        return new_jordans

    @staticmethod
    def and_shapes(shapea: SubSetR2, shapeb: SubSetR2) -> Tuple[JordanCurve]:
        """
        Computes the set of jordan curves that defines the boundary of
        the intersection between the two base shapes
        """
        assert Is.instance(shapea, SubSetR2)
        assert Is.instance(shapeb, SubSetR2)
        FollowPath.split_on_intersection([shapea.jordans, shapeb.jordans])
        indexs = FollowPath.midpoints_shapes(
            shapea, shapeb, closed=False, inside=True
        )
        all_jordans = tuple(shapea.jordans) + tuple(shapeb.jordans)
        new_jordans = FollowPath.follow_path(all_jordans, indexs)
        return new_jordans
