"""
This file contains functions to create primitive shapes such as:
- Regular polygons
- Circle
- Square
"""

import math
from fractions import Fraction
from typing import Tuple

import numpy as np

from compmec.shape.curve import PlanarCurve
from compmec.shape.jordancurve import JordanCurve
from compmec.shape.polygon import Point2D
from compmec.shape.shape import ConnectedShape, SimpleShape, WholeShape


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
        if nsides == 4:
            vertices = [(radius, 0), (0, radius), (-radius, 0), (0, -radius)]
            vertices = tuple([center + Point2D(vertex) for vertex in vertices])
        else:
            vertices = np.empty((nsides, 2), dtype="float64")
            theta = np.linspace(0, math.tau, nsides, endpoint=False)
            vertices[:, 0] = radius * np.cos(theta)
            vertices[:, 1] = radius * np.sin(theta)
            vertices = tuple([center + Point2D(vertex) for vertex in vertices])
        jordan_polygon = JordanCurve.from_vertices(vertices)
        simple_shape = SimpleShape(jordan_polygon)
        return simple_shape

    @staticmethod
    def polygon(vertices: Tuple[Point2D]) -> SimpleShape:
        vertices = [Point2D(vertex) for vertex in vertices]
        jordan_curve = JordanCurve.from_vertices(vertices)
        if float(jordan_curve) > 0:
            return SimpleShape(jordan_curve)
        hole = SimpleShape(abs(jordan_curve))
        return ConnectedShape(WholeShape(), [hole])

    @staticmethod
    def square(side: float = 1, center: Point2D = (0, 0)) -> SimpleShape:
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

        if isinstance(side, int):
            side = Fraction(side)
        side /= 2
        vertices = [(side, side), (-side, side), (-side, -side), (side, -side)]
        vertices = [center + Point2D(vertex) for vertex in vertices]
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

        angle = math.tau / ndivangle
        height = np.tan(angle / 2)

        start_point = radius * Point2D(1, 0)
        middle_point = radius * Point2D(1, height)
        beziers = []
        for i in range(ndivangle - 1):
            end_point = start_point.copy().rotate(angle)
            new_bezier = PlanarCurve([start_point, middle_point, end_point])
            beziers.append(new_bezier)
            start_point = end_point
            middle_point = middle_point.copy().rotate(angle)
        end_point = beziers[0].ctrlpoints[0]
        new_bezier = PlanarCurve([start_point, middle_point, end_point])
        beziers.append(new_bezier)

        jordan_curve = JordanCurve.from_segments(beziers)
        jordan_curve.move(center)
        circle = SimpleShape(jordan_curve)
        return circle
