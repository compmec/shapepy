"""
Module that defines the basic geometric classes used for the package

They are used to encapsulate some commands
"""

from __future__ import annotations

from typing import Tuple, Union

from ..scalar.angle import Angle
from ..scalar.reals import Math, Real
from ..tools import Is, To

TOLERANCE = 1e-9


def cartesian(xcoord: Real, ycoord: Real) -> Point2D:
    """
    Creates a Point with cartesian coordinates
    """
    xcoord = To.real(xcoord)
    ycoord = To.real(ycoord)
    return Point2D(xcoord, ycoord, None, None)


def polar(radius: Real, angle: Angle) -> Point2D:
    """
    Creates a Point with polar coordinates
    """
    radius = To.real(radius)
    angle = Angle.degrees(0) if radius == 0 else To.angle(angle)
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
            self.__angle = Angle.arg(self.__xcoord, self.__ycoord)
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
            -self.xcoord,
            -self.ycoord,
            self.radius,
            self.angle + Angle.degrees(180),
        )

    def __pos__(self) -> Point2D:
        return self.__class__(
            self.xcoord, self.ycoord, self.radius, self.angle
        )

    def __iadd__(self, other: Point2D) -> Point2D:
        return self.move(other)

    def __add__(self, other: Point2D) -> Point2D:
        other = To.point(other)
        return cartesian(self[0] + other[0], self[1] + other[1])

    def __sub__(self, other: Point2D) -> Point2D:
        other = To.point(other)
        return cartesian(self[0] - other[0], self[1] - other[1])

    def __mul__(self, other: float) -> Point2D:
        if Is.point(other):
            return inner(self, other)
        if not Is.finite(other):
            raise TypeError(f"Multiplication with non-real number: {other}")
        return cartesian(self[0] * other, self[1] * other)

    def __rmul__(self, other: float) -> Point2D:
        return self.__mul__(other)

    def __abs__(self) -> float:
        """Returns the norm of the point, the distance to the origin"""
        return self.radius

    def move(self, vector: tuple[Real, Real]) -> Point2D:
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
        self.__xcoord += vector[0]
        self.__ycoord += vector[1]
        return self

    def scale(self, amount: Union[Real, Tuple[Real, Real]]) -> Point2D:
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
        self.__xcoord *= xscale
        self.__ycoord *= yscale
        return self

    def rotate(self, angle: Angle) -> Point2D:
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
        cos_angle = angle.cos()
        sin_angle = angle.sin()
        x_new = self[0] * cos_angle - self[1] * sin_angle
        y_new = self[0] * sin_angle + self[1] * cos_angle
        self.__xcoord = x_new
        self.__ycoord = y_new
        return self


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


def is_point(point: Point2D | tuple[Real, Real]) -> bool:
    """
    Checks if the given point is a Point2D object or a tuple of two reals

    Parameters
    ----------
    point : Point2D or tuple of two reals
        The point to be checked

    Returns
    -------
    bool
        True if the point is a Point2D or a tuple of two reals, False otherwise
    """
    return Is.instance(point, Point2D) or (
        Is.instance(point, tuple)
        and len(point) == 2
        and all(Is.finite(coord) for coord in point)
    )


To.point = to_point
Is.point = is_point
