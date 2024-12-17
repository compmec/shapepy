"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""

from __future__ import annotations

from typing import Iterable, Tuple, Union

from ..boolean import BoolOr
from ..core import Empty, IBoolean2D, ICurve, IShape, Parameter, Whole
from ..curve.abc import IJordanCurve
from ..curve.concatenate import concatenate, transform_to_jordan
from ..curve.intersect import curve_and_curve
from ..point import Point2D
from ..utils import sorter
from .simple import ConnectedShape, DisjointShape, SimpleShape


def close_shape(shape: IShape) -> IShape:
    if not isinstance(shape, IShape):
        raise TypeError
    if isinstance(shape, SimpleShape):
        return SimpleShape(shape.jordan, True)
    return shape.__class__(map(close_shape, shape))


def flatten2simples(
    shapes: Union[IShape, Iterable[IShape]]
) -> Iterable[SimpleShape]:
    if isinstance(shapes, SimpleShape):
        yield shapes
        return
    for shape in shapes:
        yield from flatten2simples(shape)


def remove_wind_edges(
    graph: Graph, shapes: Iterable[IShape], wind: int
) -> Graph:
    allknots = graph.allknots
    jordans = graph.jordans
    for i, knotsi in enumerate(allknots):
        curve = jordans[i].param_curve
        for knota, knotb in zip(knotsi, knotsi[1:]):
            midpoint = curve.eval((knota + knotb) / 2, 0)
            winds = (shape.winding(midpoint) for shape in shapes)
            if not any(sub == wind for sub in winds):
                continue
            inpta = graph.find_node(i, knota)
            inptb = graph.find_node(i, knotb)
            graph.remove_edge(i, inpta, inptb)
    return graph


def remove_inverse_edges(graph: Graph) -> Graph:
    edges = tuple(graph.edges)
    nedgs = len(edges)
    for i, edgi in enumerate(edges):
        for j in range(i + 1, nedgs):
            edgj = edges[j]
            if edgi[1] != edgj[2] or edgi[2] != edgj[1]:
                continue
            graph.remove_edge(edgi[0], edgi[1], edgi[2])
            graph.remove_edge(edgj[0], edgj[1], edgj[2])
    return graph


def unite_shapes(*shapes: IShape) -> IBoolean2D:
    shapes = tuple(shapes)
    orisimples = tuple(flatten2simples(shapes))  # Original simple shapes
    jordans = tuple(simple.jordan for simple in orisimples)
    graph = Graph(jordans)
    graph = remove_inverse_edges(graph)
    graph = remove_wind_edges(graph, shapes, 1)
    new_simples = []
    for jordan in graph.extract_direct_jordans():
        for simple in orisimples:
            if id(simple.jordan) == id(jordan):
                new_simples.append(simple)
    for jordan in graph.extract_mixed_jordans():
        curve = jordan.param_curve
        midcontained = [False] * (len(curve.knots) - 1)
        for i, (knota, knotb) in enumerate(zip(curve.knots, curve.knots[1:])):
            midpoint = curve.eval((knota + knotb) / 2, 0)
            midcontained[i] = any(midpoint in shape for shape in shapes)
        simple = SimpleShape(jordan, all(midcontained))
        new_simples.append(simple)
    if not len(new_simples):
        return Whole()
    return identify_shape(new_simples)


def intersect_shapes(*shapes: IShape) -> IBoolean2D:
    shapes = tuple(shapes)
    orisimples = tuple(flatten2simples(shapes))  # Original simple shapes
    jordans = tuple(simple.jordan for simple in orisimples)
    graph = Graph(jordans)
    graph = remove_inverse_edges(graph)
    graph = remove_wind_edges(graph, shapes, 0)
    new_simples = []
    for jordan in graph.extract_direct_jordans():
        for simple in orisimples:
            if id(simple.jordan) == id(jordan):
                new_simples.append(simple)
    for jordan in graph.extract_mixed_jordans():
        curve = jordan.param_curve
        midcontained = [False] * (len(curve.knots) - 1)
        for i, (knota, knotb) in enumerate(zip(curve.knots, curve.knots[1:])):
            midpoint = curve.eval((knota + knotb) / 2, 0)
            midcontained[i] = all(midpoint in shape for shape in shapes)
        simple = SimpleShape(jordan, all(midcontained))
        new_simples.append(simple)
    if not len(new_simples):
        return Empty()
    return identify_shape(new_simples)


def identify_shape(
    simples: Iterable[SimpleShape],
) -> Union[SimpleShape, ConnectedShape, DisjointShape]:
    """
    Identify the final shape (Simple, Connected, Disjoint) from the
    given simple shapes
    """
    simples = tuple(simples)
    for simple in simples:
        if not isinstance(simple, SimpleShape):
            raise TypeError(f"Received {type(simple)}")
    areas = tuple(simple.area for simple in simples)
    simples = [simples[i] for i in sorter(areas)]
    disshapes = []
    while simples:
        connsimples = [simples.pop(len(simples) - 1)]
        index = 0
        while index < len(simples):
            simple = simples[index]
            for simplj in connsimples:
                if simple.jordan not in simplj:
                    break
                if simplj.jordan not in simple:
                    break
            else:
                connsimples.append(simples.pop(index))
                index -= 1
            index += 1
        if len(connsimples) == 1:
            shape = connsimples[0]
        else:
            shape = ConnectedShape(connsimples)
        disshapes.append(shape)
    if len(disshapes) == 1:
        return disshapes[0]
    return DisjointShape(disshapes)


class Node(tuple):
    def __new__(
        cls, jordan_index: int, parameter: Parameter, point_index: int
    ):
        self = super(Node, cls).__new__(
            cls, (jordan_index, parameter, point_index)
        )
        self.jordan_index = jordan_index
        self.parameter = parameter
        self.point_index = point_index
        return self


class Edge(tuple):
    def __new__(cls, jordan_index: int, first_index: int, last_index: int):
        self = super(Edge, cls).__new__(
            cls, (jordan_index, first_index, last_index)
        )
        self.jordan_index = jordan_index
        self.first_index = first_index
        self.last_index = last_index
        return self


class Graph:
    def __init__(self, jordans: Iterable[IJordanCurve]):
        jordans = tuple(jordans)
        for jordan in jordans:
            if not isinstance(jordan, IJordanCurve):
                raise TypeError
        self.jordans = jordans
        self.points = []
        self.allknots = []
        self.nodes = []
        self.edges = []
        self.compute_standard_nodes()
        self.compute_intersect_nodes()
        self.compute_allknots()
        self.compute_edges()

    def add_node(self, ijordan: int, param: Parameter):
        jordan = self.jordans[ijordan]
        newpt = jordan.param_curve.eval(param, 0)
        for ptindex, curpt in enumerate(self.points):
            if curpt == newpt:
                break
        else:
            ptindex = len(self.points)
            self.points.append(newpt)
        node = Node(ijordan, param, ptindex)
        self.nodes.append(node)

    def find_node(self, ijordan: int, param: Parameter):
        for node in self.nodes:
            if node[0] == ijordan and node[1] == param:
                return node[2]
        raise ValueError(f"Could not find node {ijordan}, {param}")

    def find_param(self, ijordan: int, indexpt: int):
        for node in self.nodes:
            if node.jordan_index == ijordan and node.point_index == indexpt:
                return node.parameter
        raise ValueError(f"Could not find parameter {ijordan}, {indexpt}")

    def add_edge(self, ijordan: int, inodea: int, inodeb: int):
        edge = Edge(ijordan, inodea, inodeb)
        self.edges.append(edge)
        self.edges = sorted(self.edges)

    def remove_edge(self, ijordan: int, inodea: int, inodeb: int):
        for i, edge in enumerate(self.edges):
            if edge[0] == ijordan and edge[1] == inodea and edge[2] == inodeb:
                self.edges.pop(i)
                return
        raise ValueError(
            f"Could not remove edge ({ijordan}, {inodea}, {inodeb})"
        )

    def compute_standard_nodes(self):
        for i, jordan in enumerate(self.jordans):
            curve = jordan.param_curve
            for knot in curve.knots:
                self.add_node(i, knot)

    def compute_intersect_nodes(self):
        njords = len(self.jordans)
        for i, jordani in enumerate(self.jordans):
            for j in range(i + 1, njords):
                jordanj = self.jordans[j]
                inters = two_curve_inter(jordani, jordanj)
                for parami, paramj in inters:
                    self.add_node(i, parami)
                    self.add_node(j, paramj)

    def compute_allknots(self):
        allknots = []
        for indj, _ in enumerate(self.jordans):
            knots = set()
            for jndj, param, _ in self.nodes:
                if jndj != indj:
                    continue
                knots.add(param)
            allknots.append(tuple(sorted(knots)))
        self.allknots = tuple(allknots)

    def compute_edges(self):
        for indj, _ in enumerate(self.jordans):
            knots = self.allknots[indj]
            for knota, knotb in zip(knots, knots[1:]):
                ptinda = self.find_node(indj, knota)
                ptindb = self.find_node(indj, knotb)
                self.add_edge(indj, ptinda, ptindb)

    def extract_direct_jordans(self) -> Iterable[IJordanCurve]:
        """
        Extract the order of the graph by connection

        Returns a tuple of (index jordan, knot parameter, index point)
        """
        available_jordans = tuple(sorted(set(e[0] for e in self.edges)))
        for ijord in available_jordans:
            jordan = self.jordans[ijord]
            if len(self.allknots[ijord]) != len(jordan.param_curve.knots):
                continue
            edges = tuple(e for e in self.edges if e[0] == ijord)
            if len(edges) + 1 != len(self.allknots[ijord]):
                continue
            index = 0
            while index < len(self.edges):
                if self.edges[index].jordan_index == ijord:
                    self.edges.pop(index)
                else:
                    index += 1
            yield jordan

    def extract_mixed_jordans(self) -> Iterable[IJordanCurve]:
        """
        This function gives the jordan curves when there's intersection
        between the jordans, so it's a mix of some jordan curves
        """
        available_jordans = tuple(sorted(set(e[0] for e in self.edges)))
        for ijord in available_jordans:
            filtedges = sorted(e for e in self.edges if e[0] == ijord)
            if not filtedges:
                continue
            new_edges = [filtedges[0]]
            while True:
                if new_edges[-1].last_index == new_edges[0].first_index:
                    break
                for cur_edge in self.edges:
                    if cur_edge.first_index == new_edges[-1].last_index:
                        new_edges.append(cur_edge)
                        break
            segments = []
            for edge in tuple(new_edges):
                curve = self.jordans[edge[0]].param_curve
                parama = self.find_param(edge[0], edge[1])
                paramb = self.find_param(edge[0], edge[2])
                if paramb <= parama:
                    if paramb != curve.knots[0]:
                        raise ValueError("Not expected get here")
                    paramb = curve.knots[-1]
                segment = curve.section(parama, paramb)
                segments.append(segment)
                self.remove_edge(edge[0], edge[1], edge[2])
            curve = concatenate(*segments)
            yield transform_to_jordan(curve)


def two_curve_inter(
    curvea: IJordanCurve, curveb: IJordanCurve
) -> Iterable[Tuple[float, float]]:
    """
    Computes the intersection of two parameted curves P(t) and Q(u)
    returning the pairs (ti, ui) such P(ti) = Q(ui)
    """
    if not isinstance(curvea, IJordanCurve):
        raise TypeError
    if not isinstance(curveb, IJordanCurve):
        raise TypeError
    objs = curve_and_curve(curvea, curveb)
    curvea = curvea.param_curve
    curveb = curveb.param_curve
    if isinstance(objs, Empty):
        return
    if isinstance(objs, BoolOr):
        objs = tuple(objs)
    else:
        objs = (objs,)
    points = []
    for obj in objs:
        if isinstance(obj, Point2D):
            points.append(obj)
        elif isinstance(obj, ICurve):
            points += list(obj.vertices)
        else:
            raise NotImplementedError
    setpts = []
    for point in points:
        for setpt in setpts:
            if point == setpt:
                break
        else:
            setpts.append(point)
    for point in setpts:
        parama = curvea.projection(point)[0]
        paramb = curveb.projection(point)[0]
        yield (parama, paramb)
