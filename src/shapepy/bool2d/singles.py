"""
Defines the most intuitive classes boolean classes:

* PointR2 - Only a single point on the plane
"""

from __future__ import annotations

from numbers import Real

from .. import default
from ..error import NotExpectedError
from ..geometry.abc import IContinuousCurve, IJordanCurve
from ..geometry.point import GeometricPoint, any2point
from ..geometry.transform import reverse
from .base import EmptyR2, SubSetR2, WholeR2
from .container import ContainerAnd, ContainerNot, ContainerOr


class PointR2(SubSetR2):
    """
    Defines a SubSet of the entire plane that contains only one point.
    """

    def __init__(self, point: GeometricPoint):
        point = any2point(point)
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

    def __init__(self, curve: IContinuousCurve):
        if not isinstance(curve, IContinuousCurve):
            raise TypeError
        self.__internal = curve

    @property
    def internal(self) -> IContinuousCurve:
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

    def __init__(self, jordan: IJordanCurve, boundary: bool = True):
        if not isinstance(jordan, IJordanCurve):
            raise TypeError
        self.__jordan = jordan
        self.__boundary = bool(boundary)

    @property
    def internal(self) -> IJordanCurve:
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
                return self.__contains_geompoint(other.internal)
            if isinstance(other, EmptyR2):
                return True
            if isinstance(other, WholeR2):
                return False
            if isinstance(other, CurveR2):
                return self.__contains_geomcurve(other.internal)
            if isinstance(other, ShapeR2):
                return self.__contains_shape(other)
            if isinstance(other, ContainerNot):
                # pylint: disable=superfluous-parens
                return (-self) in (~other)
            if isinstance(other, ContainerOr):
                return all(sub in self for sub in other)
            if isinstance(other, ContainerAnd):
                return False  # Not possible evaluate yet
            raise NotExpectedError(f"Should not arrive here: {type(other)}")
        if isinstance(other, GeometricPoint):
            return self.__contains_geompoint(other)
        if isinstance(other, IContinuousCurve):
            return self.__contains_geomcurve(other)
        return super().__contains__(other)

    def __neg__(self):
        return ShapeR2(reverse(self.internal), not self.boundary)

    def __hash__(self):
        return hash(self.area) if self.area > 0 else (-hash(-self.area))

    def __contains_geompoint(self, other: GeometricPoint) -> bool:
        """
        Private method to checks if given point is inside the shape.
        """
        wind = self.internal.winding(other)
        return wind > 0 if self.boundary else wind == 1

    def __contains_geomcurve(self, other: IContinuousCurve) -> bool:
        """
        Private method to checks if given curve is inside the shape.

        This function is not intelligent: It just samples the curve
        and checks if every point is inside the shape
        """
        raise NotImplementedError

    # pylint: disable=chained-comparison
    def __contains_shape(self, other: ShapeR2) -> bool:
        """
        Private method to checks if given shape is inside this shape
        """
        if self.area > 0 and other.area < 0:
            # Bounded shape cannot contains unbounded shape
            return False
        # pylint: disable=superfluous-parens
        if not (self.internal.cage & other.internal.cage):
            # The boxes are disjoint, so the jordans don't intersect
            return self.area < 0 and other.area > 0
        if self.area < 0 and other.area > 0:
            # Unbounded shape contains bounded shape if
            return other.internal in self and self.internal not in other
        raise NotImplementedError
