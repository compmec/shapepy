"""
Defines the class USegment and UPiecewise, which is equivalent to
"""

from __future__ import annotations

from copy import copy
from typing import Iterable, Tuple, Union

from ..scalar.angle import Angle
from ..scalar.reals import Real
from ..tools import Is
from .base import IGeometricCurve
from .box import Box
from .piecewise import PiecewiseCurve
from .point import Point2D
from .segment import Segment


class USegment(IGeometricCurve):
    """Equivalent to Segment, but ignores the parametrization"""

    def __init__(self, segment: Segment):
        if not Is.instance(segment, Segment):
            raise TypeError(f"Expected {Segment}, not {type(segment)}")
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

    @property
    def start_point(self) -> Point2D:
        """Gives the start point of the USegment"""
        return self.__segment(0)

    @property
    def end_point(self) -> Point2D:
        """Gives the end point of the USegment"""
        return self.__segment(1)

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


class UPiecewiseCurve(IGeometricCurve):
    """Equivalent to PiecewiseCurve, but ignores the parametrization"""

    def __init__(self, usegments: Iterable[USegment]):
        self.__usegments = tuple(usegments)

    @property
    def length(self) -> Real:
        raise NotImplementedError

    def box(self) -> Box:
        raise NotImplementedError

    def parametrize(self) -> PiecewiseCurve:
        """Gives a parametrized curve"""
        return PiecewiseCurve(useg.parametrize() for useg in self.__usegments)


def clean_usegment(usegment: USegment) -> USegment:
    """Cleans the segment, simplifying the expression"""
    return usegment


def self_intersect(usegment: USegment) -> USegment:
    """Checks if the USegment intersects itself"""
    seg = usegment.parametrize()
    return seg.xfunc.degree > 2 and seg.yfunc.degree > 2
