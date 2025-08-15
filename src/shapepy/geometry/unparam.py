"""
Defines the class USegment and UPiecewise, which is equivalent to
"""

from __future__ import annotations

from copy import copy
from typing import Tuple, Union

from ..scalar.angle import Angle
from ..scalar.reals import Real
from ..tools import Is
from .base import IGeometricCurve
from .box import Box
from .piecewise import PiecewiseCurve
from .point import Point2D, cross
from .segment import Segment


class USegment(IGeometricCurve):
    """Equivalent to Segment, but ignores the parametrization"""

    def __init__(self, segment: Segment):
        self.__segment = segment

    def __copy__(self) -> USegment:
        return self.__deepcopy__(None)

    def __deepcopy__(self, _) -> USegment:
        """Returns a deep copy of the jordan curve"""
        return self.__class__(copy(self.__segment))

    def __contains__(self, other) -> bool:
        return other in self.__segment

    @property
    def length(self) -> Real:
        """
        The length of the curve
        If the curve is not bounded, returns infinity
        """
        return self.__segment.length

    def box(self) -> Box:
        """
        Gives the box that encloses the curve
        """
        return self.__segment.box()

    def parametrize(self) -> Segment:
        """Gives a parametrized curve"""
        return self.__segment

    def __eq__(self, other: IGeometricCurve) -> bool:
        if not Is.instance(other, IGeometricCurve):
            raise TypeError
        segi = self.parametrize()
        segj = other.parametrize()
        return segi(0) == segj(0) and segi(1) == segj(1)

    def __or__(self, other: USegment) -> Union[USegment, PiecewiseCurve]:
        if not Is.instance(other, USegment):
            raise TypeError
        segi = self.parametrize()
        segj = other.parametrize()
        if segi(1) != segj(0):
            raise ValueError("Union is not continous")
        if segi.npts == 2 and segj.npts == 2:
            # They are linear
            if abs(cross(segi(1, 1), segj(0, 1))) < 1e-9:
                return USegment(
                    Segment([segi.ctrlpoints[0], segj.ctrlpoints[1]])
                )
        return PiecewiseCurve([segi, segj])

    def invert(self) -> USegment:
        """Invert the current curve's orientation, doesn't create a copy

        :return: The same curve
        :rtype: USegment
        """
        self.__segment = self.__segment.invert()
        return self

    def move(self, vector: Point2D) -> Segment:
        self.__segment.move(vector)
        return self

    def scale(self, amount: Union[Real, Tuple[Real, Real]]) -> Segment:
        self.__segment.scale(amount)
        return self

    def rotate(self, angle: Angle) -> Segment:
        self.__segment.rotate(angle)
        return self


def clean_usegment(usegment: USegment) -> USegment:
    """Cleans the segment, simplifying the expression"""
    return usegment


def self_intersect(usegment: USegment) -> USegment:
    """Checks if the USegment intersects itself"""
    return len(usegment.parametrize().ctrlpoints) > 3
