"""
Defines the piecewise curve class
"""

from __future__ import annotations

from typing import Iterable, List, Tuple, Union

from ..loggers import debug, get_logger
from ..rbool import IntervalR1, infimum, supremum
from ..scalar.angle import Angle
from ..scalar.reals import Real
from ..tools import Is, NotContinousError, To, vectorize
from .base import IParametrizedCurve
from .box import Box
from .point import Point2D
from .segment import Segment


class PiecewiseCurve(IParametrizedCurve):
    """
    Defines a piecewise curve that is the concatenation of several segments.
    """

    def __init__(
        self,
        segments: Iterable[Segment],
        knots: Union[None, Iterable[Real]] = None,
    ):
        segments = tuple(segments)
        if not all(Is.instance(seg, Segment) for seg in segments):
            raise ValueError("All segments must be instances of Segment")
        if knots is None:
            knots = tuple(map(To.rational, range(len(segments) + 1)))
        else:
            knots = tuple(sorted(map(To.finite, knots)))
        for segi, segj in zip(segments, segments[1:]):
            if segi(1) != segj(0):
                raise NotContinousError(f"{segi(1)} != {segj(0)}")
        self.__segments: Tuple[Segment, ...] = segments
        self.__knots: Tuple[Segment, ...] = knots

    def __str__(self):
        msgs = []
        for i, segmenti in enumerate(self.__segments):
            interval = [self.knots[i], self.knots[i + 1]]
            msg = f"{interval}: {segmenti}"
            msgs.append(msg)
        return r"{" + ", ".join(msgs) + r"}"

    @property
    def knots(self) -> Tuple[Real]:
        """
        Get the knots of the piecewise curve.
        """
        return self.__knots

    @property
    def length(self) -> Real:
        """
        Gets the length of the curve
        """
        return sum(seg.length for seg in self)

    def __iter__(self):
        yield from self.__segments

    def __getitem__(self, index: int) -> Segment:
        """
        Get the segment at the specified index.
        """
        return self.__segments[index]

    def __len__(self) -> int:
        """
        Get the number of segments in the piecewise curve.
        """
        return len(self.__segments)

    @debug("shapepy.geometry.piecewise")
    def span(self, node: Real) -> Union[int, None]:
        """
        Finds the index of the node

        Example
        -------
        >>> piecewise.knots
        (0, 1, 5, 6, 7)
        >>> piecewise.span(0)
        0  # It's inside [0, 1)
        >>> piecewise.span(1)
        1  # It's inside [1, 5)
        >>> piecewise.span(2)
        1  # It's inside [1, 5)
        """
        if not Is.real(node):
            raise ValueError
        if node < self.knots[0] or self.knots[-1] < node:
            return None
        for i, knot in enumerate(self.knots[1:]):
            if node < knot:
                return i
        return len(self.__segments) - 1

    def box(self) -> Box:
        """The box which encloses the piecewise curve

        :return: The box which encloses the piecewise curve
        :rtype: Box
        """
        box = None
        for bezier in self:
            box |= bezier.box()
        return box

    @vectorize(1, 0)
    def __call__(self, node: float, derivate: int = 0) -> Point2D:
        index = self.span(node)
        if index is None:
            raise ValueError(f"Node {node} is out of bounds")
        knota, knotb = self.knots[index], self.knots[index + 1]
        unitparam = (node - knota) / (knotb - knota)
        segment = self[index]
        return segment(unitparam, derivate)

    def __contains__(self, point: Point2D) -> bool:
        """Tells if the point is on the boundary"""
        return any(point in bezier for bezier in self)

    def move(self, vector: Point2D) -> PiecewiseCurve:
        vector = To.point(vector)
        self.__segments = tuple(seg.move(vector) for seg in self)
        return self

    def scale(self, amount: Union[Real, Tuple[Real, Real]]) -> Segment:
        self.__segments = tuple(seg.scale(amount) for seg in self)
        return self

    def rotate(self, angle: Angle) -> Segment:
        angle = To.angle(angle)
        self.__segments = tuple(seg.rotate(angle) for seg in self)
        return self

    @debug("shapepy.geometry.piecewise")
    def section(self, subset: IntervalR1) -> PiecewiseCurve:
        logger = get_logger("shapepy.geometry.piecewise")
        segments = tuple(self.__segments)
        knots = tuple(self.knots)
        if subset == [self.knots[0], self.knots[-1]]:
            return self
        knota, knotb = infimum(subset), supremum(subset)
        spana, spanb = self.span(knota), self.span(knotb)
        logger.info(f"current knots = {knots}")
        logger.info(f"knota, knotb = {[knota, knotb]}")
        logger.info(f"spana, spanb = {[spana, spanb]}")
        if spana == spanb:
            return segments[spana].section([knota, knotb])
        newsegs: List[Segment] = []
        if knota != knots[spana]:
            interval = [knota, knots[spana]]
            segment = segments[spana].section(interval)
            newsegs.append(segment)
        else:
            newsegs.append(segments[spana])
        newsegs += list(segments[spana + 1 : spanb])
        if knotb != knots[spanb]:
            interval = [knots[spanb], knotb]
            segment = segments[spanb].section(interval)
            newsegs.append(segment)
        newknots = sorted({knota, knotb} | set(knots[spana:spanb]))
        logger.info(f"new knots = {newknots}")
        logger.info(f"len(news) = {len(newsegs)}")
        return PiecewiseCurve(newsegs, newknots)


def is_piecewise(obj: object) -> bool:
    """
    Checks if the parameter is a Piecewise curve

    Parameters
    ----------
    obj : The object to be tested

    Returns
    -------
    bool
        True if the obj is a PiecewiseCurve, False otherwise
    """
    return Is.instance(obj, PiecewiseCurve)


Is.piecewise = is_piecewise
