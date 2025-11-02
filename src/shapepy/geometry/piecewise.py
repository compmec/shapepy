"""
Defines the piecewise curve class
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Tuple, Union

from ..loggers import debug
from ..rbool import SubSetR1, create_interval
from ..scalar.reals import Real
from ..tools import Is, To, pairs, vectorize
from .base import IParametrizedCurve
from .box import Box
from .point import Point2D
from .segment import Segment


class PiecewiseCurve(IParametrizedCurve):
    """
    Defines a piecewise curve that is the concatenation of several segments.
    """

    def __init__(self, segments: Iterable[Segment]):
        segments: Tuple[Segment, ...] = tuple(segments)
        if not all(Is.instance(seg, Segment) for seg in segments):
            raise ValueError("All segments must be instances of Segment")

        for segi, segj in pairs(segments):
            if segi.knots[-1] != segj.knots[0]:
                raise ValueError(f"{segi.domain} =|= {segj.domain}")
            knot = segi.knots[-1]
            if segi(knot) != segj(knot):
                raise ValueError(f"Not Continuous curve at {knot}")
        knots = list(seg.knots[0] for seg in segments)
        knots.append(segments[-1].knots[-1])
        self.__segments = segments
        self.__knots = tuple(knots)
        self.__domain = create_interval(knots[0], knots[-1])

    def __str__(self):
        msgs = []
        for i, segmenti in enumerate(self.__segments):
            interval = [self.knots[i], self.knots[i + 1]]
            msg = f"{interval}: {segmenti}"
            msgs.append(msg)
        return r"{" + ", ".join(msgs) + r"}"

    @property
    def domain(self) -> SubSetR1:
        return self.__domain

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

    def split(self, nodes: Iterable[Real]) -> None:
        """
        Creates an opening in the piecewise curve

        Example
        >>> piecewise.knots
        (0, 1, 2, 3)
        >>> piecewise.snap([0.5, 1.2])
        >>> piecewise.knots
        (0, 0.5, 1, 1.2, 2, 3)
        """
        nodes = set(map(To.finite, nodes)) - set(self.knots)
        spansnodes = defaultdict(set)
        for node in nodes:
            span = self.span(node)
            if span is not None:
                spansnodes[span].add(node)
        if len(spansnodes) == 0:
            return
        newsegments = []
        for i, segmenti in enumerate(self):
            if i not in spansnodes:
                newsegments.append(segmenti)
                continue
            knota, knotb = self.knots[i], self.knots[i + 1]
            unit_nodes = (
                (knot - knota) / (knotb - knota) for knot in spansnodes[i]
            )
            newsegments += list(segmenti.split(unit_nodes))
        self.__knots = tuple(sorted(list(self.knots) + list(nodes)))
        self.__segments = tuple(newsegments)

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
