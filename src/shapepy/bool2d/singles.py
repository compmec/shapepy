"""
Defines the most intuitive classes boolean classes:

* PointR2 - Only a single point on the plane
"""

from __future__ import annotations

from numbers import Real

from .. import default
from ..geometry import (
    ContinuousCurve,
    GeometricPoint,
    JordanCurve,
    geometric_point,
    reverse,
)
from .base import EmptyR2, SubSetR2, WholeR2
from .container import ContainerNot


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


class ShapeR2(SubSetR2):
    """
    Class that defines a closed region on the plane.

    It's defined by a jordan curve, which is the boundary of it
    The flag boundary means if the Shape actually includes its
    boundary or if it's an open set
    """

    def __init__(self, jordan: JordanCurve, boundary: bool = True):
        if not isinstance(jordan, JordanCurve):
            raise TypeError
        self.__jordan = jordan
        self.__boundary = bool(boundary)

    @property
    def internal(self) -> JordanCurve:
        """
        The jordan curve that defines the boundary of the simple shape
        """
        return self.__jordan

    @property
    def boundary(self) -> bool:
        """
        A flag that tells if the shape includes the boundary or not
        """
        return self.__boundary

    @property
    def area(self) -> Real:
        """
        Gives the internal area defined by the jordan curve

        * The area is positive if the jordan curve is counter-clockwise
        * otherwise, it's negative but with the same magnitude
        """
        return self.internal.area

    # pylint: disable=too-many-return-statements
    def __contains__(self, other: object) -> bool:
        if isinstance(other, SubSetR2):
            if isinstance(other, PointR2):
                return other.internal in self
            if isinstance(other, EmptyR2):
                return True
            if isinstance(other, WholeR2):
                return False
            if isinstance(other, CurveR2):
                raise NotImplementedError
            if isinstance(other, ShapeR2):
                raise NotImplementedError
            if isinstance(other, ContainerNot):
                # pylint: disable=superfluous-parens
                return (-self) in (~other)
            return super().__contains__(other)
        if isinstance(other, GeometricPoint):
            wind = self.internal.winding(other)
            return wind > 0 if self.boundary else wind == 1
        return super().__contains__(other)

    def __neg__(self):
        return ShapeR2(reverse(self.internal), not self.boundary)

    def __hash__(self):
        return hash(self.area) if self.area > 0 else (-hash(-self.area))
