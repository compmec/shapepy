"""
Defines the most intuitive classes boolean classes:

* PointR2 - Only a single point on the plane
"""

from __future__ import annotations

from .. import default
from ..geometry import ContinuousCurve, GeometricPoint, geometric_point
from .base import EmptyR2, SubSetR2


class PointR2(SubSetR2):
    """
    Defines a SubSet of the entire plane that contains only one point.
    """

    def __init__(self, point: GeometricPoint):
        point = geometric_point(point)
        if not default.isfinite(point.radius):
            raise ValueError("Cannot receive an infinity point")
        self.__point = point

    @property
    def internal(self) -> GeometricPoint:
        """
        The Geometric Point that defines the Single Point
        """
        return self.__point

    def __str__(self) -> str:
        return "{" + str(self.internal) + "}"

    def __repr__(self):
        return f"PointR2({self.internal})"

    def __hash__(self):
        return hash((4, self.internal.x, self.internal.y))

    def __eq__(self, other):
        if isinstance(other, PointR2):
            return self.internal == other.internal
        return super().__eq__(other)

    def __contains__(self, other):
        if isinstance(other, SubSetR2):
            if isinstance(other, PointR2):
                return self.internal == other.internal
            return isinstance(other, EmptyR2)
        return super().__contains__(other)


class CurveR2(SubSetR2):
    """
    Class that defines a group of points that are inside the curve
    """

    def __init__(self, curve: ContinuousCurve):
        if not isinstance(curve, ContinuousCurve):
            raise TypeError
        self.__internal = curve

    @property
    def internal(self) -> ContinuousCurve:
        """
        Gives the geometric, continuous curve which is used
        to evaluate the points
        """
        return self.__internal

    def __str__(self):
        return "Curve"

    def __repr__(self):
        return "Curve"

    def __hash__(self):
        return hash(self.internal.lenght)
