"""
This file contains functions to create primitive shapes such as:
- Regular polygons
- Circle
- Square
"""

from typing import Tuple

import numpy as np

from compmec import nurbs
from compmec.shape.jordancurve import JordanCurve, JordanPolygon
from compmec.shape.polygon import Point2D
from compmec.shape.shape import SimpleShape


class Primitive:
    @staticmethod
    def regular_polygon(nsides: int) -> SimpleShape:
        """
        Creates a regular polygon of n-sides inscribed in a circle of radius 1.
            if nsides = 3, it's a triangle
            if nsides = 4, it's a square, of side square(2)
        """
        if not isinstance(nsides, int):
            raise TypeError("nsides must be an integer")
        if nsides < 3:
            raise ValueError("nsides must be >= 3")
        vertices = np.empty((nsides, 2), dtype="float64")
        theta = np.linspace(0, 2 * np.pi, nsides, endpoint=False)
        vertices[:, 0] = np.cos(theta)
        vertices[:, 1] = np.sin(theta)
        vertices = tuple([Point2D(vertex) for vertex in vertices])
        jordan = JordanPolygon(vertices)
        return SimpleShape(jordan)

    @staticmethod
    def polygon(vertices: Tuple[Point2D]) -> SimpleShape:
        vertices = [Point2D(vertex) for vertex in vertices]
        jordan_curve = JordanPolygon(vertices)
        return SimpleShape(jordan_curve)

    @staticmethod
    def square(side: float = 1, center: Point2D = (0, 0)) -> SimpleShape:
        """
        Creates a square of side `side` and center `center`.
        Its edges are aligned with the axes
        """
        center = Point2D(center)
        vertices = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
        vertices = [center + side * Point2D(vertex) for vertex in vertices]
        vertices = tuple(vertices)
        jordan = JordanPolygon(vertices)
        return SimpleShape(jordan)

    @staticmethod
    def circle(radius: float = 1, center: Point2D = (0, 0)) -> SimpleShape:
        """
        Creates a circle with given radius and center.
        """
        degree = 2
        ndivangle = 16
        last_knot = ndivangle
        knotvector = (0, last_knot) + degree * tuple(range(last_knot + 1))
        knotvector = tuple(sorted(knotvector))
        knotvector = nurbs.KnotVector(knotvector)
        curve = nurbs.Curve(knotvector)

        theta = 2 * np.pi / ndivangle
        cos, sin = np.cos(theta), np.sin(theta)
        height = np.tan(theta / 2)
        rotation = np.array(((cos, -sin), (sin, cos)))
        points = [(1, 0), (1, height), (cos, sin)]
        for i in range(ndivangle - 1):
            new_point = rotation @ points[-2]
            points.append(new_point)
            new_point = rotation @ points[-2]
            points.append(new_point)
        points[-1] = points[0]
        points = [Point2D(point) for point in points]
        curve.ctrlpoints = points
        jordan_curve = JordanCurve(curve)
        circle = SimpleShape(jordan_curve)
        center = Point2D(center)
        circle.scale(radius, radius)
        circle.move(center)
        return circle
