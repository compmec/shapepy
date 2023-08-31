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
from compmec.shape import calculus
from compmec.shape.polygon import Point2D, Segment


def unite_beziers(beziers: Tuple[nurbs.Curve]) -> nurbs.Curve:
    """
    Given a tuple of bezier curves, it returns a unique closed curve
    """
    beziers = list(beziers)
    nbeziers = len(beziers)
    for i, bezier in enumerate(beziers):
        degree = bezier.degree
        knotvector = sorted((degree + 1) * (i, i + 1))
        new_bezier = bezier.__class__(knotvector)
        new_bezier.ctrlpoints = bezier.ctrlpoints
        new_bezier.weights = bezier.weights
        beziers[i] = new_bezier
    final_curve = beziers[0]
    for i in range(1, nbeziers):
        final_curve |= beziers[i]
    final_curve.clean()
    return final_curve


class IntersectionBeziers:
    tol_du = 1e-9  # tolerance convergence
    tol_norm = 1e-9  # tolerance convergence
    max_denom = math.ceil(1 / tol_du)

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
        tol_du = IntersectionBeziers.tol_du
        if IntersectionBeziers.is_equal_controlpoints(cptsa, cptsb):
            return ((None, None),)
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
                    if isinstance(ui, Fraction):
                        ui = ui.limit_denominator(IntersectionBeziers.max_denom)
                    if isinstance(vj, Fraction):
                        vj = vj.limit_denominator(IntersectionBeziers.max_denom)
                    ui = min(1, max(0, ui))
                    vj = min(1, max(0, vj))

                    if abs(oldui - ui) > tol_du:
                        continue
                    if abs(oldvj - vj) > tol_du:
                        continue
                    break
                if (0 < ui and ui < 1) or (0 < vj and vj < 1):
                    intersections.add((ui, vj))
        filter_inters = set()
        for ui, vj in intersections:
            for uk, vl in filter_inters:
                if abs(ui - uk) < tol_du and abs(vj - vl) < tol_du:
                    break
            else:
                filter_inters.add((ui, vj))
        for ui, vj in tuple(filter_inters):
            aui = IntersectionBeziers.eval_bezier(dega, ui)
            bvj = IntersectionBeziers.eval_bezier(degb, vj)
            pta = aui @ cptsa
            ptb = bvj @ cptsb
            norm = abs(pta - ptb)
            if norm > IntersectionBeziers.tol_norm:
                filter_inters.remove((ui, vj))
        filter_inters = tuple(filter_inters)
        return filter_inters


class JordanCurve:
    """
    Jordan Curve is an arbitrary closed curve which doesn't intersect itself.
    It stores a list of 'segments': Each 'segment' is a lambda function.
    """

    def __init__(self, curve: nurbs.Curve = None):
        self.__full_curve = None
        self.__segments = None
        if curve is not None:
            self.full_curve = curve
        self.__lenght = None

    @classmethod
    def from_full_curve(cls, curve: nurbs.Curve):
        instance = cls()
        instance.full_curve = curve
        return instance

    @classmethod
    def from_segments(cls, beziers: Tuple[nurbs.Curve]) -> JordanCurve:
        assert isinstance(beziers, (tuple, list))
        for bezier in beziers:
            assert isinstance(bezier, nurbs.Curve)
        instance = cls()
        instance.segments = beziers
        return instance

    @classmethod
    def from_vertices(cls, vertices: Tuple[Point2D]) -> JordanCurve:
        if not isinstance(vertices, (tuple, list)):
            raise TypeError
        vertices = list(vertices)
        for i, vertex in enumerate(vertices):
            vertices[i] = Point2D(vertex)
        nverts = len(vertices)
        vertices.append(vertices[0])
        knotvector = (0, 0, 1, 1)
        knotvector = tuple([Fraction(knot) for knot in knotvector])
        beziers = [0] * nverts
        for i in range(nverts):
            ctrlpoints = vertices[i : i + 2]
            new_bezier = nurbs.Curve(knotvector, ctrlpoints)
            beziers[i] = new_bezier
        return cls.from_segments(beziers)

    def copy(self) -> JordanCurve:
        return deepcopy(self)

    def clean(self) -> None:
        full_curve = self.full_curve
        full_curve.clean()
        self.full_curve = full_curve

    def move(self, point: Point2D) -> JordanCurve:
        segments = self.segments
        allctrlpoints = [bezier.ctrlpoints for bezier in segments]
        allctrlpoints = np.array(allctrlpoints)
        for bezier in segments:
            ctrlpoints = bezier.ctrlpoints
            for ctrlpoint in ctrlpoints:
                ctrlpoint.move(point)
            bezier.ctrlpoints = ctrlpoints
        self.segments = segments
        allctrlpoints = [bezier.ctrlpoints for bezier in self.segments]
        allctrlpoints = np.array(allctrlpoints)
        return self

    def scale(self, xscale: float, yscale: float) -> JordanCurve:
        float(xscale)
        float(yscale)
        segments = self.segments
        for bezier in segments:
            ctrlpoints = bezier.ctrlpoints
            for ctrlpoint in ctrlpoints:
                ctrlpoint.scale(xscale, yscale)
            bezier.ctrlpoints = ctrlpoints
        self.segments = segments
        return self

    def rotate(self, angle: float, degrees: bool = False) -> JordanCurve:
        float(angle)
        if degrees:
            angle *= np.pi / 180
        segments = self.segments
        for bezier in segments:
            ctrlpoints = bezier.ctrlpoints
            for ctrlpoint in ctrlpoints:
                ctrlpoint.rotate(angle)
            bezier.ctrlpoints = ctrlpoints
        self.segments = segments
        return self

    def invert(self) -> JordanCurve:
        full_curve = self.full_curve
        knotvector = full_curve.knotvector
        ctrlpoints = full_curve.ctrlpoints
        assert full_curve.weights is None
        umin, umax = knotvector.limits
        new_knotvector = [umin + umax - u for u in knotvector[::-1]]
        new_full_curve = full_curve.__class__(new_knotvector)
        new_full_curve.ctrlpoints = ctrlpoints[::-1]
        self.full_curve = new_full_curve
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
            bezleft, bezrigh = segment.split([node])
            new_segments[index + inserted] = bezleft
            new_segments.insert(index + inserted + 1, bezrigh)
            inserted += 1
        self.segments = tuple(new_segments)

    def points(self, subnpts: int = 2) -> Tuple[Point2D]:
        """
        Returns a list of points on the boundary.
        Main reason: plot the shape
        You can choose the precision by changing the ```subnpts``` parameter
        """
        full_curve = self.full_curve
        knots = full_curve.knotvector.knots
        usample = list(knots)
        chebynodes = 2 * np.arange(subnpts) + 1
        chebynodes = np.cos(chebynodes * np.pi / (2 * subnpts))
        chebynodes = (1 + chebynodes) / 2
        for umin, umax in zip(knots[:-1], knots[1:]):
            usample += list(umin + (umax - umin) * chebynodes)
        usample = tuple(sorted(usample))
        all_points = full_curve.eval(usample)
        return tuple(all_points)
    
    @property
    def lenght(self) -> float:
        if self.__lenght is None:
            function = calculus.BezierCurveIntegral.polynomial_scalar_bezier
            segments = self.segments
            self.__lenght = 0
            for bezier in segments:
                self.__lenght += function((0, 0), bezier.ctrlpoints)
        return self.__lenght

    @property
    def full_curve(self) -> Tuple[Point2D]:
        """
        Returns a tuple of control points
        """
        if self.__full_curve is None:
            self.__full_curve = unite_beziers(self.segments)
        return self.__full_curve

    @property
    def segments(self) -> Tuple[nurbs.Curve]:
        if self.__segments is None:
            if self.__full_curve is None:
                raise ValueError
            self.segments = self.full_curve.split()
        return tuple(self.__segments)

    @property
    def vertices(self) -> Tuple[Point2D]:
        """
        Returns a tuple of non repeted points
        """
        allpoints = []
        for point in self.full_curve.ctrlpoints:
            if point not in allpoints:
                allpoints.append(point)
        return tuple(allpoints)

    @full_curve.setter
    def full_curve(self, other: nurbs.Curve):
        if not isinstance(other, nurbs.Curve):
            raise TypeError
        assert other.ctrlpoints[0] == other.ctrlpoints[-1]
        self.__segments = None
        self.__lenght = None
        degree = other.degree
        knots = other.knotvector.knots
        for knot in knots[1:-1]:
            mult = other.knotvector.mult(knot)
            assert mult <= degree
        self.__full_curve = other

    @segments.setter
    def segments(self, other: Tuple[nurbs.Curve]):
        assert isinstance(other, (tuple, list))
        for segment in other:
            if not isinstance(segment, nurbs.Curve):
                raise TypeError
        ncurves = len(other)
        for i in range(ncurves - 1):
            end_point = other[i].ctrlpoints[-1]
            start_point = other[i + 1].ctrlpoints[0]
            assert np.all(start_point == end_point)
        for segment in other:
            segment.degree_clean()
        self.__full_curve = None
        self.__lenght = None
        segments = []
        for bezier in other:
            npts = bezier.knotvector.npts
            knotvector = tuple(npts * [Fraction(0)] + npts * [Fraction(1)])
            new_bezier = bezier.__class__(knotvector)
            ctrlpoints = [Point2D(point) for point in bezier.ctrlpoints]
            new_bezier.ctrlpoints = ctrlpoints
            new_bezier.weights = bezier.weights
            segments.append(new_bezier)
        self.__segments = tuple(segments)

    def __and__(self, other: JordanCurve) -> Tuple[Tuple[int, int, float, float]]:
        """
        Given two jordan curves, this functions returns the intersection
        between these two jordan curves
        Returns empty tuple if the curves don't intersect each other
        """
        return self.intersection(other, end_points=True)

    def __str__(self) -> str:
        msg = f"Jordan Curve of degree {self.full_curve.degree} and vertices\n"
        msg += str(self.vertices)
        return msg

    def __repr__(self) -> str:
        msg = "JordanCurve (deg %d, npts %d)"
        msg %= self.full_curve.degree, self.full_curve.npts
        return msg

    def __eq__(self, other: JordanCurve) -> bool:
        assert isinstance(other, JordanCurve)
        selcopy = self.copy()
        othcopy = other.copy()
        segms0 = list(selcopy.segments)
        segms1 = list(othcopy.segments)
        if len(segms0) != len(segms1):
            selcopy.clean()
            othcopy.clean()
            segms0 = list(selcopy.segments)
            segms1 = list(othcopy.segments)
            if len(segms0) != len(segms1):
                return False
        for i, segi in enumerate(segms0):
            segi.clean()
            segms0[i] = segi
        for i, segi in enumerate(segms1):
            segi.clean()
            segms1[i] = segi
        ctrlpts1 = segms1[0].ctrlpoints
        for index, segment0 in enumerate(segms0):
            ctrlpts0 = segment0.ctrlpoints
            if len(ctrlpts0) != len(ctrlpts1):
                continue
            for pt0, pt1 in zip(ctrlpts0, ctrlpts1):
                if pt0 != pt1:
                    break
            else:
                break
        nsegments = len(segms0)
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
        """
        Tells if the point is on the boundary
        """
        point = Point2D(point)
        projection = nurbs.advanced.Projection.point_on_bezier
        for bezier in self.segments:
            tparam = projection(point, bezier)
            vector = point - bezier(tparam)[0]
            if vector.norm_square() < 1e-9:
                return True
        return False
    
    def __abs__(self) -> JordanCurve:
        """
        Returns the same curve, but in positive direction
        """
        internal_area = calculus.JordanCurveIntegral.area(self.segments)
        return self.copy() if internal_area > 0 else (~self)

    def intersection(
        self, other: JordanCurve, end_points=False
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
        bandb = IntersectionBeziers.intersection_bezier
        intersections = set()
        for ai, sbezier in enumerate(self.segments):
            for bj, obezier in enumerate(other.segments):
                inters = bandb(sbezier.ctrlpoints, obezier.ctrlpoints)
                for item in inters:
                    ui, vj = item
                    intersections.add((ai, bj, ui, vj))
        if not end_points:
            for ai, bi, ui, vi in tuple(intersections):
                if (0 < ui and ui < 1) or (0 < vi and vi < 1):
                    continue
                intersections.remove((ai, bi, ui, vi))
        return tuple(sorted(intersections))
