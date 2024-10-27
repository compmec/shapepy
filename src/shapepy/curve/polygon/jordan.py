from __future__ import annotations

import math
from typing import Tuple

from ...core import IObject2D, Scalar
from ...point import GeneralPoint, Point2D
from .curve import LinearSegment


class JordanPolygon(IObject2D):

    def __init__(self, vertices: Tuple[GeneralPoint, ...]):
        self.vertices = vertices

    @property
    def vertices(self) -> Tuple[Point2D, ...]:
        return self.__vertices

    @property
    def vectors(self) -> Tuple[Point2D, ...]:
        return self.__vectors

    @property
    def lenght(self) -> Scalar:
        return self.__lenght

    @property
    def area(self) -> Scalar:
        return self.__area

    @property
    def segments(self) -> Tuple[LinearSegment, ...]:
        segs = []
        for i, verti in enumerate(self.vertices):
            verj = self.vertices[(i + 1) % len(self.__vertices)]
            segs.append(LinearSegment(verti, verj))
        return tuple(segs)

    @vertices.setter
    def vertices(self, vertices: Tuple[GeneralPoint, ...]):
        vertices = list(vertices)
        for i, vertex in enumerate(vertices):
            if not isinstance(vertex, Point2D):
                vertices[i] = Point2D(vertex)
        area = 0
        vectors = []
        for i, vertexi in enumerate(vertices):
            j = (i + 1) % len(vertices)
            vertexj = vertices[j]
            vector = vertexj - vertexi
            vectors.append(vector)
            area += vertexi.cross(vertexj) / 2
        lenght = sum(map(abs, vectors))
        self.__vertices = tuple(vertices)
        self.__vectors = tuple(vectors)
        self.__lenght = lenght
        self.__area = area

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JordanPolygon):
            return False
        if self.lenght != other.lenght or self.area != other.area:
            return False
        if len(self.vertices) != len(other.vertices):
            return False
        index = 0
        for j, vertj in enumerate(other.vertices):
            if vertj == self.vertices[0]:
                index = j
                break
        nverts = len(self.vertices)
        for i, verti in enumerate(self.vertices):
            vertj = other.vertices[(index + i) % nverts]
            if verti != vertj:
                return False
        return True

    def __str__(self) -> str:
        return f"JordanPolygon({self.area}, {self.lenght})"

    def __repr__(self) -> str:
        return self.__str__()

    def __invert__(self) -> JordanPolygon:
        newvertices = tuple(self.vertices[::-1])
        return self.__class__(newvertices)

    def move(self, *vector: GeneralPoint) -> JordanPolygon:
        if len(vector) == 1:
            vector = vector[0]
        if not isinstance(vector, Point2D):
            vector = Point2D(vector)
        if vector != (0, 0):
            self.vertices = tuple(vertex + vector for vertex in self.vertices)
        return self

    def scale(self, xscale: Scalar = 1, yscale: Scalar = 1) -> JordanPolygon:
        if xscale != 1 or yscale != 1:
            self.vertices = tuple(
                vertex.scale(xscale, yscale) for vertex in self.vertices
            )
        return self

    def rotate(self, angle: Scalar, degrees: bool = False) -> JordanPolygon:
        if degrees:
            angle *= math.pi / 180
        if angle != 0:
            self.vertices = tuple(
                vertex.rotate(angle) for vertex in self.vertices
            )
        return self
