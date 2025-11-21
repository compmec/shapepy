"""
This modules contains a powerful class called JordanCurve which
is in fact, stores a list of spline-curves.
"""

from __future__ import annotations

from collections import deque
from typing import Iterable, Iterator, List, Union

from ..analytic import IAnalytic
from ..loggers import debug, get_logger
from ..scalar.reals import Real
from ..tools import CyclicContainer, Is, pairs, reverse
from .base import Future
from .point import Point2D, cross
from .segment import Segment
from .unparam import UPiecewiseCurve, USegment, self_intersect


class JordanCurve(UPiecewiseCurve):
    """
    Jordan Curve is an arbitrary closed curve which doesn't intersect itself.
    It stores a list of 'segments', each segment is a bezier curve
    """

    def __init__(self, usegments: Iterable[Union[Segment, USegment]]):
        super().__init__(clean_jordan(usegments))
        for usegi in self:
            if self_intersect(usegi):
                raise ValueError(f"Segment self-intersect! {usegi}")
        self.__area = None

    @property
    def area(self) -> Real:
        """The internal area"""
        if self.__area is None:
            self.__area = compute_area(self)
        return self.__area

    def vertices(self) -> Iterator[Point2D]:
        """Vertices

        Returns in order, all the non-repeted control points from
        jordan curve's segments

        :getter: Returns a tuple of
        :type: Tuple[Point2D]

        Example use
        -----------

        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = FactoryJordan.polygon(vertices)
        >>> print(jordan.vertices)
        ((0, 0), (4, 0), (0, 3))

        """
        for useg in self:
            seg = useg.parametrize()
            yield seg.eval(seg.knots[0])

    def __str__(self) -> str:
        msg = f"Jordan Curve with {len(self)} segments and vertices\n"
        msg += str(self.vertices())
        return msg

    def __repr__(self) -> str:
        box = self.box()
        return f"JC[{len(self)}:{box.lowpt},{box.toppt}]"

    def __eq__(self, other: JordanCurve) -> bool:
        logger = get_logger("shapepy.geometry.jordancurve")
        logger.debug(f"     type: {type(other)}")
        logger.debug(f"     box: {self.box() == other.box()}")
        logger.debug(f"     len: {self.length == other.length}")
        logger.debug(f"    area: {self.area == other.area}")
        logger.debug(
            f"    all1: {all(point in self for point in other.vertices())}"
        )
        logger.debug(
            f"    all2: {all(point in other for point in self.vertices())}"
        )
        logger.debug(
            f"    cycl: {CyclicContainer(self) == CyclicContainer(other)}"
        )
        return (
            Is.instance(other, JordanCurve)
            and self.box() == other.box()
            and self.length == other.length
            and self.area == other.area
            and all(point in self for point in other.vertices())
            and all(point in other for point in self.vertices())
            and CyclicContainer(self) == CyclicContainer(other)
        )

    def __invert__(self) -> JordanCurve:
        return JordanCurve(reverse(~useg for useg in self))


@debug("shapepy.geometry.jordancurve")
def compute_area(jordan: JordanCurve) -> Real:
    """
    Computes the area inside of the jordan curve

    If jordan is clockwise, then the area is negative
    """
    total = 0
    for usegment in jordan:
        segment = usegment.parametrize()
        xfunc = segment.xfunc
        yfunc = segment.yfunc
        poly = xfunc * yfunc.derivate()
        poly -= yfunc * xfunc.derivate()
        assert Is.instance(poly, IAnalytic)
        total += poly.integrate(segment.domain)
    return total / 2


@debug("shapepy.geometry.jordan")
def clean_jordan(
    usegments: Iterable[Union[Segment, USegment]]
) -> Iterator[Union[Segment, USegment]]:
    """Cleans the jordan curve

    Removes the uncessary nodes from jordan curve

    :return: The set of segments
    :rtype: A set of segments

    Example use
    -----------

    >>> from shapepy import JordanCurve
    >>> vertices = [(0, 0), (1, 0), (4, 0), (0, 3)]
    >>> jordan = FactoryJordan.polygon(vertices)
    >>> jordan.clean()
    Jordan Curve of degree 1 and vertices
    ((0, 0), (4, 0), (0, 3))

    """
    logger = get_logger("shapepy.geometry.jordan")
    logger.debug("Segments = ")
    usegments = deque(usegments)
    endvectors = []
    for i, usegment in enumerate(usegments):
        if not Is.instance(usegment, (Segment, USegment)):
            raise ValueError
        segment = usegment.parametrize()
        logger.debug(f"    {i}: {segment}")
        vectora = segment.eval(segment.knots[0], 1)
        vectorb = segment.eval(segment.knots[-1], 1)
        endvectors.append((vectora, vectorb))
    crosses: List[Real] = []
    for (_, vectb), (vecta, _) in pairs(endvectors, cyclic=True):
        crosses.append(cross(vectb, vecta))
    logger.debug(f"End vectors = {endvectors}")
    logger.debug(f"Crosses = {crosses}")
    if not any(c == 0 for c in crosses):
        return usegments
    index = len(crosses) - 1
    while index > 0 and crosses[index] == 0:
        usegments.rotate()
        index -= 1
    usegments = Future.concatenate(usegments)
    return usegments
