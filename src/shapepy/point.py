"""
File that contains only the Point2D object
"""
from __future__ import annotations

from fractions import Fraction
from typing import Tuple, Union

from .boolean import BoolNot
from .core import IBoolean2D, Math, Scalar


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

    def __new__(cls, *point: Union[Point2D, Tuple[Scalar, Scalar]]):
        if isinstance(point[0], cls):
            return point
        return super().__new__(cls)

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

    def inner(self, other: Union[Point2D, Tuple[Scalar, Scalar]]) -> Scalar:
        """
        Inner product between two points
        """
        if not isinstance(other, Point2D):
            other = self.__class__(other)
        return self[0] * other[0] + self[1] * other[1]

    def cross(self, other: Union[Point2D, Tuple[Scalar, Scalar]]) -> Scalar:
        """
        Cross product between two points
        """
        if not isinstance(other, Point2D):
            other = self.__class__(other)
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

    def __copy__(self) -> Point2D:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> Point2D:
        """Creates a deepcopy of the object"""
        return self.__class__(self.__x, self.__y)

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
        if not isinstance(other, Point2D):
            other = self.__class__(other)
        return max(abs(self[0] - other[0]), abs(self[1] - other[1])) < 1e-9

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


GeneralPoint = Union[Point2D, Tuple[Scalar, Scalar]]
