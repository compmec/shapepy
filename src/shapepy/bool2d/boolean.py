"""
This modules contains the methods to compute the boolean
operations between the SubSetR2 instances
"""

from __future__ import annotations

from copy import copy
from fractions import Fraction
from typing import Dict, Iterable, Tuple, Union

from shapepy.geometry.jordancurve import JordanCurve

from ..geometry.segment import Segment
from ..geometry.unparam import USegment
from ..loggers import debug, get_logger
from ..tools import CyclicContainer, Is, NotExpectedError
from . import boolalg
from .base import EmptyShape, SubSetR2, WholeShape
from .graph import Edge, Graph, graph_manager, intersect_graphs, jordan2graph
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
    return Boolalg.clean(RecipeLazy.invert(subset))


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
    return Boolalg.clean(union)


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
    return Boolalg.clean(intersection)


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
    return Boolalg.clean(subset)


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
    subset = Boolalg.clean(subset)
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


class Boolalg:
    """Static methods to clean a SubSetR2 using algebraic simplifier"""

    alphabet = "abcdefghijklmnop"
    sub2var: Dict[SubSetR2, str] = {}

    @staticmethod
    def clean(subset: SubSetR2) -> SubSetR2:
        """Simplifies the subset"""

        if not Is.lazy(subset):
            return subset
        Boolalg.sub2var.clear()
        original = Boolalg.subset2expression(subset)
        simplified = boolalg.simplify(original)
        if simplified != original:
            subset = Boolalg.expression2subset(simplified)
        Boolalg.sub2var.clear()
        return subset

    @staticmethod
    def get_variable(subset: SubSetR2) -> str:
        """Gets the variable represeting the subset"""
        if subset not in Boolalg.sub2var:
            index = len(Boolalg.sub2var)
            if index > len(Boolalg.alphabet):
                raise ValueError("Too many variables")
            Boolalg.sub2var[subset] = Boolalg.alphabet[index]
        return Boolalg.sub2var[subset]

    @staticmethod
    def subset2expression(subset: SubSetR2) -> str:
        """Converts a SubSetR2 into a boolean expression"""
        if not is_lazy(subset):
            if Is.instance(subset, (EmptyShape, WholeShape)):
                raise NotExpectedError("Lazy does not contain these")
            return Boolalg.get_variable(subset)
        if Is.instance(subset, LazyNot):
            return boolalg.Formatter.invert_str(
                Boolalg.subset2expression(~subset)
            )
        internals = map(Boolalg.subset2expression, subset)
        if Is.instance(subset, LazyAnd):
            return boolalg.Formatter.mult_strs(internals, boolalg.AND)
        if Is.instance(subset, LazyOr):
            return boolalg.Formatter.mult_strs(internals, boolalg.OR)
        raise NotExpectedError

    @staticmethod
    def expression2subset(expression: str) -> SubSetR2:
        """Converts a boolean expression into a SubSetR2"""
        if expression == boolalg.TRUE:
            return WholeShape()
        if expression == boolalg.FALSE:
            return EmptyShape()
        for subset, variable in Boolalg.sub2var.items():
            if expression == variable:
                return subset
        expression = boolalg.remove_parentesis(expression)
        operator = boolalg.find_operator(expression)
        if operator == boolalg.NOT:
            subexpr = boolalg.extract(expression, boolalg.NOT)
            inverted = Boolalg.expression2subset(subexpr)
            return RecipeLazy.invert(inverted)
        subexprs = boolalg.extract(expression, operator)
        subsets = map(Boolalg.expression2subset, subexprs)
        if operator == boolalg.OR:
            return RecipeLazy.unite(subsets)
        if operator == boolalg.AND:
            return RecipeLazy.intersect(subsets)
        raise NotExpectedError(f"Invalid expression: {expression}")


class FollowPath:
    """
    Creates a graph from a jordan curve
    """
    piece = jordan.piecewise
    edges = []
    for knota, knotb in zip(piece.knots, piece.knots[1:]):
        path = SinglePath(piece, knota, knotb)
        edges.append(Edge({path}))
    return Graph(edges)


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


def shape2graph(
    shape: Union[SimpleShape, ConnectedShape, DisjointShape],
) -> Graph:
    """Converts a shape to a Graph"""
    if not Is.instance(shape, (SimpleShape, ConnectedShape, DisjointShape)):
        raise TypeError
    if Is.instance(shape, SimpleShape):
        return jordan2graph(shape.jordan)
    graph = Graph()
    for subshape in shape.subshapes:
        graph |= shape2graph(subshape)
    return graph


def remove_densities(graph: Graph, subsets: Iterable[SubSetR2], density: Real):
    """Removes the edges from the graph which density"""
    for subset in subsets:
        for edge in tuple(graph.edges):
            mid_point = edge.pointm
            if subset.density(mid_point) == density:
                graph.remove_edge(edge)


def extract_disjoint_graphs(graph: Graph) -> Iterable[Graph]:
    """Separates the given graph into a group of graphs that are disjoint"""
    edges = list(graph.edges)
    while len(edges) > 0:
        edge = edges.pop(0)
        current_edges = {edge}
        search_edges = {edge}
        while len(search_edges) > 0:
            end_nodes = {edge.nodeb for edge in search_edges}
            search_edges = {edge for edge in edges if edge.nodea in end_nodes}
            for edge in search_edges:
                edges.remove(edge)
            current_edges |= search_edges
        yield Graph(current_edges)


def possible_paths(
    edges: Iterable[Edge], start_node: Node = None
) -> Iterable[Tuple[Edge, ...]]:
    edges = tuple(edges)
    if start_node is None:
        nodes = {e.nodea for e in edges}
        for node in nodes:
            yield from possible_paths(edges, node)
        return
    indices = set(i for i, e in enumerate(edges) if e.nodea == start_node)
    other_edges = tuple(e for i, e in enumerate(edges) if i not in indices)
    for edge in (edges[i] for i in indices):
        for subpath in possible_paths(other_edges, edge.nodeb):
            yield (edge, ) + subpath 


def walk_closed_path(graph: Graph) -> CyclicContainer[Edge]:
    """Reads the graphs and extracts the unique paths"""
    if not Is.instance(graph, Graph):
        raise TypeError
    logger = get_logger("shapepy.bool2d.boolean")
    logger.debug("Extracting unique paths from the graph")
    logger.debug(str(graph))

    edges = tuple(graph.edges)
    start_node = None
    for edge in edges:
        if sum(1 if e.nodea == edge.nodea else 0 for e in edges) == 1:
            start_node = edge.nodea
            break
    for path in possible_paths(graph.edges, start_node):
        if path[0].nodea == path[-1].nodeb:
            return CyclicContainer(path)
    raise ValueError("Given graph does not contain a closed path")


@debug("shapepy.bool2d.boolean")
def edges_to_jordan(edges: CyclicContainer[Edge]) -> JordanCurve:
    """Converts the given connected edges into a Jordan Curve"""
    # logger = get_logger("shapepy.bool2d.boolean")
    # logger.info("Passed here")
    edges = tuple(edges)
    if len(edges) == 1:
        path = tuple(tuple(edges)[0].singles)[0]
        return JordanCurve(path.curve)
    usegments = []
    for edge in tuple(edges):
        path = tuple(edge.singles)[0]
        interval = [path.knota, path.knotb]
        # logger.info(f"interval = {interval}")
        subcurve = path.curve.section(interval)
        if Is.instance(subcurve, Segment):
            usegments.append(USegment(subcurve))
        else:
            usegments += list(map(USegment, subcurve))
    # logger.info(f"Returned: {len(usegments)}")
    # for i, useg in enumerate(usegments):
    #     logger.info(f"    {i}: {useg.parametrize()}")
    return JordanCurve(usegments)
