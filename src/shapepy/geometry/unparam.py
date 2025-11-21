"""
Defines the class USegment and UPiecewise, which is equivalent to
"""

from __future__ import annotations

from copy import copy
from typing import Iterable, Iterator, Tuple, Union

from ..analytic.polynomial import Polynomial
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
        self.__segment = segment

    def __copy__(self) -> USegment:
        return self.__deepcopy__(None)

    def __deepcopy__(self, _) -> USegment:
        """Returns a deep copy of the jordan curve"""
        return self.__class__(copy(self.__segment))

    def __contains__(self, other) -> bool:
        return other in self.__segment

    def __invert__(self) -> USegment:
        """Invert the current curve's orientation, doesn't create a copy

        :return: The same curve
        :rtype: USegment
        """
        return USegment(~self.__segment)

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
        return segi(segi.knots[0]) == segj(segj.knots[0]) and segi(
            segi.knots[-1]
        ) == segj(segj.knots[-1])


class UPiecewiseCurve(IGeometricCurve):
    """Equivalent to PiecewiseCurve, but ignores the parametrization"""

    def __init__(self, usegments: Iterable[Union[Segment, USegment]]):
        self.__usegments = tuple(usegments)
        self.__piecewise = None

    @property
    def length(self) -> Real:
        """The length of the curve"""
        return sum(useg.length for useg in self)

    def __iter__(self) -> Iterator[Union[Segment, USegment]]:
        """Unparametrized Segments

        When setting, it checks if the points are the same between
        the junction of two segments to ensure a closed curve

        :getter: Returns the tuple of connected planar beziers, not copy
        :setter: Sets the segments of the jordan curve
        :type: tuple[Segment]

        Example use
        -----------

        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = FactoryJordan.polygon(vertices)
        >>> print(tuple(jordan))
        (Segment (deg 1), Segment (deg 1), Segment (deg 1))
        >>> print(tuple(jordan)[0])
        Planar curve of degree 1 and control points ((0, 0), (4, 0))

        """
        yield from (
            useg if Is.instance(useg, USegment) else USegment(useg)
            for useg in self.__usegments
        )

    def __len__(self) -> int:
        return len(self.__usegments)

    def __contains__(self, point: Point2D) -> bool:
        """Tells if the point is on the boundary"""
        return any(point in useg for useg in self)

    def box(self) -> Box:
        """The box which encloses the jordan curve

        :return: The box which encloses the jordan curve
        :rtype: Box

        Example use
        -----------

        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = FactoryJordan.polygon(vertices)
        >>> jordan.box()
        Box with vertices (0, 0) and (4, 3)

        """
        box = None
        for usegment in self:
            box |= usegment.box()
        return box

    def parametrize(self) -> PiecewiseCurve:
        """Gives a parametrized curve"""
        if self.__piecewise is None:
            newsegs = []
            for i, usegment in enumerate(self.__usegments):
                segment = usegment.parametrize()
                pointa = segment(segment.knots[0])
                pointb = segment(segment.knots[-1])
                composition = find_linear_composition(
                    segment.knots, [i, i + 1]
                )
                xfunc = segment.xfunc.compose(composition)
                yfunc = segment.yfunc.compose(composition)
                segment = Segment(xfunc, yfunc, domain=[i, i + 1])
                assert segment(segment.knots[0]) == pointa
                assert segment(segment.knots[-1]) == pointb
                newsegs.append(segment)
            self.__piecewise = PiecewiseCurve(newsegs)
        return self.__piecewise


def find_linear_composition(
    domain: Tuple[Real, Real], image: Tuple[Real, Real]
) -> Polynomial:
    """
    From a function f(x) defined in [a, b] (image),
    we want to find a linear function g(t) in the domain [c, d] such

    * h(t) = f(g(t))

    Therefore
        g(c) = a
        g(d) = b
    From hypothesis, g(t) = A + B * t
        A + B * c = a
        A + B * d = b
    Therefore
        B = (b-a)/(d-c)
        A = (a*d-c*b)/(d-c)
    """
    denom = 1 / (domain[1] - domain[0])
    const = denom * (image[0] * domain[1] - image[1] * domain[0])
    slope = denom * (image[1] - image[0])
    return Polynomial([const, slope])


def clean_usegment(usegment: USegment) -> USegment:
    """Cleans the segment, simplifying the expression"""
    return usegment


def self_intersect(usegment: USegment) -> USegment:
    """Checks if the USegment intersects itself"""
    seg = usegment.parametrize()
    return seg.xfunc.degree > 2 and seg.yfunc.degree > 2
