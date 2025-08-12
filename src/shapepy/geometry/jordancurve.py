"""
This modules contains a powerful class called JordanCurve which
is in fact, stores a list of spline-curves.
"""

from __future__ import annotations

from copy import copy
from fractions import Fraction
from typing import Iterable, Optional, Tuple

import numpy as np

from ..scalar.reals import Real
from ..tools import Is, To
from .base import Future, IGeometricCurve
from .box import Box
from .piecewise import PiecewiseCurve, clean_piecewise
from .point import Point2D
from .segment import Segment, segment_self_intersect


class JordanCurve(IGeometricCurve):
    """
    Jordan Curve is an arbitrary closed curve which doesn't intersect itself.
    It stores a list of 'segments', each segment is a bezier curve
    """

    def __init__(self, segments: Iterable[Segment]):
        self.__area = None
        self.segments = segments

    def __copy__(self) -> JordanCurve:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> JordanCurve:
        """Returns a deep copy of the jordan curve"""
        segments = self.segments
        nsegments = len(segments)
        all_points = []
        for segment in segments:
            points = list(copy(point) for point in segment.ctrlpoints)
            all_points.append(points)
        for i, points in enumerate(all_points):
            j = (i + 1) % nsegments
            next_start_point = all_points[j][0]
            points[-1] = next_start_point
        new_segments = []
        for i, segment in enumerate(segments):
            points = all_points[i]
            new_segment = segment.__class__(points)
            new_segments.append(new_segment)
        return self.__class__(new_segments)

    def move(self, point: Point2D) -> JordanCurve:
        """Translate the entire curve by ``point``

        :param point: The translation amount
        :type point: Point2D
        :return: The same curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = FactoryJordan.polygon(vertices)
        >>> jordan.move((2, 3))
        Jordan Curve of degree 1 and vertices
        ((2, 3), (6, 3), (2, 6))

        """
        point = To.point(point)
        for vertex in self.vertices:
            vertex += point
        return self

    def scale(self, xscale: float, yscale: float) -> JordanCurve:
        """Scale the entire curve in horizontal and vertical direction

        :param xscale: The scale in horizontal direction
        :type xscale: float
        :param yscale: The scale in vertical direction
        :type yscale: float
        :return: The same curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = FactoryJordan.polygon(vertices)
        >>> jordan.scale(2, 3)
        Jordan Curve of degree 1 and vertices
        ((0, 0), (8, 0), (0, 9))
        >>> jordan.scale(1/2, 1/3)
        Jordan Curve of degree 1 and vertices
        ((0.0, 0.0), (4.0, 0.0), (0.0, 3.0))

        """
        float(xscale)
        float(yscale)
        for vertex in self.vertices:
            vertex.scale(xscale, yscale)
        return self

    def rotate(self, angle: float, degrees: bool = False) -> JordanCurve:
        """Rotate the entire curve around the origin

        :param angle: The amount to rotate
        :type angle: float
        :param degrees: If the angle is in radians (``degrees=False``)
        :type degrees: bool(, optional)
        :return: The same curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> import math
        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = FactoryJordan.polygon(vertices)
        >>> jordan.rotate(math.pi)
        Jordan Curve of degree 1 and vertices
        ((-0.0, 0.0), (-4.0, 4.899e-16), (-3.674e-16, -3.0))
        >>> jordan.rotate(180, degrees=True)
        Jordan Curve of degree 1 and vertices
        ((0.0, -0.0), (4.0, -9.797e-16), (7.348e-16, 3.0))

        """
        float(angle)
        if degrees:
            angle *= np.pi / 180
        for vertex in self.vertices:
            vertex.rotate(angle)
        return self

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
        segments = self.segments
        nsegs = len(segments)
        new_segments = []
        for i in range(nsegs - 1, -1, -1):
            new_segments.append(segments[i].invert())
        self.segments = tuple(new_segments)
        return self

    def points(self, subnpts: Optional[int] = None) -> Tuple[Tuple[float]]:
        """Return sample points in jordan curve for plotting curve

        You can choose the precision by changing the ```subnpts``` parameter

        * subnpts = 0 -> extremities

        * subnpts = 1 -> extremities and midpoint

        :param subnpts: The number of interior points
        :type subnpts: int(, optional)
        :return: Sampled points in jordan curve
        :rtype: tuple[tuple[float]]

        Example use
        -----------

        >>> from matplotlib import pyplot as plt
        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = FactoryJordan.polygon(vertices)
        >>> points = jordan.points(3)
        >>> xvals = [point[0] for point in points]
        >>> yvals = [point[1] for point in points]
        >>> plt.plot(xvals, yvals, marker="o")
        >>> plt.show()

        """
        assert subnpts is None or (Is.integer(subnpts) and subnpts >= 0)
        all_points = []
        for segment in self.segments:
            npts = (
                subnpts if subnpts is not None else 10 * (segment.degree - 1)
            )
            usample = tuple(Fraction(num, npts + 1) for num in range(npts + 1))
            points = segment(usample)
            all_points += list(tuple(point) for point in points)
        all_points.append(all_points[0])  # Close the curve
        return tuple(all_points)

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
        return self.piecewise.box()

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

    @property
    def piecewise(self) -> PiecewiseCurve:
        """
        Gives the piecewise curve
        """
        return self.__piecewise

    @property
    def segments(self) -> Tuple[Segment, ...]:
        """Segments

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
        >>> print(jordan.segments)
        (Segment (deg 1), Segment (deg 1), Segment (deg 1))
        >>> print(jordan.segments[0])
        Planar curve of degree 1 and control points ((0, 0), (4, 0))

        """
        return tuple(self.piecewise)

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
        ids = []
        vertices = []
        for segment in self.segments:
            for point in segment.ctrlpoints:
                if id(point) not in ids:
                    ids.append(id(point))
                    vertices.append(point)
        return tuple(vertices)

    @segments.setter
    def segments(self, other: Iterable[Segment]):
        piecewise = PiecewiseCurve(other)
        if not piecewise_is_closed(piecewise):
            raise ValueError(f"Given piecewise is not closed: {piecewise}")
        if piecewise_self_intersect(piecewise):
            raise ValueError
        self.__piecewise = clean_piecewise(piecewise)
        self.__area = None

    def __str__(self) -> str:
        max_degree = max(curve.degree for curve in self.segments)
        msg = f"Jordan Curve of degree {max_degree} and vertices\n"
        msg += str(self.vertices)
        return msg

    def __repr__(self) -> str:
        max_degree = max(curve.degree for curve in self.segments)
        msg = "JordanCurve (deg %d, nsegs %d)"
        msg %= max_degree, len(self.segments)
        return msg

    def __eq__(self, other: JordanCurve) -> bool:
        if not Is.jordan(other):
            raise ValueError
        for point in other.points(1):
            if point not in self:
                return False
        selcopy = clean_jordan(self.__copy__())
        othcopy = clean_jordan(other.__copy__())
        if len(selcopy.segments) != len(othcopy.segments):
            return False
        segment1 = othcopy.segments[0]
        for index, segment0 in enumerate(selcopy.segments):
            if segment0 == segment1:
                break
        else:
            return False
        nsegments = len(self.segments)
        for i, segment1 in enumerate(othcopy.segments):
            segment0 = selcopy.segments[(i + index) % nsegments]
            if segment0 != segment1:
                return False
        return True

    def __invert__(self) -> JordanCurve:
        return self.__copy__().invert()

    def __contains__(self, point: Point2D) -> bool:
        """Tells if the point is on the boundary"""
        return point in self.piecewise

    def __float__(self) -> float:
        """Returns the lenght of the curve

        If jordan curve is clockwise, then lenght < 0

        :getter: Returns the total lenght of the jordan curve
        :type: float

        Example use
        -----------

        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = FactoryJordan.polygon(vertices)
        >>> print(float(jordan))
        12.0
        >>> vertices = [(0, 0), (0, 3), (4, 0)]
        >>> jordan = FactoryJordan.polygon(vertices)
        >>> print(float(jordan))
        -12.0

        """
        return float(self.length if self.area > 0 else -self.length)


def compute_area(jordan: JordanCurve) -> Real:
    """
    Computes the area inside of the jordan curve

    If jordan is clockwise, then the area is negative
    """
    total = 0
    for segment in jordan.segments:
        xfunc = segment.xfunc
        yfunc = segment.yfunc
        poly = xfunc * yfunc.derivate() - yfunc * xfunc.derivate()
        assert Is.analytic(poly)
        ipoly = poly.integrate()
        total += ipoly(1) - ipoly(0)
    return total / 2


def piecewise_is_closed(piecewise: PiecewiseCurve) -> bool:
    """
    Tells if the piecewise curve is a closed curve
    """
    first_point = piecewise(piecewise.knots[0])
    last_point = piecewise(piecewise.knots[-1])
    return piecewise_is_continuous(piecewise) and (first_point == last_point)


def piecewise_is_continuous(piecewise: PiecewiseCurve) -> bool:
    """
    Tells if the segments are connected forming a continuous curve
    """
    segments = tuple(piecewise)
    return all(
        segments[i](1) == segments[i + 1](0) for i in range(len(segments) - 1)
    )


def piecewise_self_intersect(piecewise: PiecewiseCurve) -> bool:
    """
    Tells if the piecewise intersects itself

    Meaning, if there's at least two different (ta) and (tb)
    such piecewise(ta) == piecewise(tb)
    """
    return any(map(segment_self_intersect, piecewise))


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
    piecewise = clean_piecewise(jordan.piecewise)
    segments = list(piecewise)
    piecewise = Future.concatenate(segments)
    return JordanCurve(piecewise)


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
