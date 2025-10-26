"""
Defines Node, Edge and Graph, structures used to help computing the
boolean operations between shapes
"""

from __future__ import annotations

from collections import OrderedDict
from contextlib import contextmanager
from typing import Dict, Iterable, Iterator, Set, Tuple

from ..geometry.base import IParametrizedCurve
from ..geometry.intersection import GeometricIntersectionCurves
from ..geometry.point import Point2D
from ..loggers import debug, get_logger
from ..scalar.reals import Real
from ..tools import Is

GAP = "    "


def get_single_node(curve: IParametrizedCurve, parameter: Real) -> SingleNode:
    """Instantiate a new SingleNode, made by the pair: (curve, parameter)

    If given pair (curve, parameter) was already created,
    returns the previously created instance.
    """
    if not Is.instance(curve, IParametrizedCurve):
        raise TypeError(f"Invalid curve: {type(curve)}")
    if not Is.real(parameter):
        raise TypeError(f"Invalid type: {type(parameter)}")
    hashval = (id(curve), parameter)
    if hashval in Containers.single_nodes:
        return Containers.single_nodes[hashval]
    instance = SingleNode(curve, parameter)
    Containers.single_nodes[hashval] = instance
    return instance


class SingleNode:
    """Single Node stores a pair of (curve, parameter)

    A Node is equivalent to a point (x, y) = curve(parameter),
    but it's required to track back the curve and the parameter used.

    We compare if one SingleNode is equal to another
    by the curve ID and parameter.
    """

    def __init__(self, curve: IParametrizedCurve, parameter: Real):
        if id(curve) not in Containers.curves:
            Containers.curves[id(curve)] = curve
        self.__curve = curve
        self.__parameter = parameter
        self.__point = curve(parameter)
        self.__label = len(Containers.single_nodes)

    def __str__(self):
        index = Containers.index_curve(self.curve)
        return f"C{index} at {self.parameter}"

    def __repr__(self):
        return str(self.__point)

    def __eq__(self, other):
        return (
            Is.instance(other, SingleNode)
            and id(self.curve) == id(other.curve)
            and self.parameter == other.parameter
        )

    def __hash__(self):
        return hash((id(self.curve), self.parameter))

    @property
    def label(self):
        """Gives the label the SingleNode. Only for Debug purpose"""
        return self.__label

    @property
    def curve(self) -> IParametrizedCurve:
        """Gives the curve used to compute the point"""
        return self.__curve

    @property
    def parameter(self) -> Real:
        """Gives the parameter used to compute the point"""
        return self.__parameter

    @property
    def point(self) -> Point2D:
        """Gives the evaluation of curve(parameter)"""
        return self.__point


def get_node(singles: Iterable[SingleNode]) -> Node:
    """Instantiate a new Node, made by a list of SingleNode

    It's required that all the points are equal.

    Returns the previously created instance if it was already created"""
    singles: Tuple[SingleNode, ...] = tuple(singles)
    if len(singles) == 0:
        raise ValueError
    point = singles[0].point
    for si in singles[1:]:
        if si.point != point:
            raise ValueError
    if point in Containers.nodes:
        instance = Containers.nodes[point]
    else:
        instance = Node(point)
        Containers.nodes[point] = instance
    for single in singles:
        instance.add(single)
    return instance


class Node:
    """
    Defines a node, which is equivalent to a geometric point (x, y)

    This Node also contains all the pairs (curve, parameter) such,
    when evaluated ``curve(parameter)`` gives the point of the node.

    It's used because it probably exist many curves that intersect
    at a single point, and it's required to track back all the curves
    that pass through that Node.
    """

    def __init__(self, point: Point2D):
        self.__singles = set()
        self.__point = point
        self.__label = len(Node.instances)

    @property
    def label(self):
        """Gives the label the Node. Only for Debug purpose"""
        return self.__label

    @property
    def singles(self) -> Set[SingleNode]:
        """Gives the list of pairs (curve, parameter) that defines the Node"""
        return self.__singles

    @property
    def point(self) -> Point2D:
        """Gives the point of the Node"""
        return self.__point

    def __eq__(self, other):
        return Is.instance(other, Node) and self.point == other.point

    def add(self, single: SingleNode):
        """Inserts a new SingleNode into the list inside the Node"""
        if not Is.instance(single, SingleNode):
            raise TypeError(f"Invalid type: {type(single)}")
        if single.point != self.point:
            raise ValueError
        self.singles.add(single)

    def __hash__(self):
        return hash(self.point)

    def __str__(self):
        msgs = [f"N{self.label}: {self.point}:"]
        for single in self.singles:
            msgs += [f"{GAP}{s}" for s in str(single).split("\n")]
        return "\n".join(msgs)

    def __repr__(self):
        return f"N{self.label}:{self.point}"


class GroupNodes(Iterable[Node]):
    """Class that stores a group of Node."""

    def __init__(self, nodes: Iterable[Node] = None):
        self.__nodes: Set[Node] = set()
        if nodes is not None:
            self |= nodes

    def __iter__(self) -> Iterator[Node]:
        yield from self.__nodes

    def __len__(self) -> int:
        return len(self.__nodes)

    def __str__(self):
        dictnodes = {n.label: n for n in self}
        keys = sorted(dictnodes.keys())
        return "\n".join(str(dictnodes[key]) for key in keys)

    def __repr__(self):
        return "(" + ", ".join(map(repr, self)) + ")"

    def __ior__(self, other: Iterable[Node]) -> GroupNodes:
        for onode in other:
            if not Is.instance(onode, Node):
                raise TypeError(str(type(onode)))
            self.add_node(onode)
        return self

    def add_node(self, node: Node) -> Node:
        """Add a Node into the group of nodes.

        If it's already included, only skips the insertion"""
        if not Is.instance(node, Node):
            raise TypeError(str(type(node)))
        self.__nodes.add(node)
        return node

    def add_single(self, single: SingleNode) -> Node:
        """Add a single Node into the group of nodes.

        If it's already included, only skips the insertion"""
        if not Is.instance(single, SingleNode):
            raise TypeError(str(type(single)))
        return self.add_node(get_node({single}))


def single_path(
    curve: IParametrizedCurve, knota: Real, knotb: Real
) -> SinglePath:
    """Instantiate a new SinglePath, with the given triplet.

    It checks if the SinglePath with given triplet (curve, knota, knotb)
    was already created. If that's the case, returns the previous instance.
    Otherwise, creates a new instance."""

    if not Is.instance(curve, IParametrizedCurve):
        raise TypeError(f"Invalid curve: {type(curve)}")
    if not Is.real(knota):
        raise TypeError(f"Invalid type: {type(knota)}")
    if not Is.real(knotb):
        raise TypeError(f"Invalid type: {type(knotb)}")
    if not knota < knotb:
        raise ValueError(str((knota, knotb)))
    hashval = (id(curve), knota, knotb)
    if hashval not in Containers.single_paths:
        return SinglePath(curve, knota, knotb)
    return Containers.single_paths[hashval]


class SinglePath:
    """Stores a single path from the curve.

    It's equivalent to the triplet (curve, knota, knotb)

    There are infinite ways to connect two points pointa -> pointb.
    To describe which way we connect, we use the given curve.
    It's required that ``curve(knota) = pointa`` and ``curve(knotb) = pointb``
    """

    def __init__(self, curve: IParametrizedCurve, knota: Real, knotb: Real):
        knotm = (knota + knotb) / 2
        self.__curve = curve
        self.__singlea = get_single_node(curve, knota)
        self.__singlem = get_single_node(curve, knotm)
        self.__singleb = get_single_node(curve, knotb)
        self.__label = len(Containers.single_paths)
        Containers.single_paths[(id(curve), knota, knotb)] = self

    def __eq__(self, other):
        return (
            Is.instance(other, SinglePath)
            and hash(self) == hash(other)
            and id(self.curve) == id(other.curve)
            and self.knota == other.knota
            and self.knotb == other.knotb
        )

    def __hash__(self):
        return hash((id(self.curve), self.knota, self.knotb))

    @property
    def label(self):
        """Gives the label the SinglePath. Only for Debug purpose"""
        return self.__label

    @property
    def curve(self) -> IParametrizedCurve:
        """Gives the curve that connects the pointa to pointb"""
        return self.__curve

    @property
    def singlea(self) -> SingleNode:
        """Gives the initial SingleNode, the pair (curve, knota)"""
        return self.__singlea

    @property
    def singlem(self) -> SingleNode:
        """Gives the SingleNode at the middle of the segment"""
        return self.__singlem

    @property
    def singleb(self) -> SingleNode:
        """Gives the final SingleNode, the pair (curve, knotb)"""
        return self.__singleb

    @property
    def knota(self) -> Real:
        """Gives the parameter such when evaluated by curve, gives pointa"""
        return self.singlea.parameter

    @property
    def knotm(self) -> Real:
        """Gives the parameter at the middle of the two parameters"""
        return self.singlem.parameter

    @property
    def knotb(self) -> Real:
        """Gives the parameter such when evaluated by curve, gives pointb"""
        return self.singleb.parameter

    @property
    def pointa(self) -> Point2D:
        """Gives the start point of the path"""
        return self.singlea.point

    @property
    def pointm(self) -> Point2D:
        """Gives the middle point of the path"""
        return self.singlem.point

    @property
    def pointb(self) -> Point2D:
        """Gives the end point of the path"""
        return self.singleb.point

    def __str__(self):
        index = Containers.index_curve(self.curve)
        return (
            f"C{index} ({self.singlea.parameter} -> {self.singleb.parameter})"
        )

    def __repr__(self):
        index = Containers.index_curve(self.curve)
        return f"C{index}({self.singlea.parameter}->{self.singleb.parameter})"

    def __and__(self, other: SinglePath) -> GeometricIntersectionCurves:
        if not Is.instance(other, SinglePath):
            raise TypeError(str(type(other)))
        if id(self.curve) == id(other.curve):
            raise ValueError
        return self.curve & other.curve


class Containers:

    single_nodes: Dict[Tuple[int, Real], SingleNode] = OrderedDict()
    nodes: Dict[Point2D, Node] = OrderedDict()
    single_paths: Dict[Tuple[int, Real], SinglePath] = OrderedDict()
    curves: Dict[int, IParametrizedCurve] = OrderedDict()

    @staticmethod
    def index_curve(curve: IParametrizedCurve) -> int:
        for i, key in enumerate(Containers.curves):
            if id(curve) == key:
                return i
        raise ValueError("Could not find requested curve")


class Edge:
    """
    The edge defines a continuous path between two points: pointa -> pointb

    It's equivalent to SinglePath, but it's possible to exist two different
    curves (different ids) that describes the same paths.

    This class tracks all the triplets (curve, knota, knotb) that maps
    to the same path.
    """

    def __init__(self, paths: Iterable[SinglePath]):
        paths = set(paths)
        if len(paths) == 0:
            raise ValueError
        self.__singles: Set[SinglePath] = set(paths)
        if len(self.__singles) != 1:
            raise ValueError
        self.__nodea = get_node(
            {get_single_node(p.curve, p.knota) for p in paths}
        )
        self.__nodem = get_node(
            {get_single_node(p.curve, p.knotm) for p in paths}
        )
        self.__nodeb = get_node(
            {get_single_node(p.curve, p.knotb) for p in paths}
        )

    @property
    def singles(self) -> Set[SinglePath]:
        """Gives the single paths"""
        return self.__singles

    @property
    def nodea(self) -> Node:
        """Gives the start node, related to pointa"""
        return self.__nodea

    @property
    def nodem(self) -> Node:
        """Gives the middle node, related to the middle of the path"""
        return self.__nodem

    @property
    def nodeb(self) -> Node:
        """Gives the final node, related to pointb"""
        return self.__nodeb

    @property
    def pointa(self) -> Point2D:
        """Gives the start point"""
        return self.nodea.point

    @property
    def pointm(self) -> Point2D:
        """Gives the middle point"""
        return self.nodem.point

    @property
    def pointb(self) -> Point2D:
        """Gives the final point"""
        return self.nodeb.point

    def add(self, path: SinglePath):
        """Adds a SinglePath to the Edge"""
        self.__singles.add(path)

    def __contains__(self, path: SinglePath) -> bool:
        if not Is.instance(path, SinglePath):
            raise TypeError
        return path in self.singles

    def __hash__(self):
        return hash((hash(self.nodea), hash(self.nodem), hash(self.nodeb)))

    def __and__(self, other: Edge) -> Graph:
        assert Is.instance(other, Edge)
        lazys = tuple(self.singles)[0]
        lazyo = tuple(other.singles)[0]
        inters = lazys & lazyo
        graph = Graph()
        if not inters:
            graph.edges |= {self, other}
            return graph
        # logger = get_logger("shapepy.bool2d.console")
        # logger.info(str(inters))
        for curve in inters.curves:
            knots = sorted(inters.all_knots[id(curve)])
            for knota, knotb in zip(knots, knots[1:]):
                path = single_path(curve, knota, knotb)
                graph.add_path(path)
        return graph

    def __ior__(self, other: Edge) -> Edge:
        assert Is.instance(other, Edge)
        assert self.nodea.point == other.nodea.point
        assert self.nodeb.point == other.nodeb.point
        self.__nodea |= other.nodea
        self.__nodeb |= other.nodeb
        self.__singles = tuple(set(other.singles))
        return self

    def __str__(self):
        msgs = [repr(self)]
        for path in self.singles:
            msgs.append(f"{GAP}{path}")
        return "\n".join(msgs)

    def __repr__(self):
        return f"N{self.nodea.label}->N{self.nodeb.label}"


class GroupEdges(Iterable[Edge]):
    """GroupEdges stores some Edges.

    It is used to easily insert an edge into a graph for example,
    cause it makes the computations underneath"""

    def __init__(self, edges: Iterable[Edge] = None):
        self.__edges: Set[Edge] = set()
        if edges is not None:
            self |= edges

    def __iter__(self) -> Iterator[Edge]:
        yield from self.__edges

    def __len__(self) -> int:
        return len(self.__edges)

    def __str__(self):
        return "\n".join(f"E{i}: {edge}" for i, edge in enumerate(self))

    def __repr__(self):
        return str(self)

    def __ior__(self, other: Iterable[Edge]):
        for oedge in other:
            assert Is.instance(oedge, Edge)
            for sedge in self:
                if sedge == oedge:
                    sedge |= other
                    break
            else:
                self.__edges.add(oedge)
        return self

    def remove(self, edge: Edge) -> bool:
        """Removes an edge from the group"""
        assert Is.instance(edge, Edge)
        self.__edges.remove(edge)

    def add_edge(self, edge: Edge) -> Edge:
        """Inserts an edge into the group"""
        self.__edges.add(edge)

    def add_path(self, path: SinglePath) -> Edge:
        """Inserts a single path into the group"""
        for edge in self:
            if edge.pointa == path.pointa and edge.pointb == path.pointb:
                edge.add(path)
                return edge
        return self.add_edge(Edge({path}))


class Graph:
    """Defines a Graph, a structural data used when computing
    the boolean operations between shapes"""

    can_create = False

    def __init__(
        self,
        edges: GroupEdges = None,
    ):
        if not Graph.can_create:
            raise ValueError("Cannot create a graph. Missing context")
        self.edges = GroupEdges() if edges is None else edges

    @property
    def nodes(self) -> GroupNodes:
        """
        The nodes that define the graph
        """
        nodes = GroupNodes()
        nodes |= {edge.nodea for edge in self.edges}
        nodes |= {edge.nodem for edge in self.edges}
        nodes |= {edge.nodeb for edge in self.edges}
        return nodes

    @property
    def edges(self) -> GroupEdges:
        """
        The edges that defines the graph
        """
        return self.__edges

    @edges.setter
    def edges(self, edges: GroupEdges):
        if not Is.instance(edges, GroupEdges):
            edges = GroupEdges(edges)
        self.__edges = edges

    def __and__(self, other: Graph) -> Graph:
        assert Is.instance(other, Graph)
        result = Graph()
        for edgea in self.edges:
            for edgeb in other.edges:
                result |= edgea & edgeb
        return result

    def __ior__(self, other: Graph) -> Graph:
        if not Is.instance(other, Graph):
            raise TypeError(f"Wrong type: {type(other)}")
        for edge in other.edges:
            for path in edge.singles:
                self.add_path(path)
        return self

    def __str__(self):
        nodes = self.nodes
        edges = self.edges
        used_curves = {}
        for node in nodes:
            for single in node.singles:
                index = Containers.index_curve(single.curve)
                used_curves[index] = single.curve
        msgs = ["\n" + "-" * 90, repr(self), "Curves:"]
        for index in sorted(used_curves.keys()):
            curve = used_curves[index]
            msgs.append(f"{GAP}C{index}: knots = {curve.knots}")
            msgs.append(2 * GAP + str(curve))
        msgs += ["Nodes:"]
        msgs += [GAP + s for s in str(nodes).split("\n")]
        msgs.append("Edges:")
        msgs += [GAP + e for e in str(edges).split("\n")]
        msgs.append("-" * 90)
        return "\n".join(msgs)

    def remove_edge(self, edge: Edge):
        """Removes the edge"""
        self.__edges.remove(edge)

    def add_edge(self, edge: Edge) -> Edge:
        """Adds an edge into the graph"""
        if not Is.instance(edge, Edge):
            raise TypeError
        return self.edges.add_edge(edge)

    def add_path(self, path: SinglePath) -> Edge:
        """Adds a single path into the graph, creating an edge"""
        if not Is.instance(path, SinglePath):
            raise TypeError
        return self.edges.add_path(path)


@debug("shapepy.bool2d.graph")
def intersect_graphs(graphs: Iterable[Graph]) -> Graph:
    """
    Computes the intersection of many graphs
    """
    logger = get_logger("shapepy.bool2d.graph")
    size = len(graphs)
    logger.debug(f"size = {size}")
    if size == 0:
        raise ValueError("Cannot intersect zero graphs")
    if size == 1:
        return graphs[0]
    half = size // 2
    lgraph = intersect_graphs(graphs[:half])
    rgraph = intersect_graphs(graphs[half:])
    return lgraph & rgraph


@contextmanager
def graph_manager():
    """
    A context manager that allows creating Graph instances
    and cleans up the enviroment when finished
    """
    Graph.can_create = True
    try:
        yield
    finally:
        Graph.can_create = False
        Containers.single_nodes.clear()
        Containers.nodes.clear()
        Containers.single_paths.clear()
        Containers.curves.clear()


def curve2graph(curve: IParametrizedCurve) -> Graph:
    """Creates a graph that contains the nodes and edges of the curve"""
    single_path = SinglePath(curve, curve.knots[0], curve.knots[-1])
    return Graph({Edge({single_path})})
