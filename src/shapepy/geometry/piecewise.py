"""
Defines the piecewise curve class
"""

from __future__ import annotations

from typing import Iterable, Iterator, Tuple, Union

from ..loggers import debug
from ..rbool import IntervalR1, WholeR1, from_any
from ..scalar.reals import Real
from ..tools import Is, pairs
from .base import IParametrizedCurve
from .box import Box
from .point import Point2D
from .segment import Segment


class PiecewiseCurve(IParametrizedCurve):
    """
    Defines a piecewise curve that is the concatenation of several segments.
    """

    def __init__(self, segments: Iterable[Segment]):
        segments = tuple(segments)
        if not all(Is.instance(seg, Segment) for seg in segments):
            raise ValueError("All segments must be instances of Segment")
        knots = list(segments[0].knots)
        for segi, segj in pairs(segments):
            knots.append(segj.knots[-1])
            if segi.knots[-1] != segj.knots[0]:
                raise ValueError(
                    f"{segi.domain} and {segj.domain} not consecutive"
                )
            pointa = segi(segi.knots[-1])
            pointb = segj(segj.knots[0])
            if pointa != pointb:
                raise ValueError(
                    f"{segi} not continuous with {segj}: {pointa} != {pointb}"
                )
        self.__domain = IntervalR1(knots[0], knots[-1])
        self.__segments = segments
        self.__knots = tuple(knots)

    def __str__(self):
        return r"{" + ", ".join(map(str, self)) + r"}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other: PiecewiseCurve):
        return (
            Is.instance(other, PiecewiseCurve)
            and self.length == other.length
            and self.knots == other.knots
            and tuple(self) == tuple(other)
        )

    @property
    def domain(self):
        return self.__domain

    @property
    def knots(self) -> Tuple[Real, ...]:
        return self.__knots

    @property
    def length(self) -> Real:
        """
        Gets the length of the curve
        """
        return sum(seg.length for seg in self)

    def __iter__(self) -> Iterator[Segment]:
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
        if node not in self.domain:
            raise ValueError(f"Node {node} is not in {self.domain}")
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

    def eval(self, node: float, derivate: int = 0) -> Point2D:
        return self[self.span(node)].eval(node, derivate)

    def __contains__(self, point: Point2D) -> bool:
        """Tells if the point is on the boundary"""
        return any(point in bezier for bezier in self)

    @debug("shapepy.geometry.piecewise")
    def section(
        self, domain: Union[IntervalR1, WholeR1]
    ) -> Union[Segment, PiecewiseCurve]:
        domain = from_any(domain)
        if domain not in self.domain:
            raise ValueError(f"Invalid {domain} not in {self.domain}")
        newsegs = []
        for segmenti in self.__segments:
            inter = segmenti.domain & domain
            if Is.instance(inter, (IntervalR1, WholeR1)):
                newsegs.append(segmenti.section(inter))
        return newsegs[0] if len(newsegs) == 1 else PiecewiseCurve(newsegs)
