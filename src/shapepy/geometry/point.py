"""
Module that defines the basic geometric classes used for the package

They are used to encapsulate some commands
"""

from __future__ import annotations

from ..scalar.angle import Angle
from ..scalar.reals import Math, Real
from ..tools import Is, To

TOLERANCE = 1e-9


class Point2D:
    """
    Defines a Point in the plane, that has 2 coordinates (x, y)
    """

    def __init__(self, x: Real, y: Real):
        self.__x = To.real(x)
        self.__y = To.real(y)

    def __copy__(self) -> Point2D:
        return +self

    def __deepcopy__(self, memo) -> Point2D:
        """Creates a deepcopy of the object"""
        return self.__class__(self.__x, self.__y)

    def __iter__(self):
        yield self.__x
        yield self.__y

    def __getitem__(self, index: int) -> Real:
        return self.__x if index == 0 else self.__y

    def __str__(self) -> str:
        return f"({self[0]}, {self[1]})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: Point2D) -> bool:
        return (
            abs(self[0] - other[0]) < TOLERANCE
            and abs(self[1] - other[1]) < TOLERANCE
        )

    def __neg__(self) -> Point2D:
        return self.__class__(-self[0], -self[1])

    def __pos__(self) -> Point2D:
        return self.__class__(self[0], self[1])

    def __iadd__(self, other: Point2D) -> Point2D:
        return self.move(other)

    def __add__(self, other: Point2D) -> Point2D:
        other = To.point(other)
        return self.__class__(self[0] + other[0], self[1] + other[1])

    def __sub__(self, other: Point2D) -> Point2D:
        other = To.point(other)
        return self.__class__(self[0] - other[0], self[1] - other[1])

    def __mul__(self, other: float) -> Point2D:
        if Is.point(other):
            return self.__matmul__(other)
        if not Is.finite(other):
            raise TypeError(f"Multiplication with non-real number: {other}")
        return self.__class__(self[0] * other, self[1] * other)

    def __rmul__(self, other: float) -> Point2D:
        return self.__mul__(other)

    def __matmul__(self, other: Point2D) -> float:
        other = To.point(other)
        return self[0] * other[0] + self[1] * other[1]

    def __xor__(self, other: Point2D) -> float:
        if not Is.point(other):
            raise TypeError(f"Cross product with non-Point2D object: {other}")
        return self[0] * other[1] - self[1] * other[0]

    def __abs__(self) -> float:
        """Returns the norm of the point, the distance to the origin"""
        return Math.sqrt(self @ self)

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
        self.__x += vector[0]
        self.__y += vector[1]
        return self

    def scale(self, xscale: float, yscale: float) -> Point2D:
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
        self.__x *= xscale
        self.__y *= yscale
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
        self.__x = x_new
        self.__y = y_new
        return self


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
    return Point2D(point[0], point[1])


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
