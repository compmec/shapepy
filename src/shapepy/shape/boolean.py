"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""

from __future__ import annotations

from copy import copy
from fractions import Fraction
from typing import Any, Tuple

from shapepy.core import IShape

from ..curve.abc import IJordanCurve


class FollowPath:
    """
    Class responsible to compute the final jordan curve
    result from boolean operation between two simple shapes

    """

    @staticmethod
    def split_two_jordans(jordana: IJordanCurve, jordanb: IJordanCurve):
        """
        Find the intersections between two jordan curves and call split on the
        nodes which intersects
        """
        assert isinstance(jordana, IJordanCurve)
        assert isinstance(jordanb, IJordanCurve)
        if jordana.box() & jordanb.box() is None:
            return
        all_positions = (set(), set())
        inters = jordana & jordanb
        for ai, bj, ui, vj in inters:
            all_positions[0].add((ai, ui))
            all_positions[1].add((bj, vj))
        all_positions = [tuple(sorted(nodes)) for nodes in all_positions]
        for positions, jordan in zip(all_positions, (jordana, jordanb)):
            indexs = [position[0] for position in positions]
            nodes = [position[1] for position in positions]
            jordan.split(indexs, nodes)

    @staticmethod
    def pursue_path(
        index_jordan: int, index_segment: int, jordans: Tuple[IJordanCurve]
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
        assert isinstance(oneobj, (tuple, list))
        assert isinstance(other, (tuple, list))
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
        jordans: Tuple[IJordanCurve], matrix_indexs: Tuple[Tuple[int, int]]
    ) -> IJordanCurve:
        """
        Given 'n' jordan curves, and a matrix of integers
        [(a0, b0), (a1, b1), ..., (am, bm)]
        Returns a myjordan (IJordanCurve instance) such
        len(myjordan.segments) = matrix_indexs.shape[0]
        myjordan.segments[i] = jordans[ai].segments[bi]
        """
        beziers = []
        for index_jordan, index_segment in matrix_indexs:
            new_bezier = jordans[index_jordan].segments[index_segment]
            new_bezier = copy(new_bezier)
            beziers.append(new_bezier)
        new_jordan = IJordanCurve.from_segments(beziers)
        return new_jordan

    @staticmethod
    def follow_path(
        jordans: Tuple[IJordanCurve], start_indexs: Tuple[Tuple[int]]
    ) -> Tuple[IJordanCurve]:
        """
        Returns a list of jordan curves which is the result
        of the intersection between 'jordansa' and 'jordansb'
        """
        for jordan in jordans:
            assert isinstance(jordan, IJordanCurve)
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
        shapea: IShape, shapeb: IShape, closed: bool, inside: bool
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
        shapea: IShape, shapeb: IShape, closed: bool, inside: bool
    ) -> Tuple[Tuple[int]]:
        indexsa = FollowPath.midpoints_one_shape(
            shapea, shapeb, closed, inside
        )
        indexsb = FollowPath.midpoints_one_shape(
            shapeb, shapea, closed, inside
        )
        indexsa = list(indexsa)
        njordansa = len(shapea.jordans)
        for indjorb, indsegb in indexsb:
            indexsa.append((njordansa + indjorb, indsegb))
        return tuple(indexsa)

    @staticmethod
    def or_shapes(shapea: IShape, shapeb: IShape) -> Tuple[IJordanCurve]:
        assert isinstance(shapea, IShape)
        assert isinstance(shapeb, IShape)
        for jordana in shapea.jordans:
            for jordanb in shapeb.jordans:
                FollowPath.split_two_jordans(jordana, jordanb)
        indexs = FollowPath.midpoints_shapes(
            shapea, shapeb, closed=True, inside=False
        )
        all_jordans = tuple(shapea.jordans) + tuple(shapeb.jordans)
        new_jordans = FollowPath.follow_path(all_jordans, indexs)
        return new_jordans

    @staticmethod
    def and_shapes(shapea: IShape, shapeb: IShape) -> Tuple[IJordanCurve]:
        assert isinstance(shapea, IShape)
        assert isinstance(shapeb, IShape)
        for jordana in shapea.jordans:
            for jordanb in shapeb.jordans:
                FollowPath.split_two_jordans(jordana, jordanb)
        indexs = FollowPath.midpoints_shapes(
            shapea, shapeb, closed=False, inside=True
        )
        all_jordans = tuple(shapea.jordans) + tuple(shapeb.jordans)
        new_jordans = FollowPath.follow_path(all_jordans, indexs)
        return new_jordans
