"""
This modules contains the methods to compute the boolean
operations between the SubSetR2 instances
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, Iterator, Tuple, Union

from shapepy.geometry.jordancurve import JordanCurve

from ..geometry.segment import Segment
from ..geometry.unparam import USegment
from ..loggers import debug, get_logger
from ..tools import CyclicContainer, Is, NotExpectedError
from . import boolalg
from .base import EmptyShape, Future, SubSetR2, WholeShape
from .config import Config
from .curve import SingleCurve
from .graph import (
    Edge,
    Graph,
    Node,
    curve2graph,
    graph_manager,
    intersect_graphs,
)
from .lazy import LazyAnd, LazyNot, LazyOr, RecipeLazy, is_lazy
from .point import SinglePoint
from .shape import ConnectedShape, DisjointShape, SimpleShape


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
    logger = get_logger("shapepy.bool2d.boole")
    jordans = GraphComputer.clean(subset)
    for i, jordan in enumerate(jordans):
        logger.debug(f"{i}: {jordan}")
    if len(jordans) == 0:
        density = subset.density((0, 0))
        return EmptyShape() if float(density) == 0 else WholeShape()
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
        return DisjointShape((~s).clean() for s in inverted)
    if Is.instance(inverted, DisjointShape):
        return shape_from_jordans(~jordan for jordan in inverted.jordans)
    raise NotImplementedError(f"Missing typo: {type(inverted)}")


@debug("shapepy.bool2d.boolean")
def contains_bool2d(subseta: SubSetR2, subsetb: SubSetR2) -> bool:
    """
    Checks if B is inside A

    Parameters
    ----------
    subseta: SubSetR2
        The subset A
    subsetb: SubSetR2
        The subset B

    Return
    ------
    bool
        The result if B is inside A
    """
    subseta = Future.convert(subseta)
    subsetb = Future.convert(subsetb)
    if Is.instance(subseta, EmptyShape) or Is.instance(subsetb, WholeShape):
        return subseta is subsetb
    if Is.instance(subseta, WholeShape) or Is.instance(subsetb, EmptyShape):
        return True
    if Is.instance(subseta, (ConnectedShape, LazyAnd)):
        return all(subsetb in s for s in subseta)
    if Is.instance(subsetb, (DisjointShape, LazyOr)):
        return all(s in subseta for s in subsetb)
    if Is.instance(subseta, LazyNot) and Is.instance(subsetb, LazyNot):
        return contains_bool2d(~subsetb, ~subseta)
    if Is.instance(subseta, SimpleShape):
        if Is.instance(subsetb, (SinglePoint, SingleCurve, SimpleShape)):
            return subsetb in subseta
        if Is.instance(subsetb, ConnectedShape):
            return (~subseta).clean() in (~subsetb).clean()
        if not Config.auto_clean:
            raise ValueError(
                f"Needs clean to evaluate: {type(subseta)}, {type(subsetb)}"
            )
        return subsetb.clean() in subseta.clean()
    if Is.instance(subseta, (LazyOr, DisjointShape)):
        return any(subsetb in s for s in subseta)  # Needs improvement
    raise NotImplementedError(
        f"Invalid typos: {type(subseta)}, {type(subsetb)}"
    )


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


def divide_connecteds(
    simples: Tuple[SimpleShape],
) -> Tuple[Union[SimpleShape, ConnectedShape]]:
    """
    Divides the simples in groups of connected shapes

    The idea is get the simple shape with maximum abs area,
    this is the biggest shape of all we start from it.

    We them separate all shapes in inside and outside
    """
    if len(simples) == 0:
        return tuple()
    externals = []
    connected = []
    simples = list(simples)
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


def shape_from_jordans(jordans: Tuple[JordanCurve]) -> SubSetR2:
    """Returns the correspondent shape

    This function don't do entry validation
    as verify if one shape is inside other

    Example
    ----------
    >>> shape_from_jordans([])
    EmptyShape
    """
    assert len(jordans) != 0
    simples = tuple(map(SimpleShape, jordans))
    if len(simples) == 1:
        return simples[0]
    connecteds = divide_connecteds(simples)
    if len(connecteds) == 1:
        return connecteds[0]
    return DisjointShape(connecteds)


class GraphComputer:
    """Contains static methods to use Graph to compute boolean operations"""

    @staticmethod
    @debug("shapepy.bool2d.boole")
    def clean(subset: SubSetR2) -> Iterator[JordanCurve]:
        """Cleans the subset using the graphs"""
        logger = get_logger("shapepy.bool2d.boole")
        pairs = tuple(GraphComputer.extract(subset))
        djordans = {id(j): j for b, j in pairs if b}
        ijordans = {id(j): j for b, j in pairs if not b}
        # for key in djordans.keys() & ijordans.keys():
        #     djordans.pop(key)
        #     ijordans.pop(key)
        piecewises = [jordan.piecewise for jordan in djordans.values()]
        piecewises += [(~jordan).piecewise for jordan in ijordans.values()]
        logger.debug(f"Quantity of piecewises: {len(piecewises)}")
        with graph_manager():
            graphs = tuple(map(curve2graph, piecewises))
            logger.debug("Computing intersections")
            graph = intersect_graphs(graphs)
            logger.debug("Finished graph intersections")
            for edge in tuple(graph.edges):
                density = subset.density(edge.pointm)
                if not 0 < float(density) < 1:
                    graph.remove_edge(edge)
            logger.debug("After removing the edges" + str(graph))
            graphs = tuple(GraphComputer.extract_disjoint_graphs(graph))
            all_edges = map(GraphComputer.unique_closed_path, graphs)
            all_edges = tuple(e for e in all_edges if e is not None)
            logger.debug("all edges = ")
            for i, edges in enumerate(all_edges):
                logger.debug(f"    {i}: {edges}")
            jordans = tuple(map(GraphComputer.edges2jordan, all_edges))
        return jordans

    @staticmethod
    def extract(subset: SubSetR2) -> Iterator[Tuple[bool, JordanCurve]]:
        """Extracts the simple shapes from the subset"""
        if isinstance(subset, SimpleShape):
            yield (True, subset.jordan)
        elif Is.instance(subset, (ConnectedShape, DisjointShape)):
            for subshape in subset.subshapes:
                yield from GraphComputer.extract(subshape)
        elif Is.instance(subset, LazyNot):
            for var, jordan in GraphComputer.extract(~subset):
                yield (not var, jordan)
        elif Is.instance(subset, (LazyOr, LazyAnd)):
            for subsubset in subset:
                yield from GraphComputer.extract(subsubset)

    @staticmethod
    def extract_disjoint_graphs(graph: Graph) -> Iterable[Graph]:
        """Separates the given graph into disjoint graphs"""
        edges = list(graph.edges)
        while len(edges) > 0:
            edge = edges.pop(0)
            current_edges = {edge}
            search_edges = {edge}
            while len(search_edges) > 0:
                end_nodes = {edge.nodeb for edge in search_edges}
                search_edges = {
                    edge for edge in edges if edge.nodea in end_nodes
                }
                for edge in search_edges:
                    edges.remove(edge)
                current_edges |= search_edges
            yield Graph(current_edges)

    @staticmethod
    def possible_paths(
        edges: Iterable[Edge], start_node: Node
    ) -> Iterator[Tuple[Edge, ...]]:
        """Returns all the possible paths that begins at start_node"""
        edges = tuple(edges)
        indices = set(i for i, e in enumerate(edges) if e.nodea == start_node)
        other_edges = tuple(e for i, e in enumerate(edges) if i not in indices)
        for edge in (edges[i] for i in indices):
            subpaths = tuple(
                GraphComputer.possible_paths(other_edges, edge.nodeb)
            )
            if len(subpaths) == 0:
                yield (edge,)
            else:
                for subpath in subpaths:
                    yield (edge,) + subpath

    @staticmethod
    def closed_paths(
        edges: Tuple[Edge, ...], start_node: Node
    ) -> Iterator[CyclicContainer[Edge]]:
        """Gets all the closed paths that starts at given node"""
        logger = get_logger("shapepy.bool2d.boolean")
        paths = tuple(GraphComputer.possible_paths(edges, start_node))
        logger.debug(
            f"all paths starting with {repr(start_node)}: {len(paths)} paths"
        )
        # for i, path in enumerate(paths):
        #     logger.debug(f"    {i}: {path}")
        closeds = []
        for path in paths:
            if path[0].nodea == path[-1].nodeb:
                closeds.append(CyclicContainer(path))
        return closeds

    @staticmethod
    def all_closed_paths(graph: Graph) -> Iterator[CyclicContainer[Edge]]:
        """Reads the graphs and extracts the unique paths"""
        if not Is.instance(graph, Graph):
            raise TypeError

        # logger.debug("Extracting unique paths from the graph")
        # logger.debug(str(graph))

        edges = tuple(graph.edges)

        def sorter(x):
            return x[1]

        logger = get_logger("shapepy.bool2d.boole")
        counter = Counter(e.nodea for e in edges)
        logger.debug(f"counter = {dict(counter)}")
        snodes = tuple(k for k, _ in sorted(counter.items(), key=sorter))
        logger.debug(f"snodes = {snodes}")
        all_paths = []
        for start_node in snodes:
            all_paths += list(
                GraphComputer.closed_paths(graph.edges, start_node)
            )
        return all_paths

    @staticmethod
    @debug("shapepy.bool2d.boole")
    def unique_closed_path(graph: Graph) -> Union[None, CyclicContainer[Edge]]:
        """Reads the graphs and extracts the unique paths"""
        all_paths = list(GraphComputer.all_closed_paths(graph))
        for path in all_paths:
            return path
        return None

    @staticmethod
    @debug("shapepy.bool2d.boole")
    def edges2jordan(edges: CyclicContainer[Edge]) -> JordanCurve:
        """Converts the given connected edges into a Jordan Curve"""
        logger = get_logger("shapepy.bool2d.boole")
        logger.debug(f"len(edges) = {len(edges)}")
        edges = tuple(edges)
        if len(edges) == 1:
            path = tuple(tuple(edges)[0].singles)[0]
            logger.debug(f"path = {path}")
            curve = path.curve.section([path.knota, path.knotb])
            logger.debug(f"curve = {curve}")
            if isinstance(curve, Segment):
                usegments = [USegment(curve)]
            else:
                usegments = list(map(USegment, curve))
            logger.debug(f"usegments = {usegments}")
            return JordanCurve(usegments)
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
