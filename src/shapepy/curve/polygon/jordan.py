from __future__ import annotations

import math
from typing import Tuple

from ...bounding import BoundRectangle
from ...core import Scalar
from ...point import GeneralPoint, Point2D
from ..abc import IJordanCurve
from .curve import PolygonClosedCurve, PolygonOpenCurve


class JordanPolygon(IJordanCurve):

    def __init__(self, vertices: Tuple[GeneralPoint, ...]):
        self.vertices = vertices

    @property
    def param_curve(self) -> PolygonClosedCurve:
        return self.__param_curve

    @property
    def vertices(self) -> Tuple[Point2D, ...]:
        return self.param_curve.vertices

    @property
    def vectors(self) -> Tuple[Point2D, ...]:
        return self.param_curve.vectors

    @property
    def lenght(self) -> Scalar:
        return self.param_curve.lenght

    @property
    def area(self) -> Scalar:
        return self.param_curve.area

    @property
    def segments(self) -> Tuple[PolygonOpenCurve, ...]:
        segments = []
        for i, verti in enumerate(self.vertices):
            verj = self.vertices[(i + 1) % len(self.vertices)]
            segment = PolygonOpenCurve([verti, verj])
            segments.append(segment)
        return tuple(segments)

    @vertices.setter
    def vertices(self, vertices: Tuple[GeneralPoint, ...]):
        self.__param_curve = PolygonClosedCurve(vertices)

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

    def move(self, vector: GeneralPoint) -> JordanPolygon:
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

    def winding(self, point: GeneralPoint) -> Scalar:
        if not isinstance(point, Point2D):
            point = Point2D(point)
        return self.param_curve.winding(point)

    def boundbox(self) -> BoundRectangle:
        minx = min(vertex[0] for vertex in self.vertices)
        miny = min(vertex[1] for vertex in self.vertices)
        maxx = max(vertex[0] for vertex in self.vertices)
        maxy = max(vertex[1] for vertex in self.vertices)
        return BoundRectangle((minx, miny), (maxx, maxy))
