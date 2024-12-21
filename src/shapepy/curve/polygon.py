"""
This file defines the Polygonal curves:
* PolygonOpenCurve
* PolygonClosedCurve
* JordanPolygon
"""
from __future__ import annotations

from abc import abstractmethod
from typing import Iterable, Tuple, Union

import numpy as np

from ..analytic.utils import binom, uarctan2
from ..core import Math
from ..point import GeneralPoint, Point2D, treat_scalar
from .abc import (
    IClosedCurve,
    IJordanCurve,
    IOpenCurve,
    IParameterCurve,
    Parameter,
    Scalar,
)


def clean_open_curve(vertices: Iterable[GeneralPoint]) -> Iterable[Point2D]:
    """
    Removes the aligned vertex of the vertices.

    This function does not treat the case which the first point
    is aligned between the second and the last vertex.

    Parameters
    ----------
    vertices: Iterable[Point2D]
        The vertices to be cleaned
    return: Iterable[Point2D]
        The cleaned vertices
    """
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
        cross = (vi1 - vi0).cross(vi2 - vi1)
        if not cross:
            keep_vertices[i] = False
    new_vertices = (vertices[i] for i, k in enumerate(keep_vertices) if k)
    return tuple(new_vertices)


class PolygonCurve(IParameterCurve):
    """
    Defines a general Polygon Curve
    """

    def __init__(self, vertices: Iterable[GeneralPoint]):
        self.__vertices = tuple(clean_open_curve(vertices))

    @property
    def vertices(self) -> Iterable[Point2D]:
        return self.__vertices

    @property
    @abstractmethod
    def vectors(self) -> Iterable[Point2D]:
        """
        Gives the evaluated vectors of the polygon,
        meaning the difference between two consecutive vertices

        Parameters
        ----------
        return: Iterable[Point]
            The points which were evaluated at knots
        """
        raise NotImplementedError

    @property
    def lenght(self) -> Scalar:
        return sum(map(abs, self.vectors))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PolygonCurve):
            return False
        if len(self.vertices) != len(other.vertices):
            return False
        for verti, vertj in zip(self.vertices, other.vertices):
            if verti != vertj:
                return False
        return True

    def move(self, vector: GeneralPoint) -> Point2D:
        """
        Moves the curve in the plane by the given vector

        Parameters
        ----------
        vector: Point
            The pair (x, y) that must be added to the coordinates
        return: PolygonCurve
            Gives a polygonal curve, either open, closed or a jordan
        """
        if not isinstance(vector, Point2D):
            vector = Point2D(vector)
        return self.__class__(vertex.move(vector) for vertex in self.vertices)

    def scale(self, xscale: Scalar, yscale: Scalar) -> Point2D:
        """
        Scales the curve in the X and Y directions

        Parameters
        ----------
        xscale: Scalar
            The amount to be scaled in the X direction
        yscale: Scalar
            The amount to be scaled in the Y direction
        """
        return self.__class__(
            vertex.scale(xscale, yscale) for vertex in self.vertices
        )

    def rotate(self, uangle: Scalar, degrees: bool = False) -> Point2D:
        """
        Rotates the point around the origin.

        The angle mesure is unitary:
        * angle = 1 means 360 degrees rotation
        * angle = 0.5 means 180 degrees rotation
        * angle = 0.125 means 45 degrees rotation

        Parameters
        ----------
        angle: Scalar
            The unitary angle the be rotated.
        degrees: bool, default = False
            If the angle is mesure in degrees
        """
        if degrees:
            uangle = treat_scalar(uangle) / 360
        return self.__class__(
            vertex.rotate(uangle) for vertex in self.vertices
        )

    @property
    def knots(self) -> Iterable[Parameter]:
        return tuple(range(len(self.vectors) + 1))

    def projection(self, point: GeneralPoint) -> Iterable[Parameter]:
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
    """
    Class that defines a open Polygonal Curve
    """

    def __init__(self, vertices: Tuple[GeneralPoint, ...]):
        super().__init__(vertices)
        vectors = []
        for verti, vertj in zip(self.vertices, self.vertices[1:]):
            vectors.append(vertj - verti)
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
        index = int(Math.floor(node))
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
            startindex = int(Math.ceil(nodea))
        if nodeb == int(nodeb):
            endingindex = int(nodeb)
        else:
            endingindex = int(Math.ceil(nodeb))
        middlevertices = self.vertices[startindex:endingindex]
        newvertices = [startpoint] + list(middlevertices) + [endingpoint]
        return PolygonOpenCurve(tuple(newvertices))


class PolygonClosedCurve(PolygonCurve, IClosedCurve):
    """
    Class that defines a Closed Polygonal Curve
    """

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
        if not nodea < nodeb:
            raise ValueError(f"Invalid interval [{nodea}, {nodeb}]")
        if nodea == 0 and nodeb == len(self.vertices):
            return self
        startpoint = self.eval(nodea)
        endingpoint = self.eval(nodeb)
        if nodea == int(nodea):
            startindex = int(nodea) + 1
        else:
            startindex = int(Math.ceil(nodea))
        if nodeb == int(nodeb):
            endingindex = int(nodeb)
        else:
            endingindex = int(Math.floor(nodeb)) + 1
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
            vertex0 = self.vectors[proj - 1]
            vertex1 = self.vectors[proj]
            cross = vertex0.cross(vertex1)
            inner = vertex0.inner(vertex1)
            wind = uarctan2(cross, -inner)
            return wind % 1

        nverts = len(self.vertices)
        vertices = tuple(vertex - point for vertex in self.vertices)
        wind = 0
        for i, vertex0 in enumerate(vertices):
            vertex1 = vertices[(i + 1) % nverts]
            cross = vertex0.cross(vertex1)
            inner = vertex0.inner(vertex1)
            subwind = uarctan2(cross, inner)
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
        index = int(Math.floor(node)) % len(self.vertices)
        if derivate > 1:
            return 0 * self.vertices[0]
        if derivate == 1:
            return self.vectors[index]
        node %= 1
        if not node:
            return self.vertices[index]
        return self.vertices[index] + node * self.vectors[index]


class JordanPolygon(PolygonClosedCurve, IJordanCurve):
    """
    CLass that defines a Polygonal Jordan curve
    """

    @property
    def param_curve(self) -> PolygonClosedCurve:
        return self

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (IClosedCurve, IJordanCurve)):
            return False
        if self.area != other.area:
            return False
        if abs(self.lenght - other.lenght) > 1e-9:
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

    def reverse(self) -> JordanPolygon:
        newvertices = tuple(self.vertices[::-1])
        return self.__class__(newvertices)


# pylint: disable=too-many-locals
def polybidim(
    vertices: Tuple[Tuple[Scalar, Scalar], ...], expx: int, expy: int
) -> Scalar:
    """
    Computes the bidimensional integral on the area defined by the polygon

        I = int_P x^a * y^b dx dy

    Parameters
    ----------
    vertices: Tuple[Tuple[Scalar, Scalar], ...]
        The vertices of the polygon
    expx: int
        The value of the 'a', the exponent of 'x'
    expy: int
        The value of the 'b', the exponent of 'y'
    return: Scalar
        The integral's value
    """
    xvalues = tuple(vertex[0] for vertex in vertices)
    yvalues = tuple(vertex[1] for vertex in vertices)
    xvalues = np.array(xvalues, dtype="object")
    yvalues = np.array(yvalues, dtype="object")
    shixvls = np.roll(xvalues, shift=-1, axis=0)
    shiyvls = np.roll(yvalues, shift=-1, axis=0)

    matrix = [[0] * (expy + 1) for _ in range(expx + 1)]
    for i in range(expx + 1):
        for j in range(expy + 1):
            matrix[i][j] = binom(i + j, i) * binom(
                expx + expy - i - j, expy - j
            )
    cross = xvalues * shiyvls - yvalues * shixvls
    xvand0 = np.vander(xvalues, expx + 1)
    xvand1 = np.vander(shixvls, expx + 1, True)
    yvand0 = np.vander(yvalues, expy + 1)
    yvand1 = np.vander(shiyvls, expy + 1, True)
    soma = np.einsum(
        "k,ki,ki,ij,kj,kj", cross, xvand0, xvand1, matrix, yvand0, yvand1
    )
    denom = (expx + expy + 2) * (expx + expy + 1) * binom(expx + expy, expx)
    return soma / denom
