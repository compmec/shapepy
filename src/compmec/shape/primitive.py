"""
This file contains functions to create primitive shapes such as:
- Regular polygons
- Circle
- Square
"""

from fractions import Fraction
from typing import Tuple

import numpy as np

from compmec import nurbs
from compmec.shape.jordancurve import JordanCurve
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
        jordan_polygon = JordanCurve.from_vertices(vertices)
        simple_shape = SimpleShape(jordan_polygon)
        simple_shape.scale(radius, radius)
        simple_shape.move(center)
        return simple_shape

    @staticmethod
    def polygon(vertices: Tuple[Point2D]) -> SimpleShape:
        vertices = [Point2D(vertex) for vertex in vertices]
        jordan_curve = JordanCurve.from_vertices(vertices)
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
        jordan = JordanCurve.from_vertices(vertices)
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
        knotvector = nurbs.GeneratorKnotVector.bezier(degree, Fraction)

        angle = 2 * np.pi / ndivangle
        height = np.tan(angle / 2)

        start_point = Point2D(1, 0)
        middle_point = Point2D(1, height)
        beziers = []
        for i in range(ndivangle - 1):
            end_point = start_point.copy().rotate(angle)
            new_bezier = nurbs.Curve(knotvector)
            new_bezier.ctrlpoints = [start_point, middle_point, end_point]
            beziers.append(new_bezier)
            start_point = end_point.copy()
            middle_point = middle_point.copy().rotate(angle)
        end_point = Point2D(1, 0)
        new_bezier = nurbs.Curve(knotvector)
        new_bezier.ctrlpoints = [start_point, middle_point, end_point]
        beziers.append(new_bezier)

        jordan_curve = JordanCurve.from_segments(beziers)
        circle = SimpleShape(jordan_curve)
        circle.scale(radius, radius)
        circle.move(center)
        return circle
