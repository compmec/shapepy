"""
This modules contains a powerful class called JordanCurve which
is in fact, stores a list of spline-curves.
"""
from __future__ import annotations

import math
from copy import deepcopy
from fractions import Fraction
from typing import FrozenSet, Tuple

import numpy as np

from compmec import nurbs
from compmec.shape.polygon import Point2D, Segment


class IntersectionBeziers:
    @staticmethod
    def is_equal_controlpoints(cptsa: Tuple[Point2D], cptsb: Tuple[Point2D]) -> bool:
        if len(cptsa) != len(cptsb):
            return False
        for pta, ptb in zip(cptsa, cptsb):
            if pta != ptb:
                return False
        return True

    @staticmethod
    def eval_bezier(degree: int, node: float) -> Tuple[float]:
        """
        Returns [B_p(u)] = [B_{0p}(u) ... B_{pp}(u)]
        With
            B_{ip} = binom(p, i) * (1-u)^{p-i} * u^i
        """
        comp = 1 - node
        result = [0] * (degree + 1)
        for i in range(degree + 1):
            result[i] = math.comb(degree, i) * comp ** (degree - i) * node**i
        return tuple(result)

    @staticmethod
    def matrix_derivate(degree: int) -> Tuple[Tuple[int]]:
        """
        Let A(u) be a nonrational-bezier curve defined by
            A(u) = sum_{i=0}^{p} B_{ip}(u) * P_{i}
        We want to compute the derivative A'(u)

        This function returns a matrix [M] such
            A'(u) = sum_{i=0}^{p} B_{ip}(u) * Q_{i}
            Q_{i} = sum_{j=0}^{p} M_{i,j} * P_j

        Where
            B_{ip}(u) = binom(p, i) * (1-u)^{p-i} * u^i
        """
        matrix = np.zeros((degree + 1, degree + 1), dtype="int16")
        for i in range(degree):
            matrix[i, i + 1] = degree - i
            matrix[i + 1, i] = -(i + 1)
        for i in range(degree + 1):
            matrix[i, i] = 2 * i - degree
        return tuple([tuple(line) for line in matrix])

    @staticmethod
    def intersection_bezier(
        cptsa: Tuple[Point2D], cptsb: Tuple[Point2D]
    ) -> Tuple[Tuple[float]]:
        """
        Returns the intersection parameters of the intersection of two bezier curves.

        Given two bezier curves A(u) and B(v), this function returns the pairs (u*, t*)
        such A(u*) = B(v*). As there can be many intersections, returns
            [(u0*, t0*), ..., (un*, tn*)]

        If one curve is equal to another, returns a empty tuple
        if there's no intersection, returns a empty tuple
        """
        if IntersectionBeziers.is_equal_controlpoints(cptsa, cptsb):
            return tuple()
        dega = len(cptsa) - 1
        degb = len(cptsb) - 1
        dmata = np.array(IntersectionBeziers.matrix_derivate(dega))
        dmatb = np.array(IntersectionBeziers.matrix_derivate(degb))

        cptsa = np.array(cptsa)
        cptsb = np.array(cptsb)
        dcptsa = dmata @ cptsa
        ddcptsa = dmata @ dcptsa
        dcptsb = dmatb @ cptsb
        ddcptsb = dmatb @ dcptsb

        pts_ada = np.tensordot(cptsa, dcptsa, axes=0)
        pts_adb = np.tensordot(cptsa, dcptsb, axes=0)
        pts_bda = np.tensordot(cptsb, dcptsa, axes=0)
        pts_bdb = np.tensordot(cptsb, dcptsb, axes=0)
        pts_adda = np.tensordot(cptsa, ddcptsa, axes=0)
        pts_addb = np.tensordot(cptsa, ddcptsb, axes=0)
        pts_bdda = np.tensordot(cptsb, ddcptsa, axes=0)
        pts_bddb = np.tensordot(cptsb, ddcptsb, axes=0)
        pts_dada = np.tensordot(dcptsa, dcptsa, axes=0)
        pts_dadb = np.tensordot(dcptsa, dcptsb, axes=0)
        pts_dbdb = np.tensordot(dcptsb, dcptsb, axes=0)

        nptas, nptbs = dega + 3, degb + 3
        usample = [Fraction(i) / nptbs for i in range(nptas + 1)]
        vsample = [Fraction(i) / nptbs for i in range(nptbs + 1)]

        intersections = set()
        for i in range(nptas + 1):
            for j in range(nptbs + 1):
                ui = usample[i]
                vj = vsample[j]
                # Starts newton iteration
                for k in range(10):  # Number of newton iterations
                    aui = IntersectionBeziers.eval_bezier(dega, ui)
                    bvj = IntersectionBeziers.eval_bezier(degb, vj)
                    ada = aui @ pts_ada @ aui
                    adb = aui @ pts_adb @ bvj
                    bda = bvj @ pts_bda @ aui
                    bdb = bvj @ pts_bdb @ bvj
                    adda = aui @ pts_adda @ aui
                    addb = aui @ pts_addb @ bvj
                    bdda = bvj @ pts_bdda @ aui
                    bddb = bvj @ pts_bddb @ bvj
                    dada = aui @ pts_dada @ aui
                    dadb = aui @ pts_dadb @ bvj
                    dbdb = bvj @ pts_dbdb @ bvj

                    mat00 = dbdb + bddb - addb
                    mat11 = dada + adda - bdda
                    vec0 = ada - bda
                    vec1 = bdb - adb
                    denom = mat00 * mat11 - dadb**2
                    if denom == 0:
                        ui, vj = float("inf"), float("inf")
                        break
                    oldui = ui
                    oldvj = vj
                    ui -= (mat00 * vec0 + dadb * vec1) / denom
                    vj -= (dadb * vec0 + mat11 * vec1) / denom
                    ui = min(1, max(0, ui))
                    vj = min(1, max(0, vj))
                    if abs(oldui - ui) < 1e-9 and abs(oldvj - vj) < 1e-9:
                        break
                if (0 < ui and ui < 1) or (0 < vj and vj < 1):
                    intersections.add((ui, vj))
        for ui, vj in tuple(intersections):
            aui = IntersectionBeziers.eval_bezier(dega, ui)
            bvj = IntersectionBeziers.eval_bezier(degb, vj)
            pta = aui @ cptsa
            ptb = bvj @ cptsb
            norm = abs(pta - ptb)
            if norm > 1e-9:
                intersections.remove((ui, vj))
        intersections = tuple(intersections)

        return intersections


class JordanCurve:
    """
    Jordan Curve is an arbitrary closed curve which doesn't intersect itself.
    It stores a list of 'segments': Each 'segment' is a lambda function.
    """

    def __init__(self, curve: nurbs.Curve):
        assert isinstance(curve, nurbs.Curve)
        self.__full_curve = deepcopy(curve)
        self.__segments = None

    def copy(self) -> JordanCurve:
        return deepcopy(self)

    def area(self) -> float:
        """
        Computes the area of the jordan curves.
        If
        """
        raise NotImplementedError

    def move(self, point: Point2D) -> JordanCurve:
        fullctrlpts = list(self.__full_curve.ctrlpoints)
        for i, ctrlpt in enumerate(fullctrlpts):
            fullctrlpts[i] = ctrlpt + point
        self.__full_curve.ctrlpoints = tuple(fullctrlpts)
        segments = list(self.segments)
        for i, segment in enumerate(segments):
            ctrlpts = list(segment.ctrlpoints)
            for j, ctrlpt in enumerate(ctrlpts):
                ctrlpts[j] = ctrlpt + point
            segment.ctrlpoints = tuple(ctrlpts)
            segments[i] = segment
        self.__segments = segments
        return self

    def scale(self, xscale: float, yscale: float) -> JordanCurve:
        fullctrlpts = list(self.__full_curve.ctrlpoints)
        for i, ctrlpt in enumerate(fullctrlpts):
            fullctrlpts[i] = Point2D(xscale * ctrlpt[0], yscale * ctrlpt[1])
        self.__full_curve.ctrlpoints = tuple(fullctrlpts)
        segments = list(self.segments)
        for i, segment in enumerate(segments):
            ctrlpts = list(segment.ctrlpoints)
            for j, ctrlpt in enumerate(ctrlpts):
                ctrlpts[j] = Point2D(xscale * ctrlpt[0], yscale * ctrlpt[1])
            segment.ctrlpoints = tuple(ctrlpts)
            segments[i] = segment
        self.__segments = segments
        return self

    def rotate(self, angle: float, degrees: bool = False) -> JordanCurve:
        if degrees:
            angle *= np.pi / 180
        cos, sin = np.cos(angle), np.sin(angle)

        fullctrlpts = list(self.__full_curve.ctrlpoints)
        for i, ctrlpt in enumerate(fullctrlpts):
            newptx = cos * ctrlpt[0] - sin * ctrlpt[1]
            newpty = sin * ctrlpt[0] + cos * ctrlpt[1]
            fullctrlpts[i] = Point2D(newptx, newpty)
        self.__full_curve.ctrlpoints = tuple(fullctrlpts)
        segments = list(self.segments)
        for i, segment in enumerate(segments):
            ctrlpts = list(segment.ctrlpoints)
            for j, ctrlpt in enumerate(ctrlpts):
                newptx = cos * ctrlpt[0] - sin * ctrlpt[1]
                newpty = sin * ctrlpt[0] + cos * ctrlpt[1]
                ctrlpts[j] = Point2D(newptx, newpty)
            segment.ctrlpoints = tuple(ctrlpts)
            segments[i] = segment
        self.__segments = segments
        return self

    def invert(self) -> JordanCurve:
        knotvector = self.__full_curve.knotvector
        ctrlpoints = self.__full_curve.ctrlpoints
        assert self.__full_curve.weights is None
        umin, umax = knotvector.limits
        newknotvector = [umin + umax - u for u in knotvector[::-1]]
        self.__full_curve.ctrlpoints = None
        self.__full_curve.knotvector = newknotvector
        self.__full_curve.ctrlpoints = ctrlpoints[::-1]
        self.__segments = None
        return self

    def split(self, nodes: Tuple[float]) -> None:
        nodes = tuple(sorted(set(nodes)))
        nodes = np.array(nodes)
        curbeziers = self.segments
        newbeziers = []
        for bezier in curbeziers:
            limits = bezier.knotvector.limits
            mask = (limits[0] < nodes) * (nodes < limits[1])
            internal_nodes = nodes[mask]
            news = bezier.split(internal_nodes)
            newbeziers += news

    def __and__(self, other: JordanCurve) -> FrozenSet[Tuple[float]]:
        """
        Given two jordan curves, this functions returns the intersection
        between these two jordan curves
        Returns empty tuple if the curves don't intersect each other
        """
        assert isinstance(other, JordanCurve)
        selfsegs = list(self.segments)
        othesegs = list(other.segments)
        for bezier in selfsegs:
            bezier.clean()
        for bezier in othesegs:
            bezier.clean()
        bandb = IntersectionBeziers.intersection_bezier
        intersections = set()
        for sbezier in selfsegs:
            umin, umax = sbezier.knotvector.limits
            for obezier in othesegs:
                vmin, vmax = obezier.knotvector.limits
                inters = bandb(sbezier.ctrlpoints, obezier.ctrlpoints)
                # Scale inters from [0, 1] to respective intervals
                for ui, vj in inters:
                    ui = (1 - ui) * umin + ui * umax
                    vj = (1 - vj) * vmin + vj * vmax
                    intersections.add((ui, vj))

        return frozenset(intersections)

    @property
    def ctrlpoints(self) -> Tuple[Point2D]:
        """
        Returns a tuple of control points
        """
        return tuple(self.__full_curve.ctrlpoints)

    @property
    def vertices(self) -> Tuple[Point2D]:
        """
        Returns a tuple of non repeted points
        """
        allpoints = []
        for point in self.ctrlpoints:
            if point not in allpoints:
                allpoints.append(point)
        return tuple(allpoints)

    @property
    def segments(self) -> Tuple[nurbs.Curve]:
        if self.__segments is None:
            self.__segments = self.__full_curve.split()
        return tuple([deepcopy(segm) for segm in self.__segments])

    def clean(self) -> None:
        self.__segments = None
        self.__full_curve.clean()

    def __str__(self) -> str:
        msg = f"Jordan Curve of degree {self.__full_curve.degree}\n"
        msg += str(self.ctrlpoints)
        return msg

    def __repr__(self) -> str:
        msg = "JordanCurve (deg %d, npts %d)"
        msg %= self.__full_curve.degree, self.__full_curve.npts
        return msg

    def __eq__(self, other: JordanCurve) -> bool:
        assert isinstance(other, JordanCurve)
        selcopy = self.copy()
        selcopy.clean()
        othcopy = other.copy()
        othcopy.clean()
        segms0 = selcopy.segments
        segms1 = othcopy.segments
        nsegments = len(segms0)
        if len(segms1) != nsegments:
            return False
        ctrlpts1 = segms1[0].ctrlpoints
        for index, segment0 in enumerate(segms0):
            ctrlpts0 = segment0.ctrlpoints
            for pt0, pt1 in zip(ctrlpts0, ctrlpts1):
                if pt0 != pt1:
                    break
            else:
                break
        for i, segment1 in enumerate(segms1):
            segment0 = segms0[(i + index) % nsegments]
            for pt0, pt1 in zip(segment0.ctrlpoints, segment1.ctrlpoints):
                if pt0 != pt1:
                    return False
        return True

    def __ne__(self, other: JordanCurve) -> bool:
        return not self.__eq__(other)

    def __invert__(self) -> JordanCurve:
        return self.copy().invert()

    def __contains__(self, point: Point2D) -> bool:
        point = Point2D(point)
        projection = nurbs.advanced.Projection.point_on_bezier
        for bezier in self.segments:
            tparam = projection(point, bezier)
            vector = point - bezier(tparam)[0]
            if vector.norm_square() < 1e-9:
                return True
        return False


class JordanPolygon(JordanCurve):
    def __init__(self, vertices: Tuple[Point2D]):
        """
        Init a closed jordan polygon.
        Valid case:
            vertices[0] != vertices[1]
        """
        if not isinstance(vertices, (list, tuple)):
            raise TypeError
        ctrlpoints = []
        for vertex in vertices:
            point = Point2D(vertex)
            ctrlpoints.append(point)
        ctrlpoints.append(ctrlpoints[0])
        npts = len(ctrlpoints)
        knotvector = (0,) + tuple(range(0, npts)) + (npts - 1,)
        knotvector = [Fraction(knot) for knot in knotvector]
        fullcurve = nurbs.Curve(knotvector)
        fullcurve.ctrlpoints = ctrlpoints
        super().__init__(fullcurve)
