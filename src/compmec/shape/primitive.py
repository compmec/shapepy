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
from compmec.shape.shape import ConnectedShape, NumIntegration, SimpleShape, WholeShape


class Primitive:
    @staticmethod
    def regular_polygon(
        nsides: int, radius: float = 1, center: Point2D = (0, 0)
    ) -> SimpleShape:
        """
        Creates a regular polygon of n-sides inscribed in a circle of radius 1.
            if nsides = 3, it's a triangle
            if nsides = 4, it's a square, of side square(2)
        """
        try:
            assert isinstance(nsides, int)
            assert nsides >= 3
            float(radius)
            assert radius > 0
            center = Point2D(center)
        except (ValueError, TypeError, AssertionError):
            raise ValueError("Input invalid")
        vertices = np.empty((nsides, 2), dtype="float64")
        theta = np.linspace(0, 2 * np.pi, nsides, endpoint=False)
        vertices[:, 0] = np.cos(theta)
        vertices[:, 1] = np.sin(theta)
        vertices = tuple([Point2D(vertex) for vertex in vertices])
        jordan_polygon = JordanPolygon(vertices)
        simple_shape = SimpleShape(jordan_polygon)
        simple_shape.scale(radius, radius)
        simple_shape.move(center)
        return simple_shape

    @staticmethod
    def polygon(vertices: Tuple[Point2D]) -> SimpleShape:
        vertices = [Point2D(vertex) for vertex in vertices]
        jordan_curve = JordanPolygon(vertices)
        area = NumIntegration.area_inside_jordan(jordan_curve)
        if area > 0:
            return SimpleShape(jordan_curve)
        simple_shape = SimpleShape(abs(jordan_curve))
        return ConnectedShape(WholeShape(), [simple_shape])

    @staticmethod
    def square(side: float = 2, center: Point2D = (0, 0)) -> SimpleShape:
        """
        Creates a square of side `side` and center `center`.
        Its edges are aligned with the axes
        """
        try:
            float(side)
            assert side > 0
            center = Point2D(center)
        except (ValueError, TypeError, AssertionError):
            raise ValueError("Input invalid")

        if isinstance(side, int) and (side % 2 == 0):
            side //= 2
        else:
            side /= 2
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
        try:
            float(radius)
            assert radius > 0
            center = Point2D(center)
        except (ValueError, TypeError, AssertionError):
            raise ValueError("Input invalid")

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
        circle.scale(radius, radius)
        circle.move(center)
        return circle
