"""
Defines the bounding objects to faster evaluation

"""

from __future__ import annotations

from numbers import Real
from typing import Union

from .point import GeometricPoint, geometric_point


class BoxCage:
    """
    Defines a bounding rectangular box to speed up the evaluation
    if a point is inside a region defined by a curve
    """

    def __init__(self, bot_point: GeometricPoint, top_point: GeometricPoint):
        self.bot = geometric_point(bot_point)
        self.top = geometric_point(top_point)

    def winding(self, point: GeometricPoint) -> Real:
        """
        Computes the winding number for the rectangle.
        Gives one of the four values:
        * 0.00: Point is outside
        * 0.25: Point is at the vertex
        * 0.50: Point is on the edge
        * 1.00: Point is interior

        Parameters
        ----------
        point: GeometricPoint
            The point to check its position

        Return
        ------
        Real
            The winding number, a real number in: {0, 0.25, 0.5, 1}

        Example
        -------
        >>> box = BoxCage((0, 0), (2, 2))
        >>> box.winding((-1, -1))  # Outside
        0
        >>> box.winding((0, 0))  # At vertex
        0.25
        >>> box.winding((0, 1))  # On the edge
        0.5
        >>> box.winding((1, 1))  # Interior
        1
        """

        def step(value: Real) -> Real:
            """
            Computes the step function:

            Parameters
            ----------
            value: Real
                The position to evaluate

            Return
            ------
            Real
                A real number in {0, 0.5, 1}

            Example
            -------
            >>> step(-2)
            0
            >>> step(-1)
            0
            >>> step(0)
            0.5
            >>> step(1)
            1
            >>> step(2)
            1
            """
            return 0 if value < 0 else 1 if value > 0 else 0.5

        point = geometric_point(point)
        xwind = step(point.x - self.bot.x) * step(self.top.x - point.x)
        ywind = step(point.y - self.bot.y) * step(self.top.y - point.y)
        return xwind * ywind

    def __contains__(self, point: GeometricPoint) -> bool:
        return 0 < self.winding(point)

    def __and__(self, other: BoxCage) -> Union[None, BoxCage]:
        if not isinstance(other, BoxCage):
            raise TypeError
        xmin = max(self.bot.x, other.bot.x)
        ymin = max(self.bot.y, other.bot.y)
        xmax = min(self.top.x, other.top.x)
        ymax = min(self.top.y, other.top.y)
        if xmax <= xmin or ymax <= ymin:
            return None
        return BoxCage((xmin, ymin), (xmax, ymax))

    def __or__(self, other: BoxCage) -> BoxCage:
        if not isinstance(other, BoxCage):
            raise TypeError
        xmin = min(self.bot.x, other.bot.x)
        ymin = min(self.bot.y, other.bot.y)
        xmax = max(self.top.x, other.top.x)
        ymax = max(self.top.y, other.top.y)
        return BoxCage((xmin, ymin), (xmax, ymax))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BoxCage):
            raise TypeError
        return self.bot == other.bot and self.top == other.top
