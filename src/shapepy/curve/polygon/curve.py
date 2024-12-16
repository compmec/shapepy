from __future__ import annotations

import math
from abc import abstractmethod
from typing import Iterable, Tuple, Union

from numpy import arctan2

from ...point import GeneralPoint, Point2D
from ..abc import IClosedCurve, IOpenCurve, IParameterCurve, Parameter, Scalar


def clean_open_curve(vertices: Iterable[GeneralPoint]) -> Iterable[Point2D]:
    vertices = list(vertices)
    for i, vertex in enumerate(vertices):
        if not isinstance(vertex, Point2D):
            vertices[i] = Point2D(vertex)
    keep_vertices = [True] * len(vertices)
    for i, vi1 in enumerate(vertices):
        if i == 0 or i + 1 == len(vertices):
            continue
        vi0 = vertices[i - 1]
        vi2 = vertices[i + 1]
        if not (vi1 - vi0).cross(vi2 - vi1):
            keep_vertices[i] = False
    new_vertices = (vertices[i] for i, k in enumerate(keep_vertices) if k)
    return tuple(new_vertices)


class PolygonCurve(IParameterCurve):
    def __init__(self, vertices: Iterable[GeneralPoint]):
        self.__vertices = tuple(clean_open_curve(vertices))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PolygonCurve):
            return False
        if self.knots[-1] != other.knots[-1]:
            return False
        for verti, vertj in zip(self.vertices, other.vertices):
            if verti != vertj:
                return False
        return True

    @property
    def knots(self) -> Tuple[Parameter, ...]:
        return tuple(range(len(self.vectors) + 1))

    @property
    def vertices(self) -> Tuple[Point2D, ...]:
        return self.__vertices

    @property
    def lenght(self) -> Scalar:
        return sum(map(abs, self.vectors))

    @property
    @abstractmethod
    def vectors(self) -> Tuple[Point2D, ...]:
        raise NotImplementedError

    def projection(self, point: GeneralPoint) -> Tuple[Parameter, ...]:
        if not isinstance(point, Point2D):
            point = Point2D(point)
        vertices = tuple(point - vertex for vertex in self.vertices)
        projects = []
        dist_squares = []
        for i, vector in enumerate(self.vectors):
            vertex = vertices[i]
            param = vertex.inner(vector) / vector.inner(vector)
            param = max(0, min(1, param))
            vectdist = param * vector - vertex
            projects.append(i + param)
            dist_squares.append(vectdist.inner(vectdist))
        min_distsquare = min(dist_squares)
        params = set(
            p for p, d2 in zip(projects, dist_squares) if d2 == min_distsquare
        )
        return tuple(sorted(params))


class PolygonOpenCurve(PolygonCurve, IOpenCurve):
    def __init__(self, vertices: Tuple[GeneralPoint, ...]):
        super().__init__(vertices)
        vectors = []
        for vi, vj in zip(self.vertices, self.vertices[1:]):
            vectors.append(vj - vi)
        self.__vectors = tuple(vectors)

    @property
    def vectors(self) -> Tuple[Point2D, ...]:
        return self.__vectors

    def __str__(self) -> str:
        nverts = len(self.vertices)
        msg = f"Polygon Open Curve of {nverts} vertices "
        msg += str(self.vertices)
        return msg

    def __repr__(self) -> str:
        nverts = len(self.vertices)
        msg = f"PolygonOpenCurve({nverts})"
        return msg

    def eval(self, node: Parameter, derivate: int = 0) -> Point2D:
        if node < 0 or len(self.vertices) - 1 < node:
            raise ValueError(f"Given node {node} is outside the interval")
        index = int(math.floor(node))
        if derivate > 1:
            return 0 * self.vertices[0]
        if derivate == 1:
            index = min(index, len(self.vertices) - 2)
            return self.vectors[index]
        node %= 1
        if not node:
            return self.vertices[index]
        return self.vertices[index] + node * self.vectors[index]

    def section(self, nodea: Parameter, nodeb: Parameter) -> PolygonOpenCurve:
        if nodea == 0 and nodeb == len(self.vertices) - 1:
            return self
        startpoint = self.eval(nodea)
        endingpoint = self.eval(nodeb)
        if nodea == int(nodea):
            startindex = int(nodea) + 1
        else:
            startindex = int(math.ceil(nodea))
        if nodeb == int(nodeb):
            endingindex = int(nodeb)
        else:
            endingindex = int(math.ceil(nodeb))
        middlevertices = self.vertices[startindex:endingindex]
        newvertices = [startpoint] + list(middlevertices) + [endingpoint]
        return PolygonOpenCurve(tuple(newvertices))


class PolygonClosedCurve(PolygonCurve, IClosedCurve):
    def __init__(self, vertices: Tuple[GeneralPoint, ...]):
        super().__init__(vertices)
        vectors = []
        nverts = len(self.vertices)
        for i, verti in enumerate(self.vertices):
            vertj = self.vertices[(i + 1) % nverts]
            vectors.append(vertj - verti)
        self.__vectors = tuple(vectors)

    @property
    def vectors(self) -> Tuple[Point2D, ...]:
        return self.__vectors

    @property
    def area(self) -> Scalar:
        nverts = len(self.vertices)
        area = 0
        for i, vertexi in enumerate(self.vertices):
            j = (i + 1) % nverts
            vertexj = self.vertices[j]
            area += vertexi.cross(vertexj) / 2
        return area

    def __str__(self) -> str:
        nverts = len(self.vertices)
        msg = f"Polygon Closed Curve of {nverts} vertices "
        msg += str(self.vertices)
        return msg

    def __repr__(self) -> str:
        nverts = len(self.vertices)
        msg = f"PolygonClosedCurve({nverts})"
        return msg

    def section(
        self, nodea: Parameter, nodeb: Parameter
    ) -> Union[PolygonOpenCurve, PolygonClosedCurve]:
        if not (nodea < nodeb):
            raise ValueError(f"Invalid interval [{nodea}, {nodeb}]")
        if nodea == 0 and nodeb == len(self.vertices):
            return self
        startpoint = self.eval(nodea)
        endingpoint = self.eval(nodeb)
        if nodea == int(nodea):
            startindex = int(nodea) + 1
        else:
            startindex = int(math.ceil(nodea))
        if nodeb == int(nodeb):
            endingindex = int(nodeb)
        else:
            endingindex = int(math.floor(nodeb)) + 1
        middlevertices = self.vertices[startindex:endingindex]
        newvertices = [startpoint] + list(middlevertices) + [endingpoint]
        return PolygonOpenCurve(newvertices)

    def winding(self, point: GeneralPoint) -> Scalar:
        if not isinstance(point, Point2D):
            point = Point2D(point)
        proj = self.projection(point)[0]
        diff = self.eval(proj) - point
        if abs(diff) < 1e-9:
            if not isinstance(proj, int):
                return 0.5
            nverts = len(self.vertices)
            v0, v1 = self.vectors[proj - 1], self.vectors[proj]
            cross = float(v0.cross(v1))
            inner = float(v0.inner(v1))
            wind = arctan2(cross, -inner) / math.tau
            return wind % 1

        nverts = len(self.vertices)
        vertices = tuple(vertex - point for vertex in self.vertices)
        wind = 0
        for i, vertex0 in enumerate(vertices):
            vertex1 = vertices[(i + 1) % nverts]
            cross = float(vertex0.cross(vertex1))
            inner = float(vertex0.inner(vertex1))
            subwind = arctan2(cross, inner) / math.tau
            wind += subwind

        if abs(wind) < 1e-9:
            wind = 0
        elif abs(wind - 1) < 1e-9:
            wind = 1
        elif abs(wind + 1) < 1e-9:
            wind = -1
        if self.area > 0:
            return wind
        return 0 if abs(wind + 1) < 1e-9 else 1 - wind

    def eval(self, node: Parameter, derivate: int = 0) -> Point2D:
        index = int(math.floor(node)) % len(self.vertices)
        if derivate > 1:
            return 0 * self.vertices[0]
        if derivate == 1:
            return self.vectors[index]
        node %= 1
        if not node:
            return self.vertices[index]
        return self.vertices[index] + node * self.vectors[index]
