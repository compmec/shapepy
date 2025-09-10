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
from ..loggers import get_logger
from ..scalar.reals import Real
from ..tools import Is

GAP = "    "


def get_single_node(curve: IParametrizedCurve, parameter: Real) -> SingleNode:
    """Instantiate a new SingleNode, made by the pair: (curve, parameter)

    If given pair (curve, parameter) was already created, returns the
    created instance.
    """

    if not Is.instance(curve, IParametrizedCurve):
        raise TypeError(f"Invalid curve: {type(curve)}")
    if not Is.real(parameter):
        raise TypeError(f"Invalid type: {type(parameter)}")
    hashval = (id(curve), parameter)
    if hashval in SingleNode.instances:
        return SingleNode.instances[hashval]
    instance = SingleNode(curve, parameter)
    SingleNode.instances[hashval] = instance
    return instance


class SingleNode:

    instances: Dict[Tuple[int, Real], SingleNode] = OrderedDict()

    def __init__(self, curve: IParametrizedCurve, parameter: Real):
        if id(curve) not in Containers.curves:
            Containers.curves[id(curve)] = curve
        self.__curve = curve
        self.__parameter = parameter
        self.__point = curve(parameter)
        self.__label = len(SingleNode.instances)

    def __str__(self):
        index = Containers.index_curve(self.curve)
        return f"C{index} at {self.parameter}"

    def __repr__(self):
        return str(self.curve)

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
        return self.__label

    @property
    def curve(self) -> IParametrizedCurve:
        return self.__curve

    @property
    def parameter(self) -> Real:
        return self.__parameter

    @property
    def point(self) -> Point2D:
        return self.__point


def get_node(singles: Iterable[SingleNode]) -> Node:
    singles: Tuple[SingleNode, ...] = tuple(singles)
    if len(singles) == 0:
        raise ValueError
    point = singles[0].point
    for si in singles[1:]:
        if si.point != point:
            raise ValueError
    if point in Node.instances:
        instance = Node.instances[point]
    else:
        instance = Node(point)
        Node.instances[point] = instance
    for single in singles:
        instance.add(single)
    return instance


class Node:
    """
    Defines a node
    """

    instances: Dict[Point2D, Node] = OrderedDict()

    def __init__(self, point: Point2D):
        self.__singles = set()
        self.__point = point
        self.__label = len(Node.instances)

    @property
    def label(self):
        return self.__label

    @property
    def singles(self) -> Set[SingleNode]:
        return self.__singles

    @property
    def point(self) -> Point2D:
        return self.__point

    def __eq__(self, other):
        return Is.instance(other, Node) and self.point == other.point

    def add(self, single: SingleNode):
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


class GroupNodes(Iterable[Node]):

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

    def __ior__(self, other: Iterable[Node]) -> GroupNodes:
        for onode in other:
            if not Is.instance(onode, Node):
                raise TypeError(str(type(onode)))
            self.add_node(onode)
        return self

    def add_node(self, node: Node) -> Node:
        if not Is.instance(node, Node):
            raise TypeError(str(type(node)))
        self.__nodes.add(node)
        return node

    def add_single(self, single: SingleNode) -> Node:
        if not Is.instance(single, SingleNode):
            raise TypeError(str(type(single)))
        return self.add_node(get_node({single}))


def single_path(
    curve: IParametrizedCurve, knota: Real, knotb: Real
) -> SinglePath:
    if not Is.instance(curve, IParametrizedCurve):
        raise TypeError(f"Invalid curve: {type(curve)}")
    if not Is.real(knota):
        raise TypeError(f"Invalid type: {type(knota)}")
    if not Is.real(knotb):
        raise TypeError(f"Invalid type: {type(knotb)}")
    if not knota < knotb:
        raise ValueError(str((knota, knotb)))
    hashval = (id(curve), knota, knotb)
    if hashval not in SinglePath.instances:
        return SinglePath(curve, knota, knotb)
    return SinglePath.instances[hashval]


class SinglePath:

    instances = OrderedDict()

    def __init__(self, curve: IParametrizedCurve, knota: Real, knotb: Real):
        knotm = (knota + knotb) / 2
        self.__curve = curve
        self.__singlea = get_single_node(curve, knota)
        self.__singlem = get_single_node(curve, knotm)
        self.__singleb = get_single_node(curve, knotb)
        self.__label = len(SinglePath.instances)
        SinglePath.instances[(id(curve), knota, knotb)] = self

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
        return self.__label

    @property
    def curve(self) -> IParametrizedCurve:
        return self.__curve

    @property
    def singlea(self) -> SingleNode:
        return self.__singlea

    @property
    def singlem(self) -> SingleNode:
        return self.__singlem

    @property
    def singleb(self) -> SingleNode:
        return self.__singleb

    @property
    def knota(self) -> Real:
        return self.singlea.parameter

    @property
    def knotm(self) -> Real:
        return self.singlem.parameter

    @property
    def knotb(self) -> Real:
        return self.singleb.parameter

    @property
    def pointa(self) -> Point2D:
        return self.singlea.point

    @property
    def pointm(self) -> Point2D:
        return self.singlem.point

    @property
    def pointb(self) -> Point2D:
        return self.singleb.point

    def __str__(self):
        index = Containers.index_curve(self.curve)
        return (
            f"C{index} ({self.singlea.parameter} -> {self.singleb.parameter})"
        )

    def __and__(self, other: SinglePath) -> GeometricIntersectionCurves:
        if not Is.instance(other, SinglePath):
            raise TypeError(str(type(other)))
        if id(self.curve) == id(other.curve):
            raise ValueError
        return self.curve & other.curve


class Containers:

    curves: Dict[int, IParametrizedCurve] = OrderedDict()

    @staticmethod
    def index_curve(curve: IParametrizedCurve) -> int:
        for i, key in enumerate(Containers.curves):
            if id(curve) == key:
                return i
        raise ValueError("Could not find requested curve")


class Edge:
    """
    The edge that defines
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
        return self.__singles

    @property
    def nodea(self) -> Node:
        return self.__nodea

    @property
    def nodem(self) -> Node:
        return self.__nodem

    @property
    def nodeb(self) -> Node:
        return self.__nodeb

    @property
    def pointa(self) -> Point2D:
        return self.nodea.point

    @property
    def pointm(self) -> Point2D:
        return self.nodem.point

    @property
    def pointb(self) -> Point2D:
        return self.nodeb.point

    def add(self, path: SinglePath):
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
        msgs = [
            f"N{self.nodea.label}->N{self.nodem.label}->N{self.nodeb.label}"
        ]
        for path in self.singles:
            msgs.append(f"{GAP}{path}")
        return "\n".join(msgs)

    def __repr__(self):
        return str(self)


class GroupEdges(Iterable[Edge]):

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
        assert Is.instance(edge, Edge)
        self.__edges.remove(edge)

    def add_edge(self, edge: Edge) -> Edge:
        self.__edges.add(edge)

    def add_path(self, path: SinglePath) -> Edge:
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
        msgs = ["Curves:"]
        for index in sorted(used_curves.keys()):
            curve = used_curves[index]
            msgs.append(f"{GAP}C{index}: knots = {curve.knots}")
            msgs.append(2 * GAP + str(curve))
        msgs += ["Nodes:"]
        msgs += [GAP + s for s in str(nodes).split("\n")]
        msgs.append("Edges:")
        msgs += [GAP + e for e in str(edges).split("\n")]
        return "\n".join(msgs)

    def remove_edge(self, edge: Edge):
        """Removes the edge"""
        self.__edges.remove(edge)

    def add_edge(self, edge: Edge) -> Edge:
        if not Is.instance(edge, Edge):
            raise TypeError
        return self.edges.add_edge(edge)

    def add_path(self, path: SinglePath) -> Edge:
        if not Is.instance(path, SinglePath):
            raise TypeError
        return self.edges.add_path(path)


def intersect_graphs(graphs: Iterable[Graph]) -> Graph:
    """
    Computes the intersection of many graphs
    """
    size = len(graphs)
    if size == 1:
        return graphs[0]
    half = size // 2
    lgraph = intersect_graphs(graphs[:half])
    rgraph = intersect_graphs(graphs[half:])
    return lgraph & rgraph


@contextmanager
def graph_manager():
    """
    A context manager that
    """
    Graph.can_create = True
    try:
        yield
    finally:
        Graph.can_create = False
        SingleNode.instances.clear()
        Node.instances.clear()
        SinglePath.instances.clear()
        Containers.curves.clear()

def curve2graph(curve: IParametrizedCurve) -> Graph:
    """Creates a graph that contains the nodes and edges of the curve"""
    single_path = SinglePath(curve, curve.knots[0], curve.knots[-1])
    return Graph({Edge({single_path})})
