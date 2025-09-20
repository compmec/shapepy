"""
Defines a SinglePoint class, that represents a SubSet of the plane
that contains only one point on the plane
"""

from __future__ import annotations

from copy import copy
from typing import Tuple, Union

from ..geometry.point import Point2D
from ..loggers import debug
from ..scalar.angle import Angle
from ..scalar.reals import Real
from ..tools import Is, To
from .base import SubSetR2
from .density import Density


class SinglePoint(SubSetR2):
    """
    SinglePoint class

    Is a shape which is defined by only one jordan curve.
    It represents the interior/exterior region of the jordan curve
    if the jordan curve is counter-clockwise/clockwise

    """

    def __init__(self, point: Point2D):
        point = To.point(point)
        if Is.infinity(point.radius):
            raise ValueError("Must be a finite point")
        self.__point = point

    @property
    def internal(self) -> Point2D:
        """Gives the geometric point that defines the SinglePoint SubSetR2"""
        return self.__point

    def __copy__(self) -> SinglePoint:
        return SinglePoint(self.internal)

    def __deepcopy__(self, memo) -> SinglePoint:
        return SinglePoint(copy(self.__point))

    def __str__(self) -> str:  # pragma: no cover  # For debug
        return "{" + str(self.__point) + "}"

    def __eq__(self, other: SubSetR2) -> bool:
        """Compare two subsets

        Parameters
        ----------
        other: SubSetR2
            The shape to compare

        :raises ValueError: If ``other`` is not a SubSetR2 instance
        """
        if not Is.instance(other, SubSetR2):
            raise ValueError
        return (
            Is.instance(other, SinglePoint) and self.internal == other.internal
        )

    @debug("shapepy.bool2d.shape")
    def __hash__(self):
        return hash((self.internal.xcoord, self.internal.ycoord))

    def move(self, vector: Point2D) -> SinglePoint:
        self.__point = self.__point.move(vector)
        return self

    def scale(self, amount: Union[Real, Tuple[Real, Real]]) -> SinglePoint:
        self.__point = self.__point.scale(amount)
        return self

    def rotate(self, angle: Angle) -> SinglePoint:
        self.__point = self.__point.rotate(angle)
        return self

    def density(self, center: Point2D) -> Density:
        return Density.zero
