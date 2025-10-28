"""
Defines a SingleCurve class, that represents a SubSet of the plane
that contains a continous set of points on the plane
"""

from __future__ import annotations

from typing import Tuple, Union

from ..geometry.base import IGeometricCurve
from ..geometry.point import Point2D
from ..loggers import debug
from ..scalar.angle import Angle
from ..scalar.reals import Real
from ..tools import Is
from .base import SubSetR2
from .density import Density


class SingleCurve(SubSetR2):
    """SingleCurve class

    It represents a subset on the plane of continous points
    """

    def __init__(self, curve: IGeometricCurve):
        if not Is.instance(curve, IGeometricCurve):
            raise TypeError(f"Invalid: {type(curve)} != {IGeometricCurve}")
        self.__curve = curve

    @property
    def internal(self) -> IGeometricCurve:
        """Gives the geometric curve that defines the SingleCurve SubSetR2"""
        return self.__curve

    def __copy__(self) -> SingleCurve:
        return SingleCurve(self.internal)

    def __str__(self) -> str:  # pragma: no cover  # For debug
        return "{" + str(self.__curve) + "}"

    def __eq__(self, other: SubSetR2) -> bool:
        """Compare two subsets

        Parameters
        ----------
        other: SubSetR2
            The subset to compare

        :raises ValueError: If ``other`` is not a SubSetR2 instance
        """
        if not Is.instance(other, SubSetR2):
            raise ValueError
        return (
            Is.instance(other, SingleCurve) and self.internal == other.internal
        )

    @debug("shapepy.bool2d.curve")
    def __hash__(self):
        return hash(self.internal.length)

    def move(self, vector: Point2D) -> SingleCurve:
        return SingleCurve(self.__curve.move(vector))

    def scale(self, amount: Union[Real, Tuple[Real, Real]]) -> SingleCurve:
        return SingleCurve(self.__curve.scale(amount))

    def rotate(self, angle: Angle) -> SingleCurve:
        return SingleCurve(self.__curve.rotate(angle))

    def density(self, center: Point2D) -> Density:
        return Density.zero
