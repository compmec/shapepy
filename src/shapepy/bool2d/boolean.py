"""
This modules contains the methods to compute the boolean
operations between the SubSetR2 instances
"""

from __future__ import annotations

from copy import copy
from fractions import Fraction
from typing import Any, Iterable, Tuple

from shapepy.geometry.jordancurve import JordanCurve

from ..geometry.intersection import GeometricIntersectionCurves
from ..tools import Is
from .base import EmptyShape, SubSetR2, WholeShape
from .shape import shape_from_jordans


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
    new_jordans = FollowPath.or_shapes(subsets[0], subsets[1])
    if len(new_jordans) == 0:
        return WholeShape()
    return shape_from_jordans(new_jordans)


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
                        intersection |= jordana & jordanb
        intersection.evaluate()
        for jordans in all_group_jordans:
            for jordan in jordans:
                piece = jordan.piecewise
                piece.snap(intersection.all_knots[id(jordan)])

    @staticmethod
    def pursue_path(
        index_jordan: int, index_segment: int, jordans: Tuple[JordanCurve]
    ) -> Tuple[Tuple[int]]:
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
        all_segments = [jordan.segments for jordan in jordans]
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
        return tuple(matrix)

    @staticmethod
    def is_rotation(oneobj: Tuple[Any], other: Tuple[Any]) -> bool:
        """
        Tells if a list is equal to another
        """
        assert Is.iterable(oneobj)
        assert Is.iterable(other)
        oneobj = tuple(oneobj)
        other = tuple(other)
        if len(oneobj) != len(other):
            return False
        rotation = 0
        for elem in oneobj:
            if elem == other[0]:
                break
            rotation += 1
        else:
            return False
        nelems = len(other)
        for i, elem in enumerate(other):
            j = (i + rotation) % nelems
            if elem != oneobj[j]:
                return False
        return True

    @staticmethod
    def filter_rotations(matrix: Tuple[Tuple[Any]]):
        """
        Remove repeted elements in matrix such they are only rotations

        Example:
        filter_tuples([[A, B, C], [B, C, A]]) -> [[A, B, C]]
        filter_tuples([[A, B, C], [C, B, A]]) -> [[A, B, C], [C, B, A]]
        """
        filtered = []
        for line in matrix:
            for fline in filtered:
                if FollowPath.is_rotation(line, fline):
                    break
            else:
                filtered.append(line)
        return tuple(filtered)

    @staticmethod
    def indexs_to_jordan(
        jordans: Tuple[JordanCurve], matrix_indexs: Tuple[Tuple[int, int]]
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
            new_bezier = jordans[index_jordan].segments[index_segment]
            new_bezier = copy(new_bezier)
            beziers.append(new_bezier)
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
            bez_indexs.append(indices_matrix)
        bez_indexs = FollowPath.filter_rotations(bez_indexs)
        new_jordans = []
        for indices_matrix in bez_indexs:
            jordan = FollowPath.indexs_to_jordan(jordans, indices_matrix)
            new_jordans.append(jordan)
        return tuple(new_jordans)

    @staticmethod
    def midpoints_one_shape(
        shapea: SubSetR2, shapeb: SubSetR2, closed: bool, inside: bool
    ) -> Tuple[Tuple[int]]:
        """
        Returns a matrix [(a0, b0), (a1, b1), ...]
        such the middle point of
            shapea.jordans[a0].segments[b0]
        is inside/outside the shapeb

        If parameter ``closed`` is True, consider a
        point in boundary is inside.
        If ``closed=False``, a boundary point is outside

        """

        insiders = []
        outsiders = []
        for i, jordan in enumerate(shapea.jordans):
            for j, segment in enumerate(jordan.segments):
                mid_point = segment(Fraction(1, 2))
                if shapeb.contains_point(mid_point, closed):
                    insiders.append((i, j))
                else:
                    outsiders.append((i, j))
        return tuple(insiders) if inside else tuple(outsiders)

    @staticmethod
    def midpoints_shapes(
        shapea: SubSetR2, shapeb: SubSetR2, closed: bool, inside: bool
    ) -> Tuple[Tuple[int]]:
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
