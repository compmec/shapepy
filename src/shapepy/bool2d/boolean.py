"""
This modules contains the methods to compute the boolean
operations between the SubSetR2 instances
"""

from __future__ import annotations

from copy import copy
from fractions import Fraction
from typing import Dict, Iterable, Tuple, Union, Iterator

from shapepy.geometry.jordancurve import JordanCurve

from ..geometry.segment import Segment
from ..geometry.unparam import USegment
from ..loggers import debug, get_logger
from ..tools import CyclicContainer, Is, NotExpectedError
from . import boolalg
from .base import EmptyShape, SubSetR2, WholeShape
from .graph import Edge, Graph, graph_manager, intersect_graphs, curve2graph, Node
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
    jordans = GraphComputer.clean(subset)
    if len(jordans) == 0:
        density = subset.density((0, 0))
        return EmptyShape() if float(density) == 0 else WholeShape()
    return shape_from_jordans(jordans)



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



class GraphComputer:


    def clean(subset: SubSetR2) -> SubSetR2:
        """Cleans the subset using the graphs"""
        extractor = GraphComputer.extract(subset)
        simples = tuple({id(s): s for s in extractor}.values())
        piecewises = tuple(s.jordan.piecewise for s in simples)
        with graph_manager():
            graphs = tuple(map(curve2graph, piecewises))
            graph = intersect_graphs(graphs)
            for edge in tuple(graph.edges):
                density = subset.density(edge.pointm)
                if not (0 < float(density) < 1):
                    graph.remove_edge(edge)



    def extract(subset: SubSetR2) -> Iterator[SimpleShape]:
        """Extracts the simple shapes from the subset"""
        if Is.instance(subset, SimpleShape):
            yield subset
        elif Is.instance(subset, (ConnectedShape, DisjointShape)):
            for subshape in subset.subshapes:
                yield from GraphComputer.extract(subshape)
        elif Is.instance(subset, LazyNot):
            yield from GraphComputer.extract(~subset)
        elif Is.instance(subset, (LazyOr, LazyAnd)):
            for subsubset in subset:
                yield from GraphComputer.extract(subsubset)


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


    def possible_paths(edges: Iterable[Edge], start_node: Node) -> Iterator[Tuple[Edge, ...]]:
        """Returns all the possible paths that begins at start_node"""
        edges = tuple(edges)
        indices = set(i for i, e in enumerate(edges) if e.nodea == start_node)
        other_edges = tuple(e for i, e in enumerate(edges) if i not in indices)
        for edge in (edges[i] for i in indices):
            subpaths = GraphComputer.possible_paths(other_edges, edge.nodeb)
            for subpath in subpaths:
                yield (edge, ) + subpath 


    def possible_closed_paths(graph: Graph) -> CyclicContainer[Edge]:
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
        paths = GraphComputer.possible_paths(graph.edges, start_node)
        for path in paths:
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
