"""
Defines the class GeometricPoint that stores a point on the plane.
It stores the values (x, y, radius, angle), which are related.
"""

from __future__ import annotations

from numbers import Real
from typing import Any

from .. import default
from ..angle import Angle, to_angle


def any2point(obj: Any) -> GeometricPoint:
    """
    Transforms a point to a GeometricPoint if it's not already

    Parameters
    ----------
    point: Any
        -

    Return
    ------
    GeometricPoint
        The point

    Example
    -------
    >>> point = any2point((0, 0))
    >>> point
    (0, 0)
    >>> type(point)
    <class "shapepy.geometry.GeometricPoint">
    """
    if isinstance(obj, GeometricPoint):
        return obj
    xcoord = default.finite(obj[0])
    ycoord = default.finite(obj[1])
    return cartesian(xcoord, ycoord)


def str2point(text: str) -> GeometricPoint:
    """
    Converts a string into a Geometric Point
    """
    if not isinstance(text, str):
        raise TypeError
    text = text.strip()
    if text[0] != "(" or text[-1] != ")":
        raise ValueError(f"Invalid string: {text}")
    if "," in text:
        items = tuple(sub.strip() for sub in text[1:-1].split(","))
        if len(items) != 2:
            raise ValueError(f"Invalid convert to point: '{text}' -> {items}")
        return cartesian(items[0], items[1])
    raise NotImplementedError


def cartesian(x: Real, y: Real) -> GeometricPoint:
    """
    Creates an GeometricPoint instance from given cartesian coordinates

    Parameters
    ----------
    x: Real
        The x coordinate, the abscissa value
    y: Real
        The y coordinate, the ordinate value

    Return
    ------
    GeometricPoint
        The created point from given cartesian coordinates
    """
    x = default.real(x)
    y = default.real(y)
    radius = default.hypot(x, y)
    angle = Angle.arg(x, y)
    return GeometricPoint(x, y, radius, angle)


def polar(radius: Real, angle: Angle) -> GeometricPoint:
    """
    Creates an GeometricPoint instance from given polar coordinates

    Parameters
    ----------
    radius: Real
        Distance from the origin
    angle: Angle
        The angle between the point and the positive x-axis

    Return
    ------
    GeometricPoint
        The created point from given polar coordinates
    """
    angle = to_angle(angle)
    sinval, cosval = angle.sin(), angle.cos()
    if radius < 0:
        raise ValueError(f"Cannot have radius = {radius} < 0")
    x = default.finite(0) if cosval == 0 else radius * cosval
    y = default.finite(0) if sinval == 0 else radius * sinval
    return GeometricPoint(x, y, radius, angle)


class GeometricPoint:
    """
    Defines a geometric point to store the values of
    the xcoord, ycoord, radius and angle

    It's intended to be returned by the evaluation of the ContinuousCurve
    """

    def __init__(self, x: Real, y: Real, radius: Real, angle: Angle):
        self.__x = x
        self.__y = y
        self.__radius = radius
        self.__angle = to_angle(angle)

    @property
    def x(self) -> Real:
        """
        The first coordinate of the point

        :getter: Returns the first coordinate of the point
        :type: Real
        """
        return self.__x

    @property
    def y(self) -> Real:
        """
        The second coordinate of the point

        :getter: Returns the first coordinate of the point
        :type: Real
        """
        return self.__y

    @property
    def radius(self) -> Real:
        """
        The euclidian distance between the origin and the point

        :getter: Returns the L2 norm of the point
        :type: Real
        """
        return self.__radius

    @property
    def angle(self) -> Angle:
        """
        The angle measured from the x-axis

        :getter: Returns the angle of the point
        :type: Angle
        """
        return self.__angle

    def __str__(self) -> str:
        return (
            f"({self.x}, {self.y})"
            if default.isfinite(self.radius)
            else f"({self.radius}:{self.angle})"
        )

    def __repr__(self):
        return "GeomPt" + str(self)

    def __eq__(self, other: object):
        if isinstance(other, GeometricPoint):
            return self.x == other.x and self.y == other.y
        return NotImplemented


def inner(pointa: GeometricPoint, pointb: GeometricPoint) -> Real:
    """
    Computes the inner product between two points

    Parameters
    ----------
    pointa: GeometricPoint
        The point A to compute <A, B>
    pointb: GeometricPoint
        The point B to compute <A, B>

    Return
    ------
    Real
        The value of the inner product

    Example
    -------
    >>> pointa = (3, 4)
    >>> pointb = (5, 2)
    >>> inner(pointa, pointb)
    23
    """
    pointa = any2point(pointa)
    pointb = any2point(pointb)
    return pointa.x * pointb.x + pointa.y * pointb.y


def cross(pointa: GeometricPoint, pointb: GeometricPoint) -> Real:
    """
    Computes the cross product between two points

    Parameters
    ----------
    pointa: GeometricPoint
        The point A to compute A x B
    pointb: GeometricPoint
        The point B to compute A x B

    Return
    ------
    Real
        The value of the cross product

    Example
    -------
    >>> pointa = (3, 4)
    >>> pointb = (5, 2)
    >>> cross(pointa, pointb)
    -14
    """
    pointa = any2point(pointa)
    pointb = any2point(pointb)
    return pointa.x * pointb.y - pointa.y * pointb.x
