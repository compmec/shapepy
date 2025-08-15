"""
This modules contains a powerful class called JordanCurve which
is in fact, stores a list of spline-curves.
"""

from __future__ import annotations

from collections import deque
from copy import copy
from typing import Deque, Iterable, Tuple, Union

from ..scalar.angle import Angle
from ..scalar.reals import Real
from ..tools import Is, pairs, reverse
from .base import IGeometricCurve
from .box import Box
from .piecewise import PiecewiseCurve
from .point import Point2D
from .unparam import USegment, clean_usegment, self_intersect


class JordanCurve(IGeometricCurve):
    """
    Jordan Curve is an arbitrary closed curve which doesn't intersect itself.
    It stores a list of 'segments', each segment is a bezier curve
    """

    def __init__(self, usegments: Iterable[USegment]):
        self.__area = None
        self.usegments = usegments

    def __copy__(self) -> JordanCurve:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> JordanCurve:
        """Returns a deep copy of the jordan curve"""
        return self.__class__(map(copy, self.usegments))

    def move(self, vector: Point2D) -> JordanCurve:
        self.__piecewise = self.piecewise.move(vector)
        return self

    def scale(self, amount: Union[Real, Tuple[Real, Real]]) -> JordanCurve:
        self.__piecewise = self.piecewise.scale(amount)
        return self

    def rotate(self, angle: Angle) -> JordanCurve:
        self.__piecewise = self.piecewise.rotate(angle)
        return self

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
        for usegment in self.usegments:
            box |= usegment.box()
        return box

    @property
    def length(self) -> Real:
        """The length of the curve"""
        return self.piecewise.length

    @property
    def area(self) -> Real:
        """The internal area"""
        if self.__area is None:
            self.__area = compute_area(self)
        return self.__area

    def parametrize(self) -> PiecewiseCurve:
        """
        Gives the piecewise curve
        """
        return self.piecewise

    @property
    def piecewise(self) -> PiecewiseCurve:
        """
        Gives the piecewise curve
        """
        return self.__piecewise

    @property
    def usegments(self) -> Deque[USegment]:
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
        >>> print(jordan.usegments)
        (Segment (deg 1), Segment (deg 1), Segment (deg 1))
        >>> print(jordan.usegments[0])
        Planar curve of degree 1 and control points ((0, 0), (4, 0))

        """
        return deque(map(USegment, self.parametrize()))

    @property
    def vertices(self) -> Tuple[Point2D]:
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
        vertices = []
        for usegment in self.usegments:
            segment = usegment.parametrize()
            vertex = segment(segment.knots[0])
            vertices.append(vertex)
        return tuple(vertices)

    @usegments.setter
    def usegments(self, other: Iterable[USegment]):
        usegments = tuple(other)
        if not all(Is.instance(u, USegment) for u in usegments):
            raise ValueError(f"Invalid usegments: {tuple(map(type, other))}")
        if any(map(self_intersect, usegments)):
            raise ValueError("Segment must not self intersect")
        segments = [useg.parametrize() for useg in usegments]
        for segi, segj in pairs(segments):
            if segi(1) != segj(0):
                raise ValueError("The segments are not continuous")
        self.__piecewise = PiecewiseCurve(segments)
        self.__area = None

    def __str__(self) -> str:
        msg = (
            f"Jordan Curve with {len(self.usegments)} segments and vertices\n"
        )
        msg += str(self.vertices)
        return msg

    def __repr__(self) -> str:
        box = self.box()
        return f"JC[{len(self.usegments)}:{box.lowpt},{box.toppt}]"

    def __eq__(self, other: JordanCurve) -> bool:
        if not Is.jordan(other):
            raise ValueError
        if (
            self.box() != other.box()
            or self.length != other.length
            or not all(point in self for point in other.vertices)
        ):
            return False
        susegs = copy(self).clean().usegments
        ousegs = copy(other).clean().usegments
        for _ in range(len(susegs)):
            if susegs == ousegs:
                return True
            susegs.rotate()
        return False

    def invert(self) -> JordanCurve:
        """Invert the current curve's orientation, doesn't create a copy

        :return: The same curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> from matplotlib import pyplot as plt
        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = FactoryJordan.polygon(vertices)
        >>> jordan.invert([0, 2], [1/2, 2/3])
        Jordan Curve of degree 1 and vertices
        ((0, 0), (0, 3), (4, 0))
        >>> print(jordan)
        Jordan Curve of degree 1 and vertices
        ((0, 0), (0, 3), (4, 0))

        """
        self.usegments = reverse(useg.invert() for useg in self.usegments)
        return self

    def clean(self) -> JordanCurve:
        """Cleans the jordan curve"""
        usegments = list(map(clean_usegment, self.usegments))
        index = 0
        while index + 1 < len(usegments):
            union = usegments[index] | usegments[index + 1]
            if not Is.instance(union, USegment):
                index += 1
            else:
                usegments.pop(index)
                usegments[index] = union
        while len(usegments) > 1:
            union = usegments[-1] | usegments[0]
            if not Is.instance(union, USegment):
                break
            usegments.pop(0)
            usegments[-1] = union
        self.usegments = usegments
        return self

    def __invert__(self) -> JordanCurve:
        return copy(self).invert()

    def __contains__(self, point: Point2D) -> bool:
        """Tells if the point is on the boundary"""
        return point in self.piecewise


def compute_area(jordan: JordanCurve) -> Real:
    """
    Computes the area inside of the jordan curve

    If jordan is clockwise, then the area is negative
    """
    total = 0
    for usegment in jordan.usegments:
        segment = usegment.parametrize()
        xfunc = segment.xfunc
        yfunc = segment.yfunc
        poly = xfunc * yfunc.derivate() - yfunc * xfunc.derivate()
        assert Is.analytic(poly)
        ipoly = poly.integrate()
        total += ipoly(1) - ipoly(0)
    return total / 2


def get_ctrlpoints(jordan: JordanCurve) -> Iterable[Point2D]:
    """Gets the control points of the jordan curve"""
    vertices = {}
    for usegment in jordan.usegments:
        segment = usegment.parametrize()
        for ctrlpt in segment.ctrlpoints:
            vertices[id(ctrlpt)] = ctrlpt
    return vertices.values()


def clean_jordan(jordan: JordanCurve) -> JordanCurve:
    """Cleans the jordan curve

    Removes the uncessary nodes from jordan curve,
    for example, after calling ``split`` function

    :return: The same curve
    :rtype: JordanCurve

    Example use
    -----------

    >>> from shapepy import JordanCurve
    >>> vertices = [(0, 0), (1, 0), (4, 0), (0, 3)]
    >>> jordan = FactoryJordan.polygon(vertices)
    >>> jordan.clean()
    Jordan Curve of degree 1 and vertices
    ((0, 0), (4, 0), (0, 3))

    """
    usegments = deque(map(clean_usegment, jordan.usegments))
    for _ in range(len(usegments) + 1):
        union = usegments[0] | usegments[1]
        if Is.instance(union, USegment):
            usegments.popleft()
            usegments.popleft()
            usegments.appendleft(union)
        usegments.rotate()
    return JordanCurve(usegments)


def is_jordan(obj: object) -> bool:
    """
    Checks if the parameter is a Jordan Curve

    Parameters
    ----------
    obj : The object to be tested

    Returns
    -------
    bool
        True if the obj is a Jordan Curve, False otherwise
    """
    return Is.instance(obj, JordanCurve)


Is.jordan = is_jordan
