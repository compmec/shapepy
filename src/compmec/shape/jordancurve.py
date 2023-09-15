"""
This modules contains a powerful class called JordanCurve which
is in fact, stores a list of spline-curves.
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Optional, Tuple, Union

import numpy as np

from compmec.shape.curve import IntegratePlanar, PlanarCurve
from compmec.shape.polygon import Box, Point2D


class IntegrateJordan:
    @staticmethod
    def horizontal(
        jordan: JordanCurve, expx: int, expy: int, nnodes: Optional[int] = None
    ):
        """
        Computes the integral I

        I = int x^expx * y^expy * dx
        """
        assert isinstance(jordan, JordanCurve)
        assert isinstance(expx, int)
        assert isinstance(expy, int)
        assert nnodes is None or isinstance(nnodes, int)
        total = 0
        for bezier in jordan.segments:
            total += IntegratePlanar.horizontal(bezier, expx, expy, nnodes)
        return total

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
        jordan: JordanCurve, nnodes: Optional[int] = None
    ) -> Union[int, float]:
        """Computes the winding number from jordan curve

        Returns [-1, 0, or 1]
        """
        wind = 0
        for bezier in jordan.segments:
            wind += IntegratePlanar.winding_number(bezier, nnodes)
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
        """Returns a polygonal jordan curve"""
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
        if isinstance(all_ctrlpoints, str):
            raise TypeError
        nbezs = len(all_ctrlpoints)
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
        assert full_curve.ctrlpoints[0] == full_curve.ctrlpoints[-1]
        beziers = full_curve.split()
        all_ctrlpoints = [bezier.ctrlpoints for bezier in beziers]
        return cls.from_ctrlpoints(all_ctrlpoints)

    def copy(self) -> JordanCurve:
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
        point = Point2D(point)
        for vertex in self.vertices:
            vertex.move(point)
        return self

    def scale(self, xscale: float, yscale: float) -> JordanCurve:
        float(xscale)
        float(yscale)
        for vertex in self.vertices:
            vertex.scale(xscale, yscale)
        return self

    def rotate(self, angle: float, degrees: bool = False) -> JordanCurve:
        float(angle)
        if degrees:
            angle *= np.pi / 180
        for vertex in self.vertices:
            vertex.rotate(angle)
        return self

    def invert(self) -> JordanCurve:
        """
        Invert the orientation of a jordan curve
        """
        segments = self.segments
        nsegs = len(segments)
        new_segments = []
        for i in range(nsegs - 1, -1, -1):
            new_segments.append(segments[i].invert())
        self.segments = tuple(new_segments)
        return self

    def split(self, indexs: Tuple[int], nodes: Tuple[float]) -> None:
        """
        Divides a list of segments in the respective nodes
        If node == 0 or node == 1 (extremities), only ignores
        the given node
        """
        assert isinstance(indexs, (tuple, list))
        assert isinstance(nodes, (tuple, list))
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

    def points(self, subnpts: Optional[int] = 2) -> Tuple[Point2D]:
        """
        Returns a list of points on the boundary.
        Main reason: plot the jordan
        You can choose the precision by changing the ```subnpts``` parameter

        subnpts = 0 -> extremities
        subnpts = 1 -> extremities + midpoint
        """
        assert isinstance(subnpts, int)
        assert subnpts >= 0
        all_points = []
        usample = tuple(Fraction(num, subnpts + 1) for num in range(subnpts + 1))
        for segment in self.segments:
            points = segment.eval(usample)
            all_points += list(points)
        all_points.append(all_points[0])  # Close the curve
        return tuple(all_points)

    def box(self) -> Box:
        """Gives two points which encloses the jordan curve"""
        inf = float("inf")
        box = Box(Point2D(inf, inf), Point2D(-inf, -inf))
        for bezier in self.segments:
            box |= bezier.box()
        return box

    @property
    def lenght(self) -> float:
        if self.__lenght is None:
            lenght = IntegrateJordan.lenght(self)
            area = IntegrateJordan.area(self)
            self.__lenght = lenght if area > 0 else -lenght
        return self.__lenght

    @property
    def segments(self) -> Tuple[PlanarCurve]:
        return tuple(self.__segments)

    @property
    def vertices(self) -> Tuple[Point2D]:
        """
        Returns a tuple of non repeted points
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
        """
        Given two jordan curves, this functions returns the intersection
        between these two jordan curves
        Returns empty tuple if the curves don't intersect each other
        """
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
        """
        Tells if the point is on the boundary
        """
        if point not in self.box():
            return False
        for bezier in self.segments:
            if point in bezier:
                return True
        return False

    def __float__(self) -> float:
        return self.lenght

    def __abs__(self) -> JordanCurve:
        """
        Returns the same curve, but in positive direction
        """
        return self.copy() if float(self) > 0 else (~self)

    def __intersection(
        self, other: JordanCurve
    ) -> Tuple[Tuple[int, int, float, float]]:
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
        """
        Returns the intersection between two curves A and B
        result = ((a0, b0, u0, v0), (a1, b1, u1, v1), ...)
        Which
            A.segments[ai].eval(ui) == B.segments[bi].eval(vi)
        0 <= ai < len(A.segments)
        0 <= bi < len(B.segments)
        0 <= u0 <= 1
        0 <= v0 <= 1
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
