"""
Defines the most intuitive classes boolean classes:

* SinglePointR2 - Only a single point on the plane
"""

from __future__ import annotations

from .. import default
from ..geometry import GeometricPoint, geometric_point
from .base import EmptyR2, SubSetR2


class SinglePointR2(SubSetR2):
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
        return f"SinglePointR2({self.internal})"

    def __hash__(self):
        return hash((4, self.internal.x, self.internal.y))

    def __eq__(self, other):
        if isinstance(other, SinglePointR2):
            return self.internal == other.internal
        return super().__eq__(other)

    def __contains__(self, other):
        if isinstance(other, SubSetR2):
            if isinstance(other, SinglePointR2):
                return self.internal == other.internal
            return isinstance(other, EmptyR2)
        return super().__contains__(other)
