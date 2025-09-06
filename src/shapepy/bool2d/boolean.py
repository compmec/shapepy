"""
This modules contains the methods to compute the boolean
operations between the SubSetR2 instances
"""

from __future__ import annotations

from copy import copy
from fractions import Fraction
from typing import Dict, Iterable, List, Tuple

from shapepy.geometry.jordancurve import JordanCurve

from ..geometry.intersection import GeometricIntersectionCurves
from ..geometry.unparam import USegment
from ..loggers import debug
from ..scalar.boolalg import (
    AND,
    FALSE,
    NOT,
    OR,
    TRUE,
    extract,
    find_operator,
    intersect_strs,
    invert_str,
    simplify,
    unite_strs,
)
from ..tools import CyclicContainer, Is, NotExpectedError
from .base import EmptyShape, SubSetR2, WholeShape
from .lazy import LazyAnd, LazyNot, LazyOr, RecipeLazy, is_lazy
from .shape import (
    ConnectedShape,
    DisjointShape,
    SimpleShape,
    shape_from_jordans,
)


@debug("shapepy.bool2d.boolean")
def invert_bool2d(subset: SubSetR2) -> SubSetR2:
    """
    Computes the complementar set of given SubSetR2 instance

    Parameters
    ----------
    subsets: SubSetR2
        The subset to be inverted

    Return
    ------
    SubSetR2
        The complementar subset
    """
    return RecipeLazy.invert(subset)


@debug("shapepy.bool2d.boolean")
def unite_bool2d(subsets: Iterable[SubSetR2]) -> SubSetR2:
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
    return RecipeLazy.unite(subsets)


@debug("shapepy.bool2d.boolean")
def intersect_bool2d(subsets: Iterable[SubSetR2]) -> SubSetR2:
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
    return RecipeLazy.intersect(subsets)


@debug("shapepy.bool2d.boolean")
def xor_bool2d(subsets: Iterable[SubSetR2]) -> SubSetR2:
    """
    Computes the xor of given subsets

    Parameters
    ----------
    subsets: SubSetR2
        The subsets to compute the xor

    Return
    ------
    SubSetR2
        The intersection subset
    """
    return RecipeLazy.xor(subsets)


@debug("shapepy.bool2d.boolean")
def clean_bool2d(subset: SubSetR2) -> SubSetR2:
    """
    Computes the intersection of given subsets

    Parameters
    ----------
    subset: SubSetR2
        The subset to be cleaned

    Return
    ------
    SubSetR2
        The intersection subset
    """
    if not Is.lazy(subset):
        return subset
    subset = clean_with_boolalg(subset)
    if not Is.lazy(subset):
        return subset
    if Is.instance(subset, LazyNot):
        return clean_bool2d_not(subset)
    jordans = FollowPath.simplify(subset)
    if len(jordans) == 0:
        return EmptyShape() if Is.instance(subset, LazyAnd) else WholeShape()
    return shape_from_jordans(jordans)


@debug("shapepy.bool2d.boolean")
def clean_bool2d_not(subset: LazyNot) -> SubSetR2:
    """
    Cleans complementar of given subset

    Parameters
    ----------
    subset: SubSetR2
        The subset to be cleaned

    Return
    ------
    SubSetR2
        The cleaned subset
    """
    assert Is.instance(subset, LazyNot)
    inverted = ~subset
    if Is.instance(inverted, SimpleShape):
        return SimpleShape(~inverted.jordan, not inverted.boundary)
    raise NotImplementedError(f"Missing typo: {type(subset)}")


def clean_with_boolalg(subset: SubSetR2) -> SubSetR2:
    """Simplifies the subset"""

    if not Is.lazy(subset):
        raise TypeError("Expected Lazy operator")

    def create_variable(index: int) -> str:
        """"""
        if not Is.integer(index) or index > 16:
            raise ValueError(f"Invalid index {index}")
        alphabet = "abcdefghijklmnop"
        return alphabet[index]

    def subset2expression(
        subset: SubSetR2, dictvars: Dict[SubSetR2, str]
    ) -> str:
        """Converts a SubSetR2 into a boolean expression"""
        if not is_lazy(subset):
            if Is.instance(subset, EmptyShape):
                return FALSE
            if Is.instance(subset, WholeShape):
                return TRUE
            if subset not in dictvars:
                dictvars[subset] = create_variable(len(dictvars))
            return dictvars[subset]
        if Is.instance(subset, LazyNot):
            return invert_str(subset2expression(~subset, dictvars))
        internals = (subset2expression(s, dictvars) for s in subset)
        if Is.instance(subset, LazyAnd):
            return intersect_strs(internals)
        if Is.instance(subset, LazyOr):
            return unite_strs(internals)
        raise NotExpectedError

    def expression2subset(
        expression: str, dictvars: Dict[SubSetR2, str]
    ) -> SubSetR2:
        """Converts a boolean expression into a SubSetR2"""
        if expression == TRUE:
            return WholeShape()
        if expression == FALSE:
            return EmptyShape()
        for subset, var in dictvars.items():
            if expression == var:
                return subset
        operator = find_operator(expression)
        if operator == NOT:
            inverted = expression2subset(extract(expression, NOT), dictvars)
            return RecipeLazy.invert(inverted)
        subexprs = extract(expression, operator)
        subsets = (expression2subset(sub, subset2var) for sub in subexprs)
        if operator == OR:
            return RecipeLazy.unite(subsets)
        if operator == AND:
            return RecipeLazy.intersect(subsets)
        raise NotExpectedError(f"Invalid expression: {expression}")

    subset2var: Dict[SubSetR2, str] = {}
    original = subset2expression(subset, subset2var)
    simplified = simplify(original)
    if simplified != original:
        subset = expression2subset(simplified, subset2var)
    return subset


class FollowPath:
    """
    Class responsible to compute the final jordan curve
    result from boolean operation between two simple shapes

    """

    @staticmethod
    def split_on_intersection(
        all_jordans: Iterable[JordanCurve],
    ):
        """
        Find the intersections between two jordan curves and call split on the
        nodes which intersects
        """
        all_jordans = tuple(all_jordans)
        intersection = GeometricIntersectionCurves([])
        for i, jordani in enumerate(all_jordans):
            for j in range(i + 1, len(all_jordans)):
                jordanj = all_jordans[j]
                intersection |= jordani.piecewise & jordanj.piecewise
        intersection.evaluate()
        for jordan in all_jordans:
            split_knots = intersection.all_knots[id(jordan.piecewise)]
            jordan.piecewise.split(split_knots)

    @staticmethod
    def pursue_path(
        index_jordan: int, index_segment: int, jordans: Tuple[JordanCurve, ...]
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
            last_point = segment(1)
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
                if segj(0) == last_point:
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
        jordans: Tuple[JordanCurve, ...],
        start_indexs: Tuple[Tuple[int, int], ...],
    ) -> Tuple[JordanCurve]:
        """
        Returns a list of jordan curves which is the result
        of the intersection between 'jordansa' and 'jordansb'
        """
        assert all(map(Is.jordan, jordans))
        start_indexs = list(start_indexs)
        bez_indexs = []
        while len(start_indexs) > 0:
            ind_jord, ind_seg = start_indexs[0]
            indices_matrix = FollowPath.pursue_path(ind_jord, ind_seg, jordans)
            bez_indexs.append(indices_matrix)
            for pair in indices_matrix:
                if pair in start_indexs:
                    start_indexs.remove(pair)
        new_jordans = []
        for indices_matrix in bez_indexs:
            jordan = FollowPath.indexs_to_jordan(jordans, indices_matrix)
            new_jordans.append(jordan)
        return tuple(new_jordans)

    @staticmethod
    def midpoints_one_shape(
        subset: SubSetR2, jordan: JordanCurve, remove_wind: int
    ) -> Iterable[int]:
        """
        Returns a matrix [(a0, b0), (a1, b1), ...]
        such the middle point of
            shapea.jordans[a0].segments[b0]
        is inside/outside the shapeb

        If parameter ``closed`` is True, consider a
        point in boundary is inside.
        If ``closed=False``, a boundary point is outside

        """
        for j, segment in enumerate(jordan.parametrize()):
            mid_point = segment(Fraction(1, 2))
            density = subset.density(mid_point)
            if float(density) != remove_wind:
                yield j

    @staticmethod
    @debug("shapepy.bool2d.boolean")
    def midpoints_shapes(
        subset: SubSetR2, jordans: Tuple[JordanCurve, ...], remove_wind: int
    ) -> Tuple[Tuple[int, int], ...]:
        """
        This function computes the indexes of the midpoints from
        both shapes, shifting the indexs of shapeb.jordans
        """
        indices: List[Tuple[int, int]] = []
        for i, jordan in enumerate(jordans):
            indexs = FollowPath.midpoints_one_shape(
                subset, jordan, remove_wind
            )
            for j in indexs:
                indices.append((i, j))
        return tuple(indices)

    @staticmethod
    def simplify(subset: SubSetR2) -> Tuple[JordanCurve, ...]:
        """
        Computes the set of jordan curves that defines the boundary of
        the intersection between the two base shapes
        """
        assert Is.instance(subset, (LazyAnd, LazyOr))
        all_jordans = tuple(
            {id(c): c for c in FollowPath.extract_jordans(subset)}.values()
        )
        FollowPath.split_on_intersection(all_jordans)
        wind = 1 if Is.instance(subset, LazyOr) else 0
        indexs = FollowPath.midpoints_shapes(
            subset, all_jordans, remove_wind=wind
        )
        new_jordans = FollowPath.follow_path(all_jordans, indexs)
        return new_jordans

    @staticmethod
    def extract_jordans(subset: SubSetR2) -> Iterable[JordanCurve]:
        """Recovers all the jordan curves from given subset"""
        if Is.instance(subset, SimpleShape):
            yield subset.jordan
        elif Is.instance(subset, (ConnectedShape, DisjointShape)):
            for sub in subset.subshapes:
                yield from FollowPath.extract_jordans(sub)
        elif Is.instance(subset, (LazyAnd, LazyOr)):
            for sub in subset:
                yield from FollowPath.extract_jordans(sub)
        elif Is.instance(subset, LazyNot):
            for jordan in FollowPath.extract_jordans(~subset):
                yield ~jordan
        else:
            raise NotExpectedError(f"Received typo: {type(subset)}")
