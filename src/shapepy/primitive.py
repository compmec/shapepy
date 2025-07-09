"""
This file contains functions to create primitive shapes such as:
- Regular polygons
- Circle
- Square

"""

import math
from copy import copy
from fractions import Fraction
from numbers import Real
from typing import Tuple

import numpy as np

from shapepy.curve import PlanarCurve
from shapepy.jordancurve import JordanCurve
from shapepy.polygon import Point2D
from shapepy.shape import EmptyShape, SimpleShape, WholeShape


class Primitive:
    """
    Primitive class with functions to create classical shapes such as
    `circle`, `triangle`, `square`, `regular_polygon` and a generic `polygon`

    .. note:: This class also contains ``empty`` and ``whole``
        instances to easy access

    """

    empty = EmptyShape()
    whole = WholeShape()

    @staticmethod
    def regular_polygon(
        nsides: int, radius: float = 1, center: Point2D = (0, 0)
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
        if not isinstance(nsides, int):
            raise ValueError
        if nsides < 3:
            raise ValueError
        if not isinstance(radius, Real):
            raise ValueError
        if radius <= 0:
            raise ValueError
        center = Point2D(center)
        if nsides == 4:
            vertices = [(radius, 0), (0, radius), (-radius, 0), (0, -radius)]
            vertices = tuple(center + Point2D(vertex) for vertex in vertices)
        else:
            vertices = np.empty((nsides, 2), dtype="float64")
            theta = np.linspace(0, math.tau, nsides, endpoint=False)
            vertices[:, 0] = radius * np.cos(theta)
            vertices[:, 1] = radius * np.sin(theta)
            vertices = tuple(center + Point2D(vertex) for vertex in vertices)
        return Primitive.polygon(vertices)

    @staticmethod
    def polygon(vertices: Tuple[Point2D]) -> SimpleShape:
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
        vertices = tuple(Point2D(vertex) for vertex in vertices)
        jordan_curve = JordanCurve.from_vertices(vertices)
        return SimpleShape(jordan_curve)

    @staticmethod
    def triangle(side: float = 1, center: Point2D = (0, 0)) -> SimpleShape:
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
        center = Point2D(center)
        vertices = [(0, 0), (side, 0), (0, side)]
        vertices = tuple(center + Point2D(vertex) for vertex in vertices)
        return Primitive.polygon(vertices)

    @staticmethod
    def square(side: float = 1, center: Point2D = (0, 0)) -> SimpleShape:
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
        if not isinstance(side, Real) or side <= 0:
            raise ValueError
        center = Point2D(center)

        if isinstance(side, int):
            side = Fraction(side)
        side /= 2
        vertices = [(side, side), (-side, side), (-side, -side), (side, -side)]
        vertices = [center + Point2D(vertex) for vertex in vertices]
        return Primitive.polygon(vertices)

    @staticmethod
    def circle(
        radius: float = 1, center: Point2D = (0, 0), ndivangle: int = 16
    ) -> SimpleShape:
        """
        Creates a circle

        Parameters
        ----------

        radius : float, default: 1
            Radius of the circle
        center : Point2D, default: (0, 0)
            Center of the circle
        ndivangle : int, 16
            Number of divisions of the circle, minimum 4

        -------------------------------------------

        return : SimpleShape
            The simple shape that represents the circle

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()

        .. image:: ../img/primitive/positive_circle.svg

        .. note::

            We represent the circle by many quadratic segments.
            NURBS are not implemented in this code to represent
            exactly circles. You can choose the number of quadratic
            terms by changing ``ndivangle``.

        """
        if not isinstance(radius, Real) or radius <= 0:
            raise ValueError
        if not isinstance(ndivangle, int) or ndivangle < 4:
            raise ValueError
        center = Point2D(center)

        angle = math.tau / ndivangle
        height = np.tan(angle / 2)

        start_point = radius * Point2D(1, 0)
        middle_point = radius * Point2D(1, height)
        beziers = []
        for _ in range(ndivangle - 1):
            end_point = copy(start_point).rotate(angle)
            new_bezier = PlanarCurve([start_point, middle_point, end_point])
            beziers.append(new_bezier)
            start_point = end_point
            middle_point = copy(middle_point).rotate(angle)
        end_point = beziers[0].ctrlpoints[0]
        new_bezier = PlanarCurve([start_point, middle_point, end_point])
        beziers.append(new_bezier)

        jordan_curve = JordanCurve.from_segments(beziers)
        jordan_curve.move(center)
        circle = SimpleShape(jordan_curve)
        return circle
