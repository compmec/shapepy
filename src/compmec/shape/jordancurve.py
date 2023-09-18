"""
This modules contains a powerful class called JordanCurve which
is in fact, stores a list of spline-curves.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Optional, Tuple, Union

import numpy as np

from compmec.shape.curve import IntegratePlanar, PlanarCurve
from compmec.shape.polygon import Box, Point2D


class IntegrateJordan:
    @staticmethod
    def vertical(
        jordan: JordanCurve, expx: int, expy: int, nnodes: Optional[int] = None
    ):
        """
        Computes the integral I

        I = int x^expx * y^expy * dy
        """
        assert isinstance(jordan, JordanCurve)
        assert isinstance(expx, int)
        assert isinstance(expy, int)
        assert nnodes is None or isinstance(nnodes, int)
        total = 0
        for bezier in jordan.segments:
            total += IntegratePlanar.vertical(bezier, expx, expy, nnodes)
        return total

    @staticmethod
    def polynomial(
        jordan: JordanCurve, expx: int, expy: int, nnodes: Optional[int] = None
    ):
        """
        Computes the integral

        I = int x^expx * y^expy * ds
        """
        assert isinstance(jordan, JordanCurve)
        assert nnodes is None or isinstance(nnodes, int)
        total = 0
        for bezier in jordan.segments:
            total += IntegratePlanar.polynomial(bezier, expx, expy, nnodes)
        return total

    @staticmethod
    def lenght(jordan: JordanCurve, nnodes: Optional[int] = None) -> float:
        """
        Computes the lenght of jordan curve
        """
        assert isinstance(jordan, JordanCurve)
        assert nnodes is None or isinstance(nnodes, int)
        lenght = 0
        for bezier in jordan.segments:
            lenght += IntegratePlanar.lenght(bezier, nnodes)
        return lenght

    @staticmethod
    def area(jordan: JordanCurve, nnodes: Optional[int] = None) -> float:
        """
        Computes the interior area from jordan curve
        """
        assert isinstance(jordan, JordanCurve)
        assert nnodes is None or isinstance(nnodes, int)
        area = 0
        for bezier in jordan.segments:
            area += IntegratePlanar.area(bezier, nnodes)
        return area

    @staticmethod
    def winding_number(
        jordan: JordanCurve,
        center: Optional[Point2D] = (0.0, 0.0),
        nnodes: Optional[int] = None,
    ) -> Union[int, float]:
        """Computes the winding number from jordan curve

        Returns [-1, -0.5, 0, 0.5 or 1]
        """
        wind = 0
        if center in jordan.box():
            for bezier in jordan.segments:
                if center in bezier:
                    return 0.5 if float(jordan) > 0 else -0.5
        for bezier in jordan.segments:
            wind += IntegratePlanar.winding_number(bezier, center, nnodes)
        return round(wind)


class JordanCurve:
    """
    Jordan Curve is an arbitrary closed curve which doesn't intersect itself.
    It stores a list of 'segments', each segment is a bezier curve
    """

    def __init__(self, segments: Tuple[PlanarCurve]):
        self.segments = segments

    @classmethod
    def from_segments(cls, beziers: Tuple[PlanarCurve]) -> JordanCurve:
        """Initialize a JordanCurve from a list of beziers,

        :param beziers: The list connected planar curves
        :type beziers: Tuple[PlanarCurve]
        :return: The created jordan curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> from compmec.shape import PlanarCurve, JordanCurve
        >>> segment0 = PlanarCurve([(0, 0), (4, 0)])
        >>> segment1 = PlanarCurve([(4, 0), (4, 3), (0, 3)])
        >>> segment2 = PlanarCurve([(0, 3), (0, 0)])
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

        >>> from compmec.shape import JordanCurve
        >>> all_ctrlpoints = [(0, 0), (4, 0), (0, 3)]
        >>> JordanCurve.from_vertices(all_ctrlpoints)
        Jordan Curve of degree 1 and vertices
        ((0, 0), (4, 0), (0, 3))

        """
        if isinstance(vertices, str):
            raise TypeError
        vertices = list(vertices)
        for i, vertex in enumerate(vertices):
            vertices[i] = Point2D(vertex)
        nverts = len(vertices)
        vertices.append(vertices[0])
        beziers = [0] * nverts
        for i in range(nverts):
            ctrlpoints = vertices[i : i + 2]
            new_bezier = PlanarCurve(ctrlpoints)
            beziers[i] = new_bezier
        return cls.from_segments(beziers)

    @classmethod
    def from_ctrlpoints(cls, all_ctrlpoints: Tuple[Tuple[Point2D]]) -> JordanCurve:
        """Initialize a JordanCurve from a list of control points,

        :param all_ctrlpoints: The list of bezier control points
        :type all_ctrlpoints: Tuple[Tuple[Point2D]]
        :return: The created jordan curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> from compmec.shape import JordanCurve
        >>> all_ctrlpoints = [[(0, 0), (4, 0)],
                              [(4, 0), (4, 3), (0, 3)],
                              [(0, 3), (0, 0)]]
        >>> JordanCurve.from_ctrlpoints(all_ctrlpoints)
        Jordan Curve of degree 2 and vertices
        ((0, 0), (4, 0), (4, 3), (0, 3))

        """
        if isinstance(all_ctrlpoints, str):
            raise TypeError
        beziers = [0] * len(all_ctrlpoints)
        for i, ctrlpoints in enumerate(all_ctrlpoints):
            ctrlpoints = list(ctrlpoints)
            for j, ctrlpoint in enumerate(ctrlpoints):
                ctrlpoints[j] = Point2D(ctrlpoint)
            new_bezier = PlanarCurve(ctrlpoints)
            beziers[i] = new_bezier
        return cls.from_segments(beziers)

    @classmethod
    def from_full_curve(cls, full_curve) -> JordanCurve:
        """Initialize a JordanCurve from a full curve,

        :param full_curve: The full curve to split. Ideally ``compmec.nurbs.Curve`` instance
        :type full_curve: Point2D
        :return: The created jordan curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> from compmec import nurbs
        >>> from compmec.shape import Point2D, JordanCurve
        >>> knotvector = (0, 0, 0, 0.5, 1, 1, 1)
        >>> ctrlpoints = [(0, 0), (4, 0), (0, 3), (0, 0)]
        >>> ctrlpoints = [Point2D(point) for point in ctrlpoints]
        >>> curve = nurbs.Curve(knotvector, ctrlpoints)
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

    def copy(self) -> JordanCurve:
        """Returns a copy of the jordan curve.
        Also copies each point

        :return: The copied jordan curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> from compmec.shape import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = JordanCurve.from_vertices(vertices)
        >>> jordan.copy()
        Jordan Curve of degree 1 and vertices
        ((0, 0), (4, 0), (0, 3))

        """
        segments = self.segments
        nsegments = len(segments)
        all_points = []
        for segment in segments:
            points = list(point.copy() for point in segment.ctrlpoints)
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

        >>> from compmec.shape import JordanCurve
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
                        [start_point] + list(segment.ctrlpoints[1:-1]) + [end_point]
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

        >>> from compmec.shape import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = JordanCurve.from_vertices(vertices)
        >>> jordan.move((2, 3))
        Jordan Curve of degree 1 and vertices
        ((2, 3), (6, 3), (2, 6))

        """
        point = Point2D(point)
        for vertex in self.vertices:
            vertex.move(point)
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

        >>> from compmec.shape import JordanCurve
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
        >>> from compmec.shape import JordanCurve
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
        >>> from compmec.shape import JordanCurve
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

    def split(self, indexs: Tuple[int], nodes: Tuple[float]) -> None:
        """Divides the jordan curve in some nodes

        Given ``indexs = [a0, a1, ..., an]`` and ``nodes = [u0, u1, ..., un]``
        then for each pair ``(ai, ui)``, split the ``self.segments[ai]`` at ``ui``

        .. note: ``node = 0`` or ``node = 1`` are ignored

        :param indexs: The number of interior points, ``0 <= index < len(segments)``
        :type indexs: tuple[int]
        :param nodes: The nodes to split, ``0 <= node <= 1``
        :type nodes: tuple[float]

        Example use
        -----------

        >>> from matplotlib import pyplot as plt
        >>> from compmec.shape import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = JordanCurve.from_vertices(vertices)
        >>> jordan.split([0, 2], [1/2, 2/3])
        >>> print(jordan)
        Jordan Curve of degree 1 and vertices
        ((0, 0), (2.0, 0.0), (4, 0), (0, 3), (0.0, 1.0))

        """
        for index in indexs:
            assert isinstance(index, int)
            assert 0 <= index
            assert index < len(self.segments)
        for node in nodes:
            float(node)
            assert 0 <= node
            assert node <= 1
        assert len(indexs) == len(nodes)
        indexs = list(indexs)
        new_segments = list(self.segments)
        inserted = 0
        for index, node in zip(indexs, nodes):
            if abs(node) < 1e-6 or abs(node - 1) < 1e-6:
                continue
            segment = new_segments[index + inserted]
            start_point = segment.ctrlpoints[0]
            end_point = segment.ctrlpoints[-1]
            bezleft, bezrigh = segment.split([node])
            mid_point = bezrigh.ctrlpoints[0]
            bezleft.ctrlpoints = (
                [start_point] + list(bezleft.ctrlpoints[1:-1]) + [mid_point]
            )
            bezrigh.ctrlpoints = (
                [mid_point] + list(bezrigh.ctrlpoints[1:-1]) + [end_point]
            )
            new_segments[index + inserted] = bezleft
            new_segments.insert(index + inserted + 1, bezrigh)
            inserted += 1
        self.segments = tuple(new_segments)

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
        >>> from compmec.shape import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = JordanCurve.from_vertices(vertices)
        >>> points = jordan.points(3)
        >>> xvals = [point[0] for point in points]
        >>> yvals = [point[1] for point in points]
        >>> plt.plot(xvals, yvals, marker="o")
        >>> plt.show()

        """
        assert subnpts is None or (isinstance(subnpts, int) and subnpts >= 0)
        all_points = []
        for segment in self.segments:
            npts = subnpts if subnpts is not None else 10 * (segment.degree - 1)
            usample = tuple(Fraction(num, npts + 1) for num in range(npts + 1))
            points = segment.eval(usample)
            all_points += list(tuple(point) for point in points)
        all_points.append(all_points[0])  # Close the curve
        return tuple(all_points)

    def box(self) -> Box:
        """The box which encloses the jordan curve

        :return: The box which encloses the jordan curve
        :rtype: Box

        Example use
        -----------

        >>> from compmec.shape import JordanCurve
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
    def lenght(self) -> float:
        """Lenght

        If jordan curve is clockwise, then lenght < 0

        :getter: Returns the total lenght of the jordan curve
        :type: float

        Example use
        -----------

        >>> from compmec.shape import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = JordanCurve.from_vertices(vertices)
        >>> print(jordan.lenght)
        12.0
        >>> vertices = [(0, 0), (0, 3), (4, 0)]
        >>> jordan = JordanCurve.from_vertices(vertices)
        >>> print(jordan.lenght)
        -12.0

        """
        if self.__lenght is None:
            lenght = IntegrateJordan.lenght(self)
            area = IntegrateJordan.area(self)
            self.__lenght = lenght if area > 0 else -lenght
        return self.__lenght

    @property
    def segments(self) -> Tuple[PlanarCurve]:
        """Segments

        When setting, it checks if the points are the same between
        the junction of two segments to ensure a closed curve

        :getter: Returns the tuple of connected planar beziers, not copy
        :setter: Sets the segments of the jordan curve
        :type: tuple[PlanarCurve]

        Example use
        -----------

        >>> from compmec.shape import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = JordanCurve.from_vertices(vertices)
        >>> print(jordan.segments)
        (PlanarCurve (deg 1), PlanarCurve (deg 1), PlanarCurve (deg 1))
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

        >>> from compmec.shape import JordanCurve
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
    def segments(self, other: Tuple[PlanarCurve]):
        for segment in other:
            if not isinstance(segment, PlanarCurve):
                raise TypeError
        ncurves = len(other)
        for i in range(ncurves - 1):
            end_point = other[i].ctrlpoints[-1]
            start_point = other[i + 1].ctrlpoints[0]
            assert start_point == end_point
            assert id(start_point) == id(end_point)
        for segment in other:
            segment.clean()
        self.__lenght = None
        segments = []
        for bezier in other:
            ctrlpoints = [Point2D(point) for point in bezier.ctrlpoints]
            new_bezier = PlanarCurve(ctrlpoints)
            segments.append(new_bezier)
        self.__segments = tuple(segments)

    def __and__(self, other: JordanCurve) -> Tuple[Tuple[int, int, float, float]]:
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
        assert isinstance(other, JordanCurve)
        for point in other.points(1):
            if point not in self:
                return False
        selcopy = self.copy().clean()
        othcopy = other.copy().clean()
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
        return self.copy().invert()

    def __contains__(self, point: Point2D) -> bool:
        """Tells if the point is on the boundary"""
        if point not in self.box():
            return False
        for bezier in self.segments:
            if point in bezier:
                return True
        return False

    def __float__(self) -> float:
        return self.lenght

    def __abs__(self) -> JordanCurve:
        """Returns the same curve, but in positive direction"""
        return self.copy() if float(self) > 0 else (~self)

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
        self, other: JordanCurve, equal_beziers: bool = True, end_points: bool = True
    ) -> Tuple[Tuple[int, int, float, float]]:
        """Computes the intersection between two jordan curves

        Finds the values of (a*, b*, u*, v*) such

            self.segments[a*].eval(u*) == other.segments[b*].eval(v*)

        It computes the intersection between each pair of segments
        from ``self`` and ``other`` and returns the matrix of coefficients

        [(a0, b0, u0, v0), (a1, b1, u1, v1), ...]

        * 0 <= ai < len(self.segments)
        * 0 <= bi < len(other.segments)
        * 0 <= u0 <= 1
        * 0 <= v0 <= 1

        If the flat ``equal_beziers`` are active, then when ``self.segments[ai] == other.segments[bi]``, then ``ui = None`` and ``vi = None``.
        If the flag is ``False``, then these cases will not be returned

        If the flat ``end_points`` are inactive, then will remove when ``(ui, vi)`` are ``(0, 0)``, ``(0, 1)``, ``(1, 0)`` or ``(1, 1)``

        :param other: The jordan curve which intersects ``self``
        :type other: JordanCurve
        :param equal_beziers: Flag to return (or not) when two segments are equal, defaults to ``True``
        :type equal_beziers: bool(, optional)
        :param end_points: Flag to return (or not) when jordans intersect at end points, defaults to ``True``
        :type end_points: bool(, optional)
        :return: The matrix of coefficients [(ai, bi, ui, vi)] or an empty tuple in case of non-intersection
        :rtype: tuple[(int, int, float, float)]

        Example use
        -----------

        >>> from compmec.shape import JordanCurve
        >>> vertices_a = [(0, 0), (2, 0), (2, 2), (0, 2)]
        >>> jordan_a = JordanCurve.from_vertices(vertices_a)
        >>> vertices_b = [(1, 1), (3, 1), (3, 3), (1, 3)]
        >>> jordan_b = JordanCurve.from_vertices(vertices_b)
        >>> jordan_a.intersection(jordan_b)
        ((1, 0, 1/2, 1/2), (2, 3, 1/2, 1/2))

        """
        assert isinstance(other, JordanCurve)
        intersections = self.__intersection(other)
        # Filter the values
        if not equal_beziers:
            for ai, bi, ui, vi in tuple(intersections):
                if ui is None:
                    intersections.remove((ai, bi, ui, vi))
        if not end_points:
            for ai, bi, ui, vi in tuple(intersections):
                if ui is None or (0 < ui and ui < 1) or (0 < vi and vi < 1):
                    continue
                intersections.remove((ai, bi, ui, vi))
        return tuple(sorted(intersections))
