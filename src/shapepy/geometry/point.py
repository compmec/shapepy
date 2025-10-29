"""
Module that defines the basic geometric classes used for the package

They are used to encapsulate some commands
"""

from __future__ import annotations

from typing import Tuple, Union

from ..loggers import debug
from ..scalar.angle import Angle, arg, degrees
from ..scalar.reals import Math, Real
from ..tools import Is, To

TOLERANCE = 1e-9


@debug("shapepy.geometry.point", maxdepth=0)
def cartesian(xcoord: Real, ycoord: Real) -> Point2D:
    """
    Creates a Point with cartesian coordinates
    """
    xcoord = To.real(xcoord)
    ycoord = To.real(ycoord)
    return Point2D(xcoord, ycoord, None, None)


@debug("shapepy.geometry.point", maxdepth=0)
def polar(radius: Real, angle: Angle) -> Point2D:
    """
    Creates a Point with polar coordinates
    """
    radius = To.real(radius)
    angle = degrees(0) if radius == 0 else To.angle(angle)
    return Point2D(None, None, radius, angle)


class Point2D:
    """
    Defines a Point in the plane,

    It can be described in cartesian way: (x, y)
    Or also in a polar way: (radius:angle)
    """

    def __init__(
        self,
        xcoord: Real = None,
        ycoord: Real = None,
        radius: Real = None,
        angle: Angle = None,
    ):
        self.__xcoord = xcoord
        self.__ycoord = ycoord
        self.__radius = radius
        self.__angle = angle

    @property
    def xcoord(self) -> Real:
        """The horizontal coordinate of the point"""
        if self.__xcoord is None:
            cos = self.__angle.cos()
            self.__xcoord = self.__radius * cos if cos != 0 else To.finite(0)
        return self.__xcoord

    @property
    def ycoord(self) -> Real:
        """The vertical coordinate of the point"""
        if self.__ycoord is None:
            sin = self.__angle.sin()
            self.__ycoord = self.__radius * sin if sin != 0 else To.finite(0)
        return self.__ycoord

    @property
    def radius(self) -> Real:
        """The norm L2 of the point: sqrt(x*x + y*y)"""
        if self.__radius is None:
            self.__radius = Math.sqrt(self.__xcoord**2 + self.__ycoord**2)
        return self.__radius

    @property
    def angle(self) -> Angle:
        """The angle the point (x, y) forms with respect to the horizontal"""
        if self.__angle is None:
            self.__angle = arg(self.__xcoord, self.__ycoord)
        return self.__angle

    def __copy__(self) -> Point2D:
        return +self

    def __iter__(self):
        yield self.__xcoord
        yield self.__ycoord

    def __getitem__(self, index: int) -> Real:
        return self.__xcoord if index == 0 else self.__ycoord

    def __str__(self) -> str:
        return (
            f"({self.xcoord}, {self.ycoord})"
            if Is.finite(self.radius)
            else f"({self.radius}:{self.angle})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: Point2D) -> bool:
        return (
            abs(self[0] - other[0]) < TOLERANCE
            and abs(self[1] - other[1]) < TOLERANCE
        )

    def __neg__(self) -> Point2D:
        return self.__class__(
            -1 * self.xcoord,
            -1 * self.ycoord,
            self.radius,
            self.angle.__invert__(),
        )

    def __pos__(self) -> Point2D:
        return self.__class__(
            self.xcoord, self.ycoord, self.radius, self.angle
        )

    def __add__(self, other: Point2D) -> Point2D:
        other = To.point(other)
        return cartesian(self[0] + other[0], self[1] + other[1])

    def __sub__(self, other: Point2D) -> Point2D:
        other = To.point(other)
        return cartesian(self[0] - other[0], self[1] - other[1])

    def __mul__(self, other: float) -> Point2D:
        if not Is.finite(other):
            raise TypeError(f"Multiplication with non-real number: {other}")
        return cartesian(other * self.xcoord, other * self.ycoord)

    def __rmul__(self, other: float) -> Point2D:
        return self.__mul__(other)

    def __abs__(self) -> float:
        """Returns the norm of the point, the distance to the origin"""
        return self.radius


def move(point: Point2D, vector: tuple[Real, Real]) -> Point2D:
    """
    Moves the point by the given deltas

    Parameters
    ----------
    dx : float
        The delta to move the x coordinate
    dy : float
        The delta to move the y coordinate

    Returns
    -------
    Point2D
        The moved point
    """
    vector = To.point(vector)
    return cartesian(point.xcoord + vector[0], point.ycoord + vector[1])


def scale(point: Point2D, amount: Union[Real, Tuple[Real, Real]]) -> Point2D:
    """
    Scales the point by the given factors

    Parameters
    ----------
    xscale : float
        The factor to scale the x coordinate
    yscale : float
        The factor to scale the y coordinate

    Returns
    -------
    Point2D
        The scaled point
    """
    xscale, yscale = (amount, amount) if Is.real(amount) else amount
    return cartesian(xscale * point.xcoord, yscale * point.ycoord)


def rotate(point: Point2D, angle: Angle) -> Point2D:
    """
    Rotates the point around the origin by the given angle

    Parameters
    ----------
    angle : float
        The angle in radians to rotate the point

    Returns
    -------
    Point2D
        The rotated point
    """
    angle = To.angle(angle)
    sin, cos = angle.sin(), angle.cos()
    newx = cos * point.xcoord - sin * point.ycoord
    newy = sin * point.xcoord + cos * point.ycoord
    return cartesian(newx, newy)


def inner(pointa: Point2D, pointb: Point2D) -> Real:
    """Compute the cross product between two points"""
    return pointa.xcoord * pointb.xcoord + pointa.ycoord * pointb.ycoord


def cross(pointa: Point2D, pointb: Point2D) -> Real:
    """Compute the cross product between two points"""
    return pointa.xcoord * pointb.ycoord - pointa.ycoord * pointb.xcoord


def to_point(point: Point2D | tuple[Real, Real]) -> Point2D:
    """
    Converts a point to a Point2D object

    Parameters
    ----------
    point : Point2D or tuple of two reals
        The point to be converted

    Returns
    -------
    Point2D
        The converted point
    """
    if Is.instance(point, Point2D):
        return point
    xcoord = To.finite(point[0])
    ycoord = To.finite(point[1])
    return cartesian(xcoord, ycoord)


To.point = to_point
