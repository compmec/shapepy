from __future__ import annotations

import math
from typing import Tuple, Union

from .core import IObject2D, Scalar


class Point2D(IObject2D):

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

        3.0 * xcoord + 4 * ycoord - 5  # Verify if they are scalars
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
        return self.inner(self)

    def __abs__(self) -> Scalar:
        """
        The euclidean distance to origin
        """
        return math.sqrt(self.inner(self))

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
            try:
                other = tuple(other)
                other = self.__class__(other)
            except Exception:
                return False
        return max(abs(self[0] - other[0]), abs(self[1] - other[1])) < 1e-9

    def __neg__(self) -> Point2D:
        return self.__copy__().scale(-1, -1)

    def __add__(self, other: Union[Point2D, Tuple[Scalar, Scalar]]) -> Point2D:
        if not isinstance(other, Point2D):
            other = self.__class__(other)
        return self.__class__((self[0] + other[0], self[1] + other[1]))

    def __sub__(self, other: Union[Point2D, Tuple[Scalar, Scalar]]) -> Point2D:
        if not isinstance(other, Point2D):
            other = self.__class__(other)
        return self.__class__((self[0] - other[0], self[1] - other[1]))

    def __mul__(self, other: float) -> Point2D:
        float(other)
        return self.__class__((other * self[0], other * self[1]))

    def __rmul__(self, other: float) -> Point2D:
        return self.__mul__(other)

    def __truediv__(self, other: float) -> Point2D:
        float(other)
        return self.__class__((self[0] / other, self[1] / other))

    def move(self, vector: Union[Point2D, Tuple[Scalar, Scalar]]) -> Point2D:
        """
        Moves the current point to another position
        """
        return self + vector

    def rotate(self, angle: Scalar) -> Point2D:
        """
        Rotates the current point with respect to origin
        """
        float(angle)
        cos, sin = math.cos(angle), math.sin(angle)
        new_x = cos * self.__x - sin * self.__y
        new_y = sin * self.__x + cos * self.__y
        return self.__class__((new_x, new_y))

    def scale(self, xscale: Scalar, yscale: Scalar) -> Point2D:
        float(xscale)
        float(yscale)
        return self.__class__((xscale * self[0], yscale * self[1]))


GeneralPoint = Union[Point2D, Tuple[Scalar, Scalar]]
