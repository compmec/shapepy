"""
File that contains only the Point2D object
"""
from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Tuple, Union

from .analytic.utils import usincos
from .boolean import BoolNot
from .core import Empty, IBoolean2D, Math, Scalar


def treat_scalar(number: Scalar) -> Scalar:
    """
    Treats and checks the scalar number received
    """
    if isinstance(number, int):
        return Fraction(number)
    if isinstance(number, (float, Fraction)):
        return number
    if isinstance(number, str):
        raise TypeError
    # pylint: disable=pointless-statement
    3.2 * number + 4
    return number


class Point2D(IBoolean2D):
    """
    Class that describes a cartesian point.

    It contains methods like inner, cross, norm2
    """

    @property
    def ndim(self) -> int:
        return 0

    def __init__(self, *point: Union[Point2D, Tuple[Scalar, Scalar]]):
        if len(point) == 2:
            xcoord, ycoord = point
        elif len(point) == 1 and len(point[0]) == 2:
            xcoord, ycoord = point[0]
        else:
            raise ValueError
        xcoord = treat_scalar(xcoord)
        ycoord = treat_scalar(ycoord)
        self.__x = xcoord
        self.__y = ycoord

    def move(self, vector: GeneralPoint) -> Point2D:
        """
        Moves the object in the plane by the given vector

        Parameters
        ----------
        vector: Point
            The pair (x, y) that must be added to the coordinates

        Example
        -------
        >>> mypoint = Point(0, 0)
        >>> mypoint.move((1, 2))
        (1, 2)
        """
        return self.__class__(self[0] + vector[0], self[1] + vector[1])

    def scale(self, xscale: Scalar, yscale: Scalar) -> Point2D:
        """
        Scales the object in the X and Y directions

        Parameters
        ----------
        xscale: Scalar
            The amount to be scaled in the X direction
        yscale: Scalar
            The amount to be scaled in the Y direction

        Example
        -------
        >>> mypoint = Point(2, 3)
        >>> mypoint.scale(5, 3)
        (10, 9)
        """
        return self.__class__(xscale * self[0], yscale * self[1])

    def rotate(self, uangle: Scalar) -> Point2D:
        """
        Rotates the point around the origin.

        The angle mesure is unitary:
        * angle = 1 means 360 degrees rotation
        * angle = 0.5 means 180 degrees rotation
        * angle = 0.125 means 45 degrees rotation

        Parameters
        ----------
        angle: Scalar
            The unitary angle the be rotated.

        Example
        -------
        >>> mypoint = Point(2, 3)
        >>> mypoint.rotate(180/360)  # 180 degrees
        (-2, -3)
        >>> mypoint.rotate(90/360)
        (-3, 2)
        """
        sin, cos = usincos(uangle)
        newx = self[0] * cos - self[1] * sin
        newy = self[0] * sin + self[1] * cos
        return self.__class__(newx, newy)

    def inner(self, other: Union[Point2D, Tuple[Scalar, Scalar]]) -> Scalar:
        """
        Inner product between two points
        """
        return self[0] * other[0] + self[1] * other[1]

    def cross(self, other: Union[Point2D, Tuple[Scalar, Scalar]]) -> Scalar:
        """
        Cross product between two points
        """
        return self[0] * other[1] - self[1] * other[0]

    def norm2(self) -> Scalar:
        """
        Computes the square of the norm L2 of the point.
        Meaning, the inner product between itself
        """
        return self.inner(self)

    def __abs__(self) -> Scalar:
        """
        The euclidean distance to origin
        """
        return Math.sqrt(self.inner(self))

    def __iter__(self):
        yield self.__x
        yield self.__y

    def __getitem__(self, index: int):
        index = int(index)
        return self.__x if index == 0 else self.__y

    def __str__(self) -> str:
        return f"({self.__x}, {self.__y})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        delx = abs(self[0] - other[0])
        dely = abs(self[1] - other[1])
        return max(delx, dely) < 1e-6

    def __add__(self, other: Union[Point2D, Tuple[Scalar, Scalar]]) -> Point2D:
        if not isinstance(other, Point2D):
            other = self.__class__(other)
        return self.__class__((self[0] + other[0], self[1] + other[1]))

    def __sub__(self, other: Union[Point2D, Tuple[Scalar, Scalar]]) -> Point2D:
        if not isinstance(other, Point2D):
            other = self.__class__(other)
        return self.__class__((self[0] - other[0], self[1] - other[1]))

    def __rmul__(self, other: float) -> Point2D:
        float(other)
        return self.__class__((other * self[0], other * self[1]))

    def __invert__(self) -> BoolNot:
        return BoolNot(self)

    def __contains__(self, other: IBoolean2D):
        if isinstance(other, Point2D):
            return other == self
        return super().__contains__(other)

    def __and__(self, other: IBoolean2D) -> IBoolean2D:
        return self if (self in other) else Empty()


GeneralPoint = Union[Point2D, Tuple[Scalar, Scalar]]


def treat_points(vertices: Iterable[GeneralPoint]) -> Iterable[Point2D]:
    """
    Converts points to Point2D instances
    """
    for vertex in vertices:
        yield vertex if isinstance(vertex, Point2D) else Point2D(vertex)
