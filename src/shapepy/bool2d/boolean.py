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
from ..tools import CyclicContainer, Is, NotExpectedError
from .base import EmptyShape, SubSetR2, WholeShape
from .container import (
    LazyAnd,
    LazyNot,
    LazyOr,
    expand_morgans,
    recipe_and,
    recipe_not,
    recipe_or,
)
from .shape import ConnectedShape, DisjointShape, SimpleShape


@debug("shapepy.bool2d.boolean")
def unite_bool2d(subsets: Iterable[SubSetR2], clean: bool = True) -> SubSetR2:
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
    recipe = recipe_or(subsets)
    return recipe if not clean else clean_bool2d(recipe)


@debug("shapepy.bool2d.boolean")
def intersect_bool2d(
    subsets: Iterable[SubSetR2], clean: bool = True
) -> SubSetR2:
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
    recipe = recipe_and(subsets)
    return recipe if not clean else clean_bool2d(recipe)


@debug("shapepy.bool2d.boolean")
def invert_bool2d(subset: SubSetR2, clean=True) -> SubSetR2:
    """
    Computes the complementar of the give subset

    Parameters
    ----------
    subset: SubSetR2
        The subset to be inverted

    Return
    ------
    SubSetR2
        The complementar subset
    """
    recipe = recipe_not(subset)
    return recipe if not clean else clean_bool2d(recipe)


# pylint: disable=too-many-branches,too-many-return-statements
@debug("shapepy.bool2d.boolean")
def clean_bool2d(subset: SubSetR2) -> SubSetR2:
    """
    Cleans or Simplifies the given subset
    """
    subset = filter_xor(subset)
    subset = expand_morgans(subset)
    subset = filter_xor(subset)
    subset = expand_morgans(subset)
    if not Is.instance(subset, (LazyAnd, LazyNot, LazyOr)):
        return copy(subset)
    if Is.instance(subset, LazyNot):
        return simplifies_inverse(~subset)
    assert len(subset) == 2
    shapea, shapeb = subset
    if not Is.instance(shapea, (SimpleShape, ConnectedShape, DisjointShape)):
        shapea = clean_bool2d(shapea)
    if not Is.instance(shapeb, (SimpleShape, ConnectedShape, DisjointShape)):
        shapeb = clean_bool2d(shapeb)
    if shapea in shapeb:
        return copy(shapea if Is.instance(subset, LazyAnd) else shapeb)
    if shapeb in shapea:
        return copy(shapeb if Is.instance(subset, LazyAnd) else shapea)
    if Is.instance(subset, LazyAnd):
        new_jordans = FollowPath.and_shapes(shapea, shapeb)
        if len(new_jordans) == 0:
            return EmptyShape()
    elif Is.instance(subset, LazyOr):
        new_jordans = FollowPath.or_shapes(shapea, shapeb)
        if len(new_jordans) == 0:
            return WholeShape()
    else:
        raise NotExpectedError
    simples = map(SimpleShape, new_jordans)
    return shape_from_simples(simples)


@debug("shapepy.bool2d.boolean")
def simplifies_inverse(invsubset: SubSetR2) -> SubSetR2:
    """Simplifies the value of (~subset)"""
    if Is.instance(invsubset, (EmptyShape, WholeShape, SimpleShape)):
        return -invsubset
    if Is.instance(invsubset, ConnectedShape):
        return DisjointShape(-simple for simple in invsubset.subshapes)
    if Is.instance(invsubset, DisjointShape):
        simples = []
        for subsubshape in invsubset.subshapes:
            if Is.instance(subsubshape, SimpleShape):
                simples.append(invert_bool2d(subsubshape))
            elif Is.instance(subsubshape, ConnectedShape):
                simples += list(map(invert_bool2d, subsubshape.subshapes))
            else:
                raise NotExpectedError(str(type(subsubshape)))
        return shape_from_simples(simples)
    raise NotExpectedError(str(type(invsubset)))


@debug("shapepy.bool2d.boolean")
def filter_xor(subset: SubSetR2) -> SubSetR2:
    """Simplifies the subset searching for XOR operations

    * AND[X, NOT[X]] -> EmptyShape
    * OR[X, NOT[X]] -> WholeShape
    """
    if not Is.instance(subset, (LazyAnd, LazyOr)):
        return subset
    internals = tuple(filter_xor(i) for i in subset)
    lazynots = tuple(i for i in internals if Is.instance(i, LazyNot))
    notlazys = tuple(i for i in internals if not Is.instance(i, LazyNot))
    for lazyn in lazynots:
        for nlazy in notlazys:
            if ~lazyn == nlazy:
                return (
                    WholeShape()
                    if Is.instance(subset, LazyOr)
                    else EmptyShape()
                )
    return (
        recipe_or(internals)
        if Is.instance(subset, LazyOr)
        else recipe_and(internals)
    )


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
    @debug("shapepy.bool2d.boolean")
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
    @debug("shapepy.bool2d.boolean")
    def or_shapes(
        shapea: SubSetR2, shapeb: SubSetR2
    ) -> Tuple[JordanCurve, ...]:
        """
        Computes the set of jordan curves that defines the boundary of
        the union between the two base shapes
        """
        if not Is.instance(
            shapea, (SimpleShape, ConnectedShape, DisjointShape)
        ):
            raise TypeError(str(type(shapea)))
        if not Is.instance(
            shapeb, (SimpleShape, ConnectedShape, DisjointShape)
        ):
            raise TypeError(str(type(shapeb)))
        FollowPath.split_on_intersection([shapea.jordans, shapeb.jordans])
        indexs = FollowPath.midpoints_shapes(
            shapea, shapeb, closed=True, inside=False
        )
        all_jordans = tuple(shapea.jordans) + tuple(shapeb.jordans)
        new_jordans = FollowPath.follow_path(all_jordans, indexs)
        return new_jordans

    @staticmethod
    @debug("shapepy.bool2d.boolean")
    def and_shapes(
        shapea: SubSetR2, shapeb: SubSetR2
    ) -> Tuple[JordanCurve, ...]:
        """
        Computes the set of jordan curves that defines the boundary of
        the intersection between the two base shapes
        """
        if not Is.instance(
            shapea, (SimpleShape, ConnectedShape, DisjointShape)
        ):
            raise TypeError(str(type(shapea)))
        if not Is.instance(
            shapeb, (SimpleShape, ConnectedShape, DisjointShape)
        ):
            raise TypeError(str(type(shapeb)))
        FollowPath.split_on_intersection([shapea.jordans, shapeb.jordans])
        indexs = FollowPath.midpoints_shapes(
            shapea, shapeb, closed=False, inside=True
        )
        all_jordans = tuple(shapea.jordans) + tuple(shapeb.jordans)
        new_jordans = FollowPath.follow_path(all_jordans, indexs)
        return new_jordans


def divide_connecteds(
    simples: Tuple[SimpleShape],
) -> Tuple[Union[SimpleShape, ConnectedShape]]:
    """
    Divides the simples in groups of connected shapes

    The idea is get the simple shape with maximum abs area,
    this is the biggest shape of all we start from it.

    We them separate all shapes in inside and outside
    """
    simples = list(simples)
    if len(simples) == 0:
        return tuple()
    for simple in simples:
        if not Is.instance(simple, SimpleShape):
            raise TypeError(f"Invalid type {type(simple)}")
    externals = []
    connected = []
    while len(simples) != 0:
        areas = (s.area for s in simples)
        absareas = tuple(map(abs, areas))
        index = absareas.index(max(absareas))
        connected.append(simples.pop(index))
        internal = []
        while len(simples) != 0:  # Divide in two groups
            simple = simples.pop(0)
            jordan = simple.jordan
            for subsimple in connected:
                subjordan = subsimple.jordan
                if jordan not in subsimple or subjordan not in simple:
                    externals.append(simple)
                    break
            else:
                internal.append(simple)
        simples = internal
    if len(connected) == 1:
        connected = connected[0]
    else:
        connected = ConnectedShape(connected)
    return (connected,) + divide_connecteds(externals)


def shape_from_simples(simples: Tuple[SimpleShape, ...]) -> SubSetR2:
    """Returns the correspondent shape

    This function don't do entry validation
    as verify if one shape is inside other

    Example
    ----------
    >>> shape_from_jordans([])
    EmptyShape
    """
    simples = tuple(simples)
    for simple in simples:
        if not Is.instance(simple, SimpleShape):
            raise TypeError(f"Invalid type = {type(simple)}")
    assert len(simples) != 0
    if len(simples) == 1:
        return simples[0]
    connecteds = divide_connecteds(simples)
    if len(connecteds) == 1:
        return connecteds[0]
    return DisjointShape(connecteds)
