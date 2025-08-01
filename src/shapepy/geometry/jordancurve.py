"""
This modules contains a powerful class called JordanCurve which
is in fact, stores a list of spline-curves.
"""

from __future__ import annotations

from copy import copy
from fractions import Fraction
from typing import Optional, Tuple

import numpy as np

from shapepy.geometry.box import Box
from shapepy.geometry.point import Point2D
from shapepy.geometry.segment import Segment

from ..scalar.bezier import Bezier, bezier2polynomial
from ..scalar.calculus import derivate, integrate
from ..scalar.reals import Real
from ..tools import Is, To


class JordanCurve:
    """
    Jordan Curve is an arbitrary closed curve which doesn't intersect itself.
    It stores a list of 'segments', each segment is a bezier curve
    """

    def __init__(self, segments: Tuple[Segment]):
        self.__length = None
        self.__area = None
        self.segments = segments

    @classmethod
    def from_segments(cls, beziers: Tuple[Segment]) -> JordanCurve:
        """Initialize a JordanCurve from a list of beziers,

        :param beziers: The list connected planar curves
        :type beziers: Tuple[Segment]
        :return: The created jordan curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> from shapepy import Segment, JordanCurve
        >>> segment0 = Segment([(0, 0), (4, 0)])
        >>> segment1 = Segment([(4, 0), (4, 3), (0, 3)])
        >>> segment2 = Segment([(0, 3), (0, 0)])
        >>> JordanCurve.from_segments([segment0, segment1, segment2])
        Jordan Curve of degree 2 and vertices
        ((0, 0), (4, 0), (4, 3), (0, 3))

        """
        nbezs = len(beziers)
        for i, bezi in enumerate(beziers):
            j = (i + 1) % nbezs
            bezj = beziers[j]
            prev_end_point = bezi.ctrlpoints[-1]
            next_start_point = bezj.ctrlpoints[0]
            assert prev_end_point == next_start_point
            bezi.ctrlpoints = list(bezi.ctrlpoints[:-1]) + [next_start_point]
        return cls(beziers)

    @classmethod
    def from_vertices(cls, vertices: Tuple[Point2D]) -> JordanCurve:
        """Initialize a polygonal JordanCurve from a list of vertices,

        :param vertices: The list vertices
        :type vertices: Tuple[Point2D]
        :return: The created jordan curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> from shapepy import JordanCurve
        >>> all_ctrlpoints = [(0, 0), (4, 0), (0, 3)]
        >>> JordanCurve.from_vertices(all_ctrlpoints)
        Jordan Curve of degree 1 and vertices
        ((0, 0), (4, 0), (0, 3))

        """
        if Is.instance(vertices, str):
            raise TypeError
        vertices = list(vertices)
        for i, vertex in enumerate(vertices):
            vertices[i] = To.point(vertex)
        nverts = len(vertices)
        vertices.append(vertices[0])
        beziers = [0] * nverts
        for i in range(nverts):
            ctrlpoints = vertices[i : i + 2]
            new_bezier = Segment(ctrlpoints)
            beziers[i] = new_bezier
        return cls.from_segments(beziers)

    @classmethod
    def from_ctrlpoints(
        cls, all_ctrlpoints: Tuple[Tuple[Point2D]]
    ) -> JordanCurve:
        """Initialize a JordanCurve from a list of control points,

        :param all_ctrlpoints: The list of bezier control points
        :type all_ctrlpoints: Tuple[Tuple[Point2D]]
        :return: The created jordan curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> from shapepy import JordanCurve
        >>> all_ctrlpoints = [[(0, 0), (4, 0)],
                              [(4, 0), (4, 3), (0, 3)],
                              [(0, 3), (0, 0)]]
        >>> JordanCurve.from_ctrlpoints(all_ctrlpoints)
        Jordan Curve of degree 2 and vertices
        ((0, 0), (4, 0), (4, 3), (0, 3))

        """
        if Is.instance(all_ctrlpoints, str):
            raise TypeError
        beziers = [0] * len(all_ctrlpoints)
        for i, ctrlpoints in enumerate(all_ctrlpoints):
            ctrlpoints = list(ctrlpoints)
            for j, ctrlpoint in enumerate(ctrlpoints):
                ctrlpoints[j] = To.point(ctrlpoint)
            new_bezier = Segment(ctrlpoints)
            beziers[i] = new_bezier
        return cls.from_segments(beziers)

    @classmethod
    def from_full_curve(cls, full_curve) -> JordanCurve:
        """Initialize a JordanCurve from a full curve,

        :param full_curve: The full curve to split.
                Ideally ``pynurbs.Curve`` instance
        :type full_curve: Point2D
        :return: The created jordan curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> import pynurbs
        >>> from shapepy import Point2D, JordanCurve
        >>> knotvector = (0, 0, 0, 0.5, 1, 1, 1)
        >>> ctrlpoints = [(0, 0), (4, 0), (0, 3), (0, 0)]
        >>> ctrlpoints = [Point2D(point) for point in ctrlpoints]
        >>> curve = pynurbs.Curve(knotvector, ctrlpoints)
        >>> jordan = JordanCurve.from_full_curve(curve)
        >>> print(jordan)
        Jordan Curve of degree 2 and vertices
        ((0.0, 0.0), (4.0, 0.0), (2.0, 1.5), (0.0, 3.0))

        """
        assert full_curve.ctrlpoints[0] == full_curve.ctrlpoints[-1]
        beziers = full_curve.split()
        for bezier in beziers:
            bezier.clean()
        all_ctrlpoints = [bezier.ctrlpoints for bezier in beziers]
        return cls.from_ctrlpoints(all_ctrlpoints)

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
        return self.__class__.from_segments(new_segments)

    def clean(self) -> JordanCurve:
        """Clean the jordan curve

        Removes the uncessary nodes from jordan curve,
        for example, after calling ``split`` function

        :return: The same curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (1, 0), (4, 0), (0, 3)]
        >>> jordan = JordanCurve.from_vertices(vertices)
        >>> jordan.clean()
        Jordan Curve of degree 1 and vertices
        ((0, 0), (4, 0), (0, 3))

        """
        for segment in self.segments:
            segment.clean()
        segments = list(self.segments)
        while True:
            nsegments = len(segments)
            for i in range(nsegments):
                j = (i + 1) % nsegments
                seg0 = segments[i]
                seg1 = segments[j]
                try:
                    start_point = seg0.ctrlpoints[0]
                    end_point = seg1.ctrlpoints[-1]
                    segment = seg0 | seg1
                    segment.ctrlpoints = (
                        [start_point]
                        + list(segment.ctrlpoints[1:-1])
                        + [end_point]
                    )
                    segments[i] = segment
                    segments.pop(j)
                    break  # Can unite
                except ValueError:
                    pass  # Cannot unite
            else:  # Cannot unite more segments
                break
        self.segments = segments
        return self

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
        >>> jordan = JordanCurve.from_vertices(vertices)
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
        >>> jordan = JordanCurve.from_vertices(vertices)
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
        >>> jordan = JordanCurve.from_vertices(vertices)
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
        >>> jordan = JordanCurve.from_vertices(vertices)
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

    def __split_segment(self, index: int, nodes: Tuple[float]) -> None:
        nodes = tuple(sorted(nodes))
        segment = self.segments[index]
        new_segments = segment.split(nodes)
        for new_segment in new_segments:
            new_segment.clean()
        points = list(new_segments[0].ctrlpoints)
        points[0] = segment.ctrlpoints[0]
        new_segments[0].ctrlpoints = points
        points = list(new_segments[-1].ctrlpoints)
        points[-1] = segment.ctrlpoints[-1]
        new_segments[-1].ctrlpoints = points
        for i in range(len(nodes)):
            points = list(new_segments[i + 1].ctrlpoints)
            points[0] = new_segments[i].ctrlpoints[-1]
            new_segments[i + 1].ctrlpoints = points
        total_segments = list(self.segments)
        total_segments.pop(index)
        for i, segment in enumerate(new_segments):
            total_segments.insert(index + i, segment)
        self.segments = total_segments

    def split(self, indexs: Tuple[int], nodes: Tuple[float]) -> None:
        """Divides the jordan curve in some nodes

        Given ``indexs = [a0, a1, ..., an]`` and ``nodes = [u0, u1, ..., un]``
        then for each pair ``(ai, ui)``,
        split the ``self.segments[ai]`` at ``ui``

        .. note: ``node = 0`` or ``node = 1`` are ignored

        :param indexs: The number of interior points,
                       ``0 <= index < len(segments)``
        :type indexs: tuple[int]
        :param nodes: The nodes to split, ``0 <= node <= 1``
        :type nodes: tuple[float]

        Example use
        -----------

        >>> from matplotlib import pyplot as plt
        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = JordanCurve.from_vertices(vertices)
        >>> jordan.split([0, 2], [1/2, 2/3])
        >>> print(jordan)
        Jordan Curve of degree 1 and vertices
        ((0, 0), (2.0, 0.0), (4, 0), (0, 3), (0.0, 1.0))

        """
        for index in indexs:
            assert Is.integer(index) and 0 <= index
            assert index < len(self.segments)
        for node in nodes:
            assert Is.finite(node) and 0 <= node <= 1
        assert len(indexs) == len(nodes)
        # Clean boundary nodes, when node = 0 or 1
        pairs = sorted(zip(indexs, nodes))
        i = 0
        while i < len(pairs):
            node = pairs[i][1]
            if abs(node) < 1e-6 or abs(node - 1) < 1e-6:
                pairs.pop(i)
            else:
                i += 1
        shift = 0
        for ind in range(len(self.segments)):
            new_nodes = tuple(node for index, node in pairs if index == ind)
            if len(new_nodes) == 0:
                continue
            self.__split_segment(ind + shift, new_nodes)
            shift += len(new_nodes)

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
        >>> jordan = JordanCurve.from_vertices(vertices)
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
        >>> jordan = JordanCurve.from_vertices(vertices)
        >>> jordan.box()
        Box with vertices (0, 0) and (4, 3)

        """
        box = None
        for bezier in self.segments:
            box |= bezier.box()
        return box

    @property
    def length(self) -> Real:
        """The length of the curve"""
        if self.__length is None:
            self.__length = sum(seg.length for seg in self.segments)
        return self.__length

    @property
    def area(self) -> Real:
        """The internal area"""
        if self.__area is None:
            self.__area = compute_area(self)
        return self.__area

    @property
    def segments(self) -> Tuple[Segment]:
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
        >>> jordan = JordanCurve.from_vertices(vertices)
        >>> print(jordan.segments)
        (Segment (deg 1), Segment (deg 1), Segment (deg 1))
        >>> print(jordan.segments[0])
        Planar curve of degree 1 and control points ((0, 0), (4, 0))

        """
        return tuple(self.__segments)

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
        >>> jordan = JordanCurve.from_vertices(vertices)
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
    def segments(self, other: Tuple[Segment]):
        for segment in other:
            if not Is.instance(segment, Segment):
                raise TypeError
        ncurves = len(other)
        for i in range(ncurves - 1):
            end_point = other[i].ctrlpoints[-1]
            start_point = other[i + 1].ctrlpoints[0]
            assert start_point == end_point
            assert id(start_point) == id(end_point)
        for segment in other:
            segment.clean()
        self.__length = None
        self.__area = None
        segments = []
        for bezier in other:
            ctrlpoints = [To.point(point) for point in bezier.ctrlpoints]
            new_bezier = Segment(ctrlpoints)
            segments.append(new_bezier)
        self.__segments = tuple(segments)

    def __and__(
        self, other: JordanCurve
    ) -> Tuple[Tuple[int, int, float, float]]:
        """Computes the intersection of two jordan curves"""
        return self.intersection(other, equal_beziers=False, end_points=False)

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
        assert Is.instance(other, JordanCurve)
        for point in other.points(1):
            if point not in self:
                return False
        selcopy = self.__copy__().clean()
        othcopy = other.__copy__().clean()
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
        if point not in self.box():
            return False
        for bezier in self.segments:
            if point in bezier:
                return True
        return False

    def __float__(self) -> float:
        """Returns the lenght of the curve

        If jordan curve is clockwise, then lenght < 0

        :getter: Returns the total lenght of the jordan curve
        :type: float

        Example use
        -----------

        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = JordanCurve.from_vertices(vertices)
        >>> print(float(jordan))
        12.0
        >>> vertices = [(0, 0), (0, 3), (4, 0)]
        >>> jordan = JordanCurve.from_vertices(vertices)
        >>> print(float(jordan))
        -12.0

        """
        return float(self.length if self.area > 0 else -self.length)

    def __abs__(self) -> JordanCurve:
        """Returns the same curve, but in positive direction"""
        curve = self.__copy__()
        return curve if float(self) > 0 else curve.invert()

    def __intersection(
        self, other: JordanCurve
    ) -> Tuple[Tuple[int, int, float, float]]:
        """Private method of ``intersection``

        Computes the intersection between ``self`` and ``other``
        returning a list of [(a0, b0, u0, v0), ...]
        such self.segments[a0](u0) == other.segments[b0](v0)

        If (ui, vi) == (None, None), it means
        self.segments[a0] == other.segments[b0]

        """
        intersections = set()
        for ai, sbezier in enumerate(self.segments):
            for bj, obezier in enumerate(other.segments):
                inters = sbezier & obezier
                if inters is None:
                    continue
                if len(inters) == 0:  # Equal curves
                    intersections.add((ai, bj, None, None))
                for ui, vj in inters:
                    intersections.add((ai, bj, ui, vj))
        return list(intersections)

    def intersection(
        self,
        other: JordanCurve,
        equal_beziers: bool = True,
        end_points: bool = True,
    ) -> Tuple[Tuple[int, int, float, float]]:
        r"""Computes the intersection between two jordan curves

        Finds the values of (:math:`a^{\star}`, :math:`b^{\star}`,
        :math:`u^{\star}`, :math:`v^{\star}`) such

        .. math::
            S_{a^{\star}}(u^{\star}) == O_{b^{\star}}(v^{\star})

        It computes the intersection between each pair of segments
        from ``self`` and ``other`` and returns the matrix of coefficients

        .. math::

            \begin{bmatrix}
            a_0 & b_0 & u_0 & v_0 \\
            a_1 & b_1 & u_1 & v_1 \\
            \vdots & \vdots & \vdots & \vdots \\
            a_{n} & b_{n} & u_{n} & v_{n}
            \end{bmatrix}

        If two bezier curves are equal, then ``u_i = v_i = None``

        * ``0 <= a_i < len(self.segments)``
        * ``0 <= b_i < len(other.segments)``
        * ``0 <= u_i <= 1`` or ``None``
        * ``0 <= v_i <= 1`` or ``None``

        Parameters
        ----------
        other : JordanCurve
            The jordan curve which intersects ``self``
        equal_beziers : bool, default = True
            Flag to return (or not) when two segments are equal

            If the flag ``equal_beziers`` are inactive,
            then will remove when ``(ui, vi) == (None, None)``.

        end_points : bool, default = True
            Flag to return (or not) when jordans intersect at end points

            If the flag ``end_points`` are inactive,
            then will remove when ``(ui, vi)`` are
            ``(0, 0)``, ``(0, 1)``, ``(1, 0)`` or ``(1, 1)``

        :return: The matrix of coefficients ``[(ai, bi, ui, vi)]``
                 or an empty tuple in case of non-intersection
        :rtype: tuple[(int, int, float, float)]


        Example use
        -----------
        >>> from shapepy import JordanCurve
        >>> vertices_a = [(0, 0), (2, 0), (2, 2), (0, 2)]
        >>> jordan_a = JordanCurve.from_vertices(vertices_a)
        >>> vertices_b = [(1, 1), (3, 1), (3, 3), (1, 3)]
        >>> jordan_b = JordanCurve.from_vertices(vertices_b)
        >>> jordan_a.intersection(jordan_b)
        ((1, 0, 1/2, 1/2), (2, 3, 1/2, 1/2))

        """
        assert Is.instance(other, JordanCurve)
        intersections = self.__intersection(other)
        # Filter the values
        if not equal_beziers:
            for ai, bi, ui, vi in tuple(intersections):
                if ui is None:
                    intersections.remove((ai, bi, ui, vi))
        if not end_points:
            for ai, bi, ui, vi in tuple(intersections):
                if ui is None or (0 < ui < 1) or (0 < vi < 1):
                    continue
                intersections.remove((ai, bi, ui, vi))
        return tuple(sorted(intersections))


def compute_area(jordan: JordanCurve) -> Real:
    """
    Computes the area inside of the jordan curve

    If jordan is clockwise, then the area is negative
    """

    total = 0
    for segment in jordan.segments:
        xfunc = bezier2polynomial(Bezier(pt[0] for pt in segment.ctrlpoints))
        yfunc = bezier2polynomial(Bezier(pt[1] for pt in segment.ctrlpoints))
        poly = integrate(xfunc * derivate(yfunc) - yfunc * derivate(xfunc))
        total += poly(1) - poly(0)
    return total / 2
