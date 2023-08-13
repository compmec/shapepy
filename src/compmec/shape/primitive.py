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
        points = np.empty((nsides, 2), dtype="float64")
        theta = np.linspace(0, 2 * np.pi, nsides, endpoint=False)
        points[:, 0] = np.cos(theta)
        points[:, 1] = np.sin(theta)
        jordan = JordanPolygon(points)
        return SimpleShape([jordan])

    @staticmethod
    def triangle(side: float = 1, center: Tuple[float] = (0, 0)) -> SimpleShape:
        """
        Creates an equilatery triangle of side `side` and center `center`.
        """
        vertices = [
            (0, np.sqrt(3) / 3),
            (-1 / 2, -np.sqrt(3) / 6),
            (1 / 2, -np.sqrt(3) / 6),
        ]
        vertices = side * np.array(vertices)
        vertices[:, 0] += center[0]
        vertices[:, 1] += center[1]
        vertices = tuple(vertices)
        jordanpolygon = JordanPolygon(vertices)
        return SimpleShape([jordanpolygon])

    @staticmethod
    def square(side: float = 1, center: Tuple[float] = (0, 0)) -> SimpleShape:
        """
        Creates a square of side `side` and center `center`.
        Its edges are aligned with the axes
        """

        vertices = [(1 / 2, 1 / 2), (-1 / 2, 1 / 2), (-1 / 2, -1 / 2), (1 / 2, -1 / 2)]
        vertices = side * np.array(vertices)
        vertices[:, 0] += center[0]
        vertices[:, 1] += center[1]
        vertices = tuple(vertices)
        jordanpolygon = JordanPolygon(vertices)
        return SimpleShape([jordanpolygon])

    @staticmethod
    def circle(radius: float = 1, center: Tuple[float] = (0, 0)) -> SimpleShape:
        """
        Creates a circle with given radius and center.
        """
        polygon = Primitive.regular_polygon(16)
        polygon *= radius
        polygon += center
        return polygon
