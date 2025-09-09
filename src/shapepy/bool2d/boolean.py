"""
This modules contains the methods to compute the boolean
operations between the SubSetR2 instances
"""

from __future__ import annotations

from copy import copy
from fractions import Fraction
from typing import Dict, Iterable, Tuple, Union

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
    return clean_with_boolalg(RecipeLazy.invert(subset))


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
    union = RecipeLazy.unite(subsets)
    return clean_with_boolalg(union)


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
    intersection = RecipeLazy.intersect(subsets)
    return clean_with_boolalg(intersection)


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
    subset = RecipeLazy.xor(subsets)
    return clean_with_boolalg(subset)


# pylint: disable=too-many-return-statements
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
    subset = clean_with_boolalg(subset)
    if not Is.lazy(subset):
        return subset
    if Is.instance(subset, LazyNot):
        return clean_bool2d_not(subset)
    subsets = tuple(subset)
    assert len(subsets) == 2
    shapea, shapeb = subsets
    shapea = clean_bool2d(shapea)
    shapeb = clean_bool2d(shapeb)
    if Is.instance(subset, LazyAnd):
        if shapeb in shapea:
            return copy(shapeb)
        if shapea in shapeb:
            return copy(shapea)
        jordans = FollowPath.and_shapes(shapea, shapeb)
    elif Is.instance(subset, LazyOr):
        if shapeb in shapea:
            return copy(shapea)
        if shapea in shapeb:
            return copy(shapeb)
        jordans = FollowPath.or_shapes(shapea, shapeb)
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
        return SimpleShape(~inverted.jordan, True)
    if Is.instance(inverted, ConnectedShape):
        return DisjointShape(~simple for simple in inverted.subshapes)
    if Is.instance(inverted, DisjointShape):
        new_jordans = tuple(~jordan for jordan in inverted.jordans)
        return shape_from_jordans(new_jordans)
    raise NotImplementedError(f"Missing typo: {type(inverted)}")


def clean_with_boolalg(subset: SubSetR2) -> SubSetR2:
    """Simplifies the subset"""

    if not Is.lazy(subset):
        return subset

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
            if Is.instance(subset, (EmptyShape, WholeShape)):
                raise NotExpectedError("Lazy does not contain these")
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
        while operator is None:
            expression = expression[1:-1]
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
            for j, segment in enumerate(jordan.parametrize()):
                mid_point = segment(Fraction(1, 2))
                density = shapeb.density(mid_point)
                mid_point_in = (float(density) > 0 and closed) or density == 1
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
        assert Is.instance(
            shapea, (SimpleShape, ConnectedShape, DisjointShape)
        )
        assert Is.instance(
            shapeb, (SimpleShape, ConnectedShape, DisjointShape)
        )
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
        assert Is.instance(
            shapea, (SimpleShape, ConnectedShape, DisjointShape)
        )
        assert Is.instance(
            shapeb, (SimpleShape, ConnectedShape, DisjointShape)
        )
        FollowPath.split_on_intersection([shapea.jordans, shapeb.jordans])
        indexs = FollowPath.midpoints_shapes(
            shapea, shapeb, closed=False, inside=True
        )
        all_jordans = tuple(shapea.jordans) + tuple(shapeb.jordans)
        new_jordans = FollowPath.follow_path(all_jordans, indexs)
        return new_jordans
