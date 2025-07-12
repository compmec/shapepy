"""
Cage class for geometric operations.
This class is used to speed up the evaluation of point containment
"""

from __future__ import annotations

from typing import Union

from .point import Point2D


class Cage:
    """
    Cage class, which speeds up the evaluation of ``__contains__``
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
        return f"Cage with vertices {self.lowpt} and {self.toppt}"

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

    def __or__(self, other: Cage) -> Cage:
        xmin = min(self.lowpt[0], other.lowpt[0])
        ymin = min(self.lowpt[1], other.lowpt[1])
        xmax = max(self.toppt[0], other.toppt[0])
        ymax = max(self.toppt[1], other.toppt[1])
        return Cage(Point2D(xmin, ymin), Point2D(xmax, ymax))

    def __ror__(self, other) -> Cage:
        return self

    def __and__(self, other: Cage) -> Union[Cage, None]:
        xmin = max(self.lowpt[0], other.lowpt[0])
        xmax = min(self.toppt[0], other.toppt[0])
        if xmax < xmin:
            return None
        ymin = max(self.lowpt[1], other.lowpt[1])
        ymax = min(self.toppt[1], other.toppt[1])
        if ymax < ymin:
            return None
        return Cage(Point2D(xmin, ymin), Point2D(xmax, ymax))
