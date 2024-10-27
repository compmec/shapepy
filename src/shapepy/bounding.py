"""
This file contains two classes that helps evaluating if a point
is inside a given shape.

Basicaly if there's a curve in the plane, that is limited,
then there's a convex shape that contains this curve.

It's easier to check if a point is inside a convex shape than
for a random shape.
The two easiest convex shapes that can be created are the
rectangle and a circle, that are defined inside this file
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Union

from .core import Empty, IObject2D, Scalar, Whole
from .point import GeneralPoint, Point2D


class BoundObject(IObject2D):
    """
    Base bounding object, that speed up evaluation of `__contains__`
    """

    @abstractmethod
    def winding(self, point: GeneralPoint) -> Scalar:
        """
        Computes the winding number

        Parameters
        ----------
        point : Point2D
            The point to evaluate

        :return: The winding value
        :rtype: float
        """
        raise NotImplementedError

    def __contains__(self, point: GeneralPoint) -> bool:
        return 0 < self.winding(point)


class BoundRectangle(BoundObject):
    """
    Rectangle version of Bounding Object
    """

    def __init__(self, lowpt: GeneralPoint, toppt: GeneralPoint):
        if not isinstance(lowpt, Point2D):
            lowpt = Point2D(lowpt)
        if not isinstance(toppt, Point2D):
            toppt = Point2D(toppt)
        if toppt[0] <= lowpt[0] or toppt[1] <= lowpt[1]:
            raise ValueError
        self.lowpt = lowpt
        self.toppt = toppt

    def __str__(self) -> str:
        xmin, xmax = self.lowpt[0], self.toppt[0]
        ymin, ymax = self.lowpt[1], self.toppt[1]
        return f"Box[{xmin}, {xmax}]x[{ymin}, {ymax}]"

    def __repr__(self) -> str:
        return self.__str__()

    def winding(self, point: GeneralPoint) -> Scalar:
        if not isinstance(point, Point2D):
            point = Point2D(point)
        if point[0] < self.lowpt[0] or point[1] < self.lowpt[1]:
            return 0
        if self.toppt[0] < point[0] or self.toppt[1] < point[1]:
            return 0
        left = point[0] == self.lowpt[0]
        righ = point[0] == self.toppt[0]
        bott = point[1] == self.lowpt[1]
        topp = point[1] == self.toppt[1]
        if not (left or righ or bott or topp):
            return 1
        return 0.25 if (left or righ) and (bott or topp) else 0.5

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BoundRectangle):
            return False
        return self.lowpt == other.lowpt and self.toppt == other.toppt

    def __or__(self, other: object) -> Union[Whole, BoundRectangle]:
        if not isinstance(other, BoundRectangle):
            raise TypeError
        minx = min(self.lowpt[0], other.lowpt[0])
        miny = min(self.lowpt[1], other.lowpt[1])
        maxx = max(self.toppt[0], other.toppt[0])
        maxy = max(self.toppt[1], other.toppt[1])
        return self.__class__((minx, miny), (maxx, maxy))

    def __and__(self, other: object) -> Union[Empty, BoundRectangle]:
        if not isinstance(other, BoundRectangle):
            raise TypeError
        minx = max(self.lowpt[0], other.lowpt[0])
        miny = max(self.lowpt[1], other.lowpt[1])
        maxx = min(self.toppt[0], other.toppt[0])
        maxy = min(self.toppt[1], other.toppt[1])
        if maxx <= minx or maxy <= miny:
            return Empty()
        return self.__class__((minx, miny), (maxx, maxy))


class BoundCircle(BoundObject):
    """
    Circle version of Bounding Object
    """

    def __init__(self, center: GeneralPoint, radius: Scalar):
        if not isinstance(center, Point2D):
            center = Point2D(center)
        if radius <= 0:
            raise ValueError
        self.center = center
        self.radius = radius

    def __str__(self) -> str:
        return f"Circle[{self.radius}, {self.center}]"

    def __repr__(self) -> str:
        return self.__str__()

    def winding(self, point: GeneralPoint) -> Scalar:
        if not isinstance(point, Point2D):
            point = Point2D(point)
        diff = (point - self.center).norm2() - self.radius**2
        return 0 if diff > 0 else 1 if diff < 0 else 0.5

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BoundCircle):
            return False
        return self.center == other.center and self.radius == other.radius

    def __or__(self, other: object) -> Union[Whole, BoundCircle]:
        if not isinstance(other, BoundCircle):
            raise TypeError
        if self.center == other.center:
            new_radius = max(self.radius, other.radius)
            return self.__class__(self.center, new_radius)
        raise NotImplementedError

    def __and__(self, other: object) -> Union[Empty, BoundCircle]:
        if not isinstance(other, BoundCircle):
            raise TypeError
        if self.center == other.center:
            new_radius = min(self.radius, other.radius)
            return self.__class__(self.center, new_radius)
        raise NotImplementedError
