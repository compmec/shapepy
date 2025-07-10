"""
Module that defines the basic geometric classes used for the package

They are used to encapsulate some commands
"""

from __future__ import annotations

import fractions
import math
from typing import Tuple, Union

import numpy as np


class Point2D:
    """
    Defines a Point in the plane, that has 2 coordinates (x, y)
    """

    def __new__(cls, *point: Tuple[float]):
        if isinstance(point[0], cls):
            return point[0]
        return super().__new__(cls)

    def __init__(self, *point: Tuple[float]):
        x, y = point if len(point) == 2 else point[0]
        if isinstance(x, str) or isinstance(y, str):
            raise TypeError
        float(x)
        float(y)
        self._x = x
        self._y = y
        isxfrac = isinstance(x, (int, fractions.Fraction))
        isyfrac = isinstance(y, (int, fractions.Fraction))
        if isxfrac and isyfrac:
            self._x = fractions.Fraction(x).limit_denominator(1e9)
            self._y = fractions.Fraction(y).limit_denominator(1e9)

    def inner(self, other: Point2D) -> float:
        """
        Inner product between two points
        """
        assert isinstance(other, self.__class__)
        return self[0] * other[0] + self[1] * other[1]

    def cross(self, other: Point2D) -> float:
        """
        Cross product between two points
        """
        assert isinstance(other, self.__class__)
        return self[0] * other[1] - self[1] * other[0]

    def norm2(self) -> float:
        """
        Computes the L2 norm square = <point, point>
        """
        return self.inner(self)

    def __abs__(self) -> float:
        """
        The euclidean distance to origin
        """
        norm2 = self.inner(self)
        if not isinstance(norm2, (int, fractions.Fraction)):
            sqrt = math.sqrt(norm2)
            return int(sqrt) if int(sqrt) == sqrt else sqrt
        if isinstance(norm2, int):
            num, den = norm2, 1
        else:
            num, den = norm2.numerator, norm2.denominator
        sqrtnum = math.sqrt(num)
        sqrtnum = int(sqrtnum) if int(sqrtnum) ** 2 == num else sqrtnum
        sqrtden = math.sqrt(den)
        sqrtden = int(sqrtden) if int(sqrtden) ** 2 == den else sqrtden
        if isinstance(norm2, fractions.Fraction):
            return fractions.Fraction(sqrtnum) / sqrtden
        return sqrtnum / sqrtden

    def __copy__(self) -> Point2D:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> Point2D:
        """Creates a deepcopy of the object"""
        return self.__class__(self._x, self._y)

    def __iter__(self):
        yield self._x
        yield self._y

    def __getitem__(self, index: int):
        assert isinstance(index, int)
        assert index in {0, 1}
        return self._x if index == 0 else self._y

    def __str__(self) -> str:
        if isinstance(self._x, fractions.Fraction):
            xmsg = str(self._x.numerator)
            xmsg += (
                ""
                if (self._x.denominator == 1)
                else ("/" + str(self._x.denominator))
            )
        else:
            xmsg = str(self._x)
        if isinstance(self._y, fractions.Fraction):
            ymsg = str(self._y.numerator)
            ymsg += (
                ""
                if (self._y.denominator == 1)
                else ("/" + str(self._y.denominator))
            )
        else:
            ymsg = str(self._y)
        return f"({xmsg}, {ymsg})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: Point2D) -> bool:
        if not isinstance(other, Point2D):
            other = Point2D(other)
        if abs(self[0] - other[0]) > 1e-9:
            return False
        if abs(self[1] - other[1]) > 1e-9:
            return False
        return True

    def __neg__(self) -> Point2D:
        return self.__copy__().scale(-1, -1)

    def __iadd__(self, other: Point2D) -> Point2D:
        if not isinstance(other, Point2D):
            other = Point2D(other)
        return self.move(other)

    def __isub__(self, other: Point2D) -> Point2D:
        if not isinstance(other, Point2D):
            other = Point2D(other)
        return self.move(-other)

    def __imul__(self, other: float) -> Point2D:
        if isinstance(other, self.__class__):
            return self.inner(other)
        self._x *= other
        self._y *= other
        return self

    def __itruediv__(self, other: float) -> Point2D:
        self._x /= other
        self._y /= other
        return self

    def __add__(self, other: Point2D) -> Point2D:
        new = self.__copy__()
        new += other
        return new

    def __sub__(self, other: Point2D) -> Point2D:
        new = self.__copy__()
        new -= other
        return new

    def __mul__(self, other: float) -> Point2D:
        new = self.__copy__()
        new *= other
        return new

    def __rmul__(self, other: float) -> Point2D:
        return self.__mul__(other)

    def __truediv__(self, other: float) -> Point2D:
        new = self.__copy__()
        new /= other
        return new

    def __or__(self, other: Point2D) -> float:
        return self.inner(other)

    def __xor__(self, other: Point2D) -> float:
        return self.cross(other)

    def move(self, vector: Point2D) -> Point2D:
        """
        Moves the current point to another position
        Doesn't create a copy
        """
        self._x += vector[0]
        self._y += vector[1]
        return self

    def rotate(self, angle: float) -> Point2D:
        """
        Rotates the current point with respect to origin
        Doesn't create a copy
        """
        float(angle)
        cos, sin = np.cos(angle), np.sin(angle)
        new_x = cos * self._x - sin * self._y
        new_y = sin * self._x + cos * self._y
        self._x = new_x
        self._y = new_y
        return self

    def scale(self, xscale: float, yscale: float) -> Point2D:
        """
        Gives the new point (xscale * x0, yscale * y0)
        """
        float(xscale)
        float(yscale)
        self._x *= xscale
        self._y *= yscale
        return self


class Box:
    """
    Box class, which speeds up the evaluation of ``__contains__``
    in classes like ``PlanarCurve``, ``JordanCurve`` and ``SimpleShape``.

    Since it's faster to evaluate if a point is in a rectangle (this box),
    we avoid some computations like projecting the point on a curve and
    verifying if the distance is big enough to consider whether the point
    is the object

    """

    dx = 1e-6
    dy = 1e-6

    def __init__(self, lowpt: Point2D, toppt: Point2D):
        self.lowpt = lowpt
        self.toppt = toppt

    def __str__(self) -> str:
        return f"Box with vertices {self.lowpt} and {self.toppt}"

    def __bool__(self) -> bool:
        return True

    def __float__(self) -> float:
        """Returns the area of the box"""
        return (self.toppt[0] - self.lowpt[0]) * (
            self.toppt[1] - self.lowpt[1]
        )

    def __contains__(self, point: Point2D) -> bool:
        if point[0] < self.lowpt[0] - self.dx:
            return False
        if point[1] < self.lowpt[1] - self.dy:
            return False
        if self.toppt[0] + self.dx < point[0]:
            return False
        return not self.toppt[1] + self.dy < point[1]

    def __or__(self, other: Box) -> Box:
        xmin = min(self.lowpt[0], other.lowpt[0])
        ymin = min(self.lowpt[1], other.lowpt[1])
        xmax = max(self.toppt[0], other.toppt[0])
        ymax = max(self.toppt[1], other.toppt[1])
        return Box(Point2D(xmin, ymin), Point2D(xmax, ymax))

    def __ror__(self, other) -> Box:
        return self

    def __and__(self, other: Box) -> Union[Box, None]:
        xmin = max(self.lowpt[0], other.lowpt[0])
        xmax = min(self.toppt[0], other.toppt[0])
        if xmax < xmin:
            return None
        ymin = max(self.lowpt[1], other.lowpt[1])
        ymax = min(self.toppt[1], other.toppt[1])
        if ymax < ymin:
            return None
        return Box(Point2D(xmin, ymin), Point2D(xmax, ymax))
