"""
This file contains the functions that computes the final shape
made by union/intersection of some shapes.

The only called functions used are 'unite_shapes' and 'intersect_shapes'.
The others serves only as auxiliar function for both functions.

Basically the main strategy is to collect the boundary of all the shapes,
meaning, getting all the jordan curves and then creating a graph.
A graph contains the nodes as:
* The vertices of a jordan curve, or point evaluation of its knots
* Or also the intersection between any two jordan curves
After all nodes are collected, then edges are created to connect the nodes.
An edge is a segment of the jordan curve, that connects two nodes.

Once the graph is created, destroy some edges by verifying the positioning
of the middle point of this segment.
* For union, if the middle point is contained by any shape, edge is destroyed
* For intersection, edge is destroyed if middle point is not inside all shapes

After that, we only need find the final paths,
walking through the existing edges of the graph
"""

from __future__ import annotations

from typing import Iterable, Tuple, Union

from ..boolean import BoolOr
from ..core import Empty, IBoolean2D, Parameter, Scalar
from ..curve.abc import ICurve, IJordanCurve
from ..curve.concatenate import concatenate
from ..curve.intersect import curve_and_curve
from ..curve.transform import transform_to_jordan
from ..point import Point2D


class JordanContainer:
    """
    A class to store jordan curves that defines
    Simple, Connected or Disjoint shapes
    """

    def __init__(self, alljords: Iterable[Iterable[IJordanCurve]]):
        alljords = tuple(map(tuple, alljords))
        for jords in alljords:
            for jord in jords:
                if not isinstance(jord, IJordanCurve):
                    raise TypeError
        self.alljords = alljords

    def winding(self, point: Point2D) -> Scalar:
        """
        Computes the winding number relative to that shape
        """
        if not isinstance(point, Point2D):
            raise TypeError
        for jords in self.alljords:
            for jord in jords:
                wind = jord.winding(point)
                if wind == 0:
                    break
                if 0 < wind < 1:
                    return wind
            else:
                return 1
        return 0

    def flatten(self) -> Iterable[IJordanCurve]:
        """
        Gives the jordans curves
        """
        for jords in self.alljords:
            yield from jords


def remove_wind_edges(
    graph: Graph, shapes: Iterable[JordanContainer], wind: int
) -> Graph:
    """
    This function gets the graph and remove the edges such the winding value
    of the midpoint is equal to given the wind value

    Parameters
    ----------
    graph: Graph
        The graph with the nodes of the edges of the intersection of jordans
    shapes: Iterable[JordanContainer]
        The shapes that originally have generated the graph
    wind: int
        The winding value to be excluded, can be either 0 or 1
    return: Graph
        The same graph with removed wind, changes the received instance
    """
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
            graph.remove_edge((i, inpta, inptb))
    return graph


def remove_inverse_edges(graph: Graph) -> Graph:
    """
    Remove the inverse edges of a graph.
    For example, if there's an edge that connects the node (A -> B)
    and there's another edge that connects (B -> A), then remove both

    This function changes the actual graph, doesn't create a new instance
    """
    edges = tuple(graph.edges)
    nedgs = len(edges)
    for i, edgi in enumerate(edges):
        for j in range(i + 1, nedgs):
            edgj = edges[j]
            if edgi[1] != edgj[2] or edgi[2] != edgj[1]:
                continue
            graph.remove_edge(edgi)
            graph.remove_edge(edgj)
    return graph


def unite_containers(containers: JordanContainer) -> Iterable[IJordanCurve]:
    """
    Computes the union of the shapes

    Parameters
    ----------
    shapes: Iterable[JordanContainer]
        The shapes to be united
    return: IBoolean2D
        The result, can be Whole, Simple, Connected, Disjoint, BoolOr, etc
    """
    containers = tuple(containers)
    for container in containers:
        if not isinstance(container, JordanContainer):
            raise TypeError(f"Not a JordanContainer, but {type(container)}")
    alljordans = []
    for container in containers:
        alljordans += list(container.flatten())
    graph = Graph(alljordans)
    graph = remove_inverse_edges(graph)
    graph = remove_wind_edges(graph, containers, 1)
    yield from extract_direct_jordans(graph)
    yield from extract_mixed_jordans(graph)


def intersect_containers(
    containers: JordanContainer,
) -> Iterable[IJordanCurve]:
    """
    Computes the intersection of the shapes

    Parameters
    ----------
    shapes: Iterable[IShape]
        The shapes to be intersected
    return: IBoolean2D
        The result, can be Empty, Simple, Connected, Disjoint, BoolAnd, etc
    """
    containers = tuple(containers)
    for container in containers:
        if not isinstance(container, JordanContainer):
            raise TypeError(f"Not a JordanContainer, but {type(container)}")
    alljordans = []
    for container in containers:
        alljordans += list(container.flatten())
    graph = Graph(alljordans)
    graph = remove_inverse_edges(graph)
    graph = remove_wind_edges(graph, containers, 0)
    yield from extract_direct_jordans(graph)
    yield from extract_mixed_jordans(graph)


def identify_container(
    simples: Iterable[IJordanCurve],
) -> JordanContainer:
    """
    Identify the final container (Simple, Connected, Disjoint) from the
    received jordan curves
    """
    simples = tuple(simples)
    for simple in simples:
        if not isinstance(simple, IJordanCurve):
            raise TypeError(f"Received {type(simple)}")

    def sorter(jordan):
        return jordan.area

    simples = sorted(simples, key=sorter)
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
        disshapes.append(connsimples)
    return JordanContainer(disshapes)


class Node(tuple):
    """
    A node of the class Graph.
    Keeps track of:
    * Jordan curve's index
    * The parameter, such evaluated at curve gives the point
    * The index of the point on the graph
    """

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
    """
    This class has the purpose of storing an edge
    It keeps track of
    * Jordan curve's index
    * The index of the start (first) point
    * The index of the ending (last) point
    """

    def __new__(cls, jordan_index: int, first_index: int, last_index: int):
        self = super(Edge, cls).__new__(
            cls, (jordan_index, first_index, last_index)
        )
        self.jordan_index = jordan_index
        self.first_index = first_index
        self.last_index = last_index
        return self


def extract_direct_jordans(graph: Graph) -> Iterable[IJordanCurve]:
    """
    Extracts the jordans curves that are not resulted
    by intersection of the jordans.
    It means the all/none of the edges are in the final shape
    """
    available_jordans = tuple(sorted(set(e[0] for e in graph.edges)))
    for ijord in available_jordans:
        jordan = graph.jordans[ijord]
        if len(graph.allknots[ijord]) != len(jordan.param_curve.knots):
            continue
        edges = tuple(e for e in graph.edges if e[0] == ijord)
        if len(edges) + 1 != len(graph.allknots[ijord]):
            continue
        indexpts = set(edge[1] for edge in edges)
        indexpts |= set(edge[2] for edge in edges)
        index = 0
        while index < len(graph.edges):
            edge = graph.edges[index]
            if edge.jordan_index == ijord:
                graph.edges.pop(index)
            elif edge[1] in indexpts or edge[2] in indexpts:
                graph.edges.pop(index)
            else:
                index += 1
        yield jordan


def extract_sequence(
    triplets: Iterable[Tuple[int, int, int]]
) -> Union[None, Iterable[int]]:
    """
    This function extract sequences
    """
    triplets = tuple(triplets)
    for i, triplet0 in enumerate(triplets):
        sequence = [i]
        lasttri = triplet0
        while True:
            if lasttri[2] == triplet0[1]:
                return tuple(sequence)
            for j, tripletj in enumerate(triplets):
                if j in sequence:
                    continue
                if tripletj[1] == lasttri[2]:
                    sequence.append(j)
                    lasttri = tripletj
                    break
            else:
                break
    return None


def extract_mixed_jordans(graph: Graph) -> Iterable[IJordanCurve]:
    """
    This function gives the jordan curves when there's intersection
    between the jordans, so it's a mix of some jordan curves
    """
    while True:
        sequence = extract_sequence(graph.edges)
        if sequence is None:
            break
        new_edges = tuple(graph.edges[i] for i in sequence)
        indexpts = set(e[1] for e in new_edges) | set(e[2] for e in new_edges)
        for edge in tuple(graph.edges):
            if edge[1] in indexpts or edge[2] in indexpts:
                graph.remove_edge(edge)
        segments = []
        for edge in tuple(new_edges):
            curve = graph.jordans[edge[0]].param_curve
            parama = graph.find_param(edge[0], edge[1])
            paramb = graph.find_param(edge[0], edge[2])
            if paramb <= parama:
                if paramb != curve.knots[0]:
                    raise ValueError("Not expected get here")
                paramb = curve.knots[-1]
            segment = curve.section(parama, paramb)
            segments.append(segment)
        curve = concatenate(*segments)
        yield transform_to_jordan(curve)


class Graph:
    """
    This class is meant to store a graph: contains nodes and edges

    Each node represents a point on the plane:
    * Either it's the vertex of a jordan curve
    * Or it's an intersection point between two jordans
    Each edge is a path that connects two nodes:
    it's presented by the jordan curve's index and the two nodes it connects
    """

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
        """
        Add a new node in the graph

        Parameters
        ----------
        ijordan: int
            The index of the jordan curve
        param: Parameter
            The value such evaluating gives a point
        """
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
        """
        Gives the point's index for such is evaluated the jordan's curve
        """
        for node in self.nodes:
            if node[0] == ijordan and node[1] == param:
                return node[2]
        raise ValueError(f"Could not find node {ijordan}, {param}")

    def find_param(self, ijordan: int, indexpt: int):
        """
        Searchs for the parameter value t such evaluating the curve p(t) at
        this value, gives the points[indexpt]
        """
        for node in self.nodes:
            if node.jordan_index == ijordan and node.point_index == indexpt:
                return node.parameter
        raise ValueError(f"Could not find parameter {ijordan}, {indexpt}")

    def add_edge(self, ijordan: int, inodea: int, inodeb: int):
        """
        Adds a new Edge into the graph with
        * index of jordan's curve
        * index of the starting node
        * index of the finishing node
        """
        edge = Edge(ijordan, inodea, inodeb)
        self.edges.append(edge)
        self.edges = sorted(self.edges)

    def remove_edge(self, edge: Edge):
        """
        Removes given edge from the graph
        """
        for i, cedge in enumerate(self.edges):
            if edge == cedge:
                self.edges.pop(i)
                return
        raise ValueError(
            f"Could not remove edge {edge} from current edges {self.edges}"
        )

    def compute_standard_nodes(self):
        """
        Inserts in the graph all the standard nodes:
        The nodes such are the vertex of each jordan curve.
        The vertices of a jordan curve are the points such are evaluation
        at the knots of the jordan curve
        """
        for i, jordan in enumerate(self.jordans):
            curve = jordan.param_curve
            for knot in curve.knots:
                self.add_node(i, knot)

    def compute_intersect_nodes(self):
        """
        Inserts on the graph all the nodes such are originated by
        the intersection of two jordan curves
        """
        njords = len(self.jordans)
        for i, jordani in enumerate(self.jordans):
            for j in range(i + 1, njords):
                jordanj = self.jordans[j]
                inters = two_curve_inter(jordani, jordanj)
                for parami, paramj in inters:
                    self.add_node(i, parami)
                    self.add_node(j, paramj)

    def compute_allknots(self):
        """
        Computes the expanded knots of each jordan curve.
        Normally a parametric curve has knots like
        [0, 1, 2, 3] and if there's an intersection at 0.5 and 2.3,
        then this function computes the expanded knots [0, 0.5, 1, 2, 2.3, 3]
        """
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
        """
        Add all the edges on the graphs.
        Meaning, it iterates over each jordan curve,
        adding the edges which this jordans connects.
        """
        for indj, _ in enumerate(self.jordans):
            knots = self.allknots[indj]
            for knota, knotb in zip(knots, knots[1:]):
                ptinda = self.find_node(indj, knota)
                ptindb = self.find_node(indj, knotb)
                self.add_edge(indj, ptinda, ptindb)

    def __str__(self) -> str:
        msg = f"Graph with {len(self.jordans)}, "
        msg += f"{len(self.points)} points, "
        msg += f"{len(self.nodes)} nodes, "
        msg += f"{len(self.edges)} edges\n"
        msg += "Points:\n"
        for i, point in enumerate(self.points):
            msg += f"    point {i}: {point}\n"
        msg += "Nodes:\n"
        for i, node in enumerate(self.nodes):
            msg += f"    node {i}: {node}\n"
        msg += "Edges:\n"
        for i, edge in enumerate(self.edges):
            msg += f"    edge {i}: {edge}\n"
        return msg


def extract_points(objs: IBoolean2D) -> Iterable[Point2D]:
    """
    Receives the result of the intersection of two curves
    and returns only the points that are in this intersection:
    * If it's a direct point, then it gives only the point
    * If it's a curve, then it gives the vertices of this curve
    """
    if not isinstance(objs, IBoolean2D):
        raise TypeError
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
    return setpts


def two_curve_inter(
    curvea: IJordanCurve, curveb: IJordanCurve
) -> Iterable[Tuple[Parameter, Parameter]]:
    """
    Computes the intersection of two parameted curves P(t) and Q(u)
    returning the pairs (ti, ui) such P(ti) = Q(ui)
    """
    if not isinstance(curvea, IJordanCurve):
        raise TypeError
    if not isinstance(curveb, IJordanCurve):
        raise TypeError
    objs = curve_and_curve(curvea, curveb)
    if isinstance(objs, Empty):
        return
    curvea = curvea.param_curve
    curveb = curveb.param_curve
    setpts = extract_points(objs)
    for point in setpts:
        parama = curvea.projection(point)[0]
        paramb = curveb.projection(point)[0]
        yield (parama, paramb)
