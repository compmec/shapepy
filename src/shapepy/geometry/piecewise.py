"""
Defines the piecewise curve class
"""

from __future__ import annotations

from typing import Iterable, Tuple, Union

from ..scalar.reals import Real
from ..tools import Is, To
from .base import IGeometricCurve
from .box import Box
from .point import Point2D
from .segment import Segment, clean_segment


class PiecewiseCurve(IGeometricCurve):
    """
    Defines a piecewise curve that is the concatenation of several segments.
    """

    def __init__(
        self,
        segments: Iterable[Segment],
        knots: Union[None, Iterable[Real]] = None,
    ):
        segments = tuple(segments)
        if not all(map(Is.segment, segments)):
            raise ValueError("All segments must be instances of Segment")
        if knots is None:
            knots = tuple(map(To.rational, range(len(segments) + 1)))
        else:
            knots = tuple(sorted(map(To.real, knots)))
        self.__segments = segments
        self.__knots = knots

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

    def span(self, node: Real) -> Union[int, None]:
        """
        Finds the index of the node
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

    def __call__(self, node: float) -> Point2D:
        index = self.span(node)
        if index is None:
            raise ValueError(f"Node {node} is out of bounds")
        knota, knotb = self.knots[index], self.knots[index + 1]
        unitparam = (node - knota) / (knotb - knota)
        return self[index](unitparam)

    def __contains__(self, point: Point2D) -> bool:
        """Tells if the point is on the boundary"""
        return any(point in bezier for bezier in self)


def clean_piecewise(piecewise: PiecewiseCurve) -> PiecewiseCurve:
    """
    Cleans the piecewise curve, keeping the current parametrisation
    """
    return PiecewiseCurve(map(clean_segment, piecewise))


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
