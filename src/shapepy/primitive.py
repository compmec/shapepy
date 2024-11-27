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

from .analytic.trigonometric import Trignomial
from .core import Scalar
from .curve.piecewise import JordanPiecewise
from .curve.polygon import JordanPolygon
from .point import GeneralPoint, Point2D
from .shape import SimpleShape


class Primitive:
    """
    Primitive class with functions to create classical shapes such as
    `circle`, `triangle`, `square`, `regular_polygon` and a generic `polygon`

    """

    @staticmethod
    def regular_polygon(
        nsides: int, radius: Scalar = 1, center: GeneralPoint = (0, 0)
    ) -> SimpleShape:
        """
        Creates a regular polygon

        Parameters
        ----------

        nsides : int
            Number of sides of regular polygon, >= 3
        radius : float, default: 1
            Radius of the external circle that contains the polygon.
        center : Point2D, default: (0, 0)
            The geometric center of the regular polygon

        -------------------------------------------

        return : SimpleShape
            The simple shape that represents the regular polygon

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> triangle = Primitive.regular_polygon(nsides = 3)

        .. image:: ../img/primitive/regular3.svg

        .. image:: ../img/primitive/regular4.svg

        .. image:: ../img/primitive/regular5.svg

        """
        nsides = int(nsides)
        if nsides < 3:
            raise ValueError
        if radius <= 0:
            raise ValueError
        if not isinstance(center, Point2D):
            center = Point2D(center)

        if nsides == 4:
            vertices = [
                (radius, 0 * radius),
                (0 * radius, radius),
                (-radius, 0 * radius),
                (0 * radius, -radius),
            ]
        else:
            vertices = np.empty((nsides, 2), dtype="float64")
            theta = np.linspace(0, math.tau, nsides, endpoint=False)
            vertices[:, 0] = radius * np.cos(theta)
            vertices[:, 1] = radius * np.sin(theta)
        simple = Primitive.polygon(vertices)
        return simple.move(center)

    @staticmethod
    def polygon(vertices: Tuple[GeneralPoint]) -> SimpleShape:
        """
        Creates a generic polygon

        vertices: tuple[Point2D]
            Vertices of the polygon

        -------------------------------------------

        return : SimpleShape
            The simple shape that represents the polygon

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> vertices = [(1, 0), (0, 1), (-1, 1), (0, -1)]
        >>> shape = Primitive.polygon(vertices)

        .. image:: ../img/primitive/diamond.svg

        """
        jordan = JordanPolygon(vertices)
        return SimpleShape(jordan)

    @staticmethod
    def triangle(
        side: Scalar = 1, center: GeneralPoint = (0, 0)
    ) -> SimpleShape:
        """
        Create a right triangle

        Parameters
        ----------
        side : float, default: 1
            Width and height of the triangle
        center : Point2D, default: (0, 0)
            Position of the vertex of right angle

        -------------------------------------------

        return : SimpleShape
            The simple shape that represents the triangle

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> triangle = Primitive.triangle()

        .. image:: ../img/primitive/triangle.svg

        """
        if side <= 0:
            raise ValueError
        vertices = [(0 * side, 0 * side), (side, 0 * side), (0 * side, side)]
        simple = Primitive.polygon(vertices)
        return simple.move(center)

    @staticmethod
    def square(side: Scalar = 1, center: GeneralPoint = (0, 0)) -> SimpleShape:
        """
        Creates a square with sides aligned with axis

        Parameters
        ----------

        side : float, default: 1
            Side of the square.
        center : Point2D, default: (0, 0)
            The geometric center of the square

        -------------------------------------------

        return : SimpleShape
            The simple shape that represents the square

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> square = Primitive.square()

        .. image:: ../img/primitive/square.svg

        """
        if side <= 0:
            raise ValueError
        if isinstance(side, int):
            side = Fraction(side)
        vertices = [
            (side / 2, side / 2),
            (-side / 2, side / 2),
            (-side / 2, -side / 2),
            (side / 2, -side / 2),
        ]
        simple = Primitive.polygon(vertices)
        return simple.move(center)

    @staticmethod
    def circle(
        radius: Scalar = 1, center: GeneralPoint = (0, 0)
    ) -> SimpleShape:
        """
        Creates a circle

        Parameters
        ----------

        radius : float, default: 1
            Radius of the circle
        center : Point2D, default: (0, 0)
            Center of the circle

        -------------------------------------------

        return : SimpleShape
            The simple shape that represents the circle

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()

        .. image:: ../img/primitive/positive_circle.svg

        """
        xfunc = Trignomial((center[0], 0 * radius, radius), 1)
        yfunc = Trignomial((center[1], radius, 0 * radius), 1)
        jordan = JordanPiecewise(((xfunc, yfunc),))
        return SimpleShape(jordan, True)
