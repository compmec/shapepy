"""
File that defines the structures used to compute the intersection of curves

It's used to compute further the boolean operations of shapes
"""

from __future__ import annotations

from numbers import Real
from typing import Dict, Iterable, List, Tuple

from .. import default
from .abc import IContinuousCurve
from .curve import extract_knots
from .point import GeometricPoint


class Edge:
    """
    Defines an edge, which is a segment of continuous curve that connects
    the vertexa to the vertexb.

    For simplicity, the curve cannot be piecewise, only a analytic curve

    Although there's infinite ways to describe a path from vertexa to vertexb,
    an edge is equal to another if and only if they describe the same path.
    """

    def __init__(
        self,
        vertexa: GeometricPoint,
        vertexb: GeometricPoint,
        triplets: Iterable[Tuple[IContinuousCurve, Real, Real]],
    ):
        self.vertexa = vertexa
        self.vertexb = vertexb
        self.triplets = tuple(triplets)
        self.__subcurve = None

    @property
    def subcurve(self) -> IContinuousCurve:
        """
        Gets the cage that bounds the edge.
        """
        if self.__subcurve is None:
            curve, knota, knotb = self.triplets[0]
            self.__subcurve = curve.section([knota, knotb])
        return self.__subcurve

    def __and__(self, other: Edge) -> Graph:
        """
        Computes the intersection between two edges, giving a graph
        """
        result = Graph()
        if (self.subcurve.cage & other.subcurve.cage) is None:
            return result
        raise NotImplementedError


class Graph:
    """
    Defines a graph
    """

    def __init__(self):
        self.edges: List[Edge] = []

    def vertices(self) -> Dict[GeometricPoint, List[Edge]]:
        """
        Gives the vertices and the connected edges for each vertex
        """
        vertices = {}
        for edge in self.edges:
            if edge.vertexa not in vertices:
                vertices[edge.vertexa] = []
            if edge.vertexb not in vertices:
                vertices[edge.vertexb] = []
            vertices[edge.vertexa].append(edge)
            vertices[edge.vertexb].append(edge)
        return vertices

    def add_edge(self, edge: Edge):
        """
        Adds a new edge on the graph
        """
        self.edges.append(edge)

    def remove_edge(self, edge: Edge):
        """
        Removes an edge of the graph
        """
        for i, internal in enumerate(self.edges):
            if id(internal) == id(edge):
                self.edges.pop(i)
                break

    def __ior__(self, other: Graph) -> Graph:
        """
        This function creates a new Graph that unites two graphs
        matching the vertices

        This function must not be used careless
        """
        if not isinstance(other, Graph):
            raise TypeError
        for edge in other.edges:
            self.add_edge(edge)
        return self

    def __and__(self, other: Graph) -> Graph:
        """
        This function creates a new Graph that computes the intersection
        between the edges of the curves of both graphs
        """
        if not isinstance(other, Graph):
            raise TypeError
        result = Graph()
        for edge1 in self.edges:
            for edge2 in other.edges:
                result |= edge1 & edge2
        return result


def curve2graph(curve: IContinuousCurve) -> Graph:
    """
    Creates a graph based on the curve.

    It's particular useful for piecewise curves:
    each segment of the curve is an edge of the graph

    For non-piecewise curves, the graph contains only one edge
    """
    knots = tuple(extract_knots(curve))
    nedges = len(knots) - 1
    vertices = tuple(map(curve.eval, knots))
    graph = Graph()
    for i in range(nedges):
        knota = knots[i]
        knotb = knots[i + 1]
        vertexa = vertices[i]
        vertexb = vertices[i + 1]
        edge = Edge(vertexa, vertexb, ((curve, knota, knotb),))
        graph.add_edge(edge)
    return graph


def sample(left: Real, right: Real, npts: int) -> Iterable[Real]:
    """
    It's equivalent to linspace, but it handles when the
    left or right values are infinity
    """
    if default.isinfinity(left) or default.isinfinity(right):
        raise NotImplementedError
    ndivs = npts - 1
    return ((((ndivs - i) * left + i * right) / ndivs) for i in range(npts))
