"""
File that defines the classes

* Math: to store mathematical methods used
* BaseCurve: Defines a parent of BezierCurve and Segment
* Operations
* Intersection
* Projection
* Derivate
* IntegratePlanar
"""

from __future__ import annotations

import math
from copy import copy
from fractions import Fraction
from typing import Iterable, Optional, Tuple, Union

import pynurbs

from shapepy.geometry.box import Box
from shapepy.geometry.point import Point2D

from ..scalar.bezier import Bezier, clean, derivate, split
from ..scalar.quadrature import closed_linspace
from ..scalar.reals import Real
from ..tools import Is, To, vectorize


class Segment:
    """
    Defines a planar curve in the plane,
    that contains a bezier curve inside it
    """

    def __init__(self, ctrlpoints: Iterable[Point2D]):
        if not Is.iterable(ctrlpoints):
            raise ValueError("Control points must be iterable")
        self.ctrlpoints = list(map(To.point, ctrlpoints))

    def __or__(self, other: Segment) -> Segment:
        """Computes the union of two bezier curves"""
        assert Is.instance(other, Segment)
        assert self.degree == other.degree
        assert self.ctrlpoints[-1] == other.ctrlpoints[0]
        # Last point of first derivative
        dapt = self.ctrlpoints[-1] - self.ctrlpoints[-2]
        # First point of first derivative
        dbpt = other.ctrlpoints[1] - other.ctrlpoints[0]
        if abs(dapt ^ dbpt) > 1e-6:
            node = To.rational(1, 2)
        else:
            dsumpt = dapt + dbpt
            denomin = dsumpt @ dsumpt
            node = dapt @ dsumpt / denomin
        knotvectora = pynurbs.GeneratorKnotVector.bezier(
            self.degree, To.rational
        )
        knotvectora.scale(node)
        knotvectorb = pynurbs.GeneratorKnotVector.bezier(
            other.degree, To.rational
        )
        knotvectorb.scale(1 - node).shift(node)
        newknotvector = tuple(knotvectora) + tuple(
            knotvectorb[self.degree + 1 :]
        )
        finalcurve = pynurbs.Curve(newknotvector)
        finalcurve.ctrlpoints = tuple(self.ctrlpoints) + tuple(
            other.ctrlpoints
        )
        finalcurve.knot_clean((node,))
        if finalcurve.degree + 1 != finalcurve.npts:
            raise ValueError("Union is not a bezier curve!")
        return self.__class__(finalcurve.ctrlpoints)

    def __and__(self, other: Segment) -> Union[None, Tuple[Tuple[int]]]:
        """Computes the intersection between two Planar Curves

        Returns None if there's no intersection

        Returns tuple() if curves are equal

        Returns [(a0, b0), (a1, b1), ...]
        Which self(ai) == other(bi)
        """
        if self.box() & other.box() is None:
            return None
        if self == other:
            return tuple()
        if self.degree == 1 and other.degree == 1:
            params = Intersection.lines(self, other)
            return (params,) if len(params) != 0 else tuple()
        usample = list(closed_linspace(self.npts + 3))
        vsample = list(closed_linspace(other.npts + 3))
        pairs = []
        for ui in usample:
            pairs += [(ui, vj) for vj in vsample]
        for _ in range(3):
            pairs = Intersection.bezier_and_bezier(self, other, pairs)
            pairs.insert(0, (0, 0))
            pairs.insert(0, (0, 1))
            pairs.insert(0, (1, 0))
            pairs.insert(0, (1, 1))
            # Filter values by distance of points
            tol_norm = 1e-6
            pairs = Intersection.filter_distance(self, other, pairs, tol_norm)
            # Filter values by distance abs(ui-uj, vi-vj)
            tol_du = 1e-6
            pairs = Intersection.filter_parameters(pairs, tol_du)
        return tuple(pairs)

    def __str__(self) -> str:
        msg = f"Planar curve of degree {self.degree} and "
        msg += f"control points {self.ctrlpoints}"
        return msg

    def __repr__(self) -> str:
        msg = f"Segment (deg {self.degree})"
        return msg

    def __eq__(self, other: Segment) -> bool:
        assert Is.instance(other, Segment)
        if self.npts != other.npts:
            return False
        for pta, ptb in zip(self.ctrlpoints, other.ctrlpoints):
            if pta != ptb:
                return False
        return True

    def __contains__(self, point: Point2D) -> bool:
        point = To.point(point)
        if point not in self.box():
            return False
        params = Projection.point_on_curve(point, self)
        vectors = tuple(cval - point for cval in self(params))
        distances = tuple(abs(vector) for vector in vectors)
        for dist in distances:
            if dist < 1e-6:  # Tolerance
                return True
        return False

    @vectorize(1, 0)
    def __call__(self, node: Real) -> Point2D:
        planar = Bezier(self.ctrlpoints)
        return planar(node)

    @property
    def degree(self) -> int:
        """
        The degree of the bezier curve

        Degree = 1 -> Linear curve
        Degree = 2 -> Quadratic
        """
        return self.npts - 1

    @property
    def npts(self) -> int:
        """
        The number of control points used by the curve
        """
        return len(self.ctrlpoints)

    @property
    def ctrlpoints(self) -> Tuple[Point2D, ...]:
        """
        The control points that defines the planar curve
        """
        return self.__ctrlpoints

    @ctrlpoints.setter
    def ctrlpoints(self, points: Iterable[Point2D]):
        self.__ctrlpoints = list(map(To.point, points))
        self.__planar = Bezier(self.ctrlpoints)

    def derivate(self, times: Optional[int] = 1) -> Segment:
        """
        Gives the first derivative of the curve
        """
        if not Is.integer(times) or times <= 0:
            raise ValueError(f"Times must be integer >= 1, not {times}")
        newplanar = derivate(Bezier(self.ctrlpoints), times)
        return self.__class__(newplanar)

    def box(self) -> Box:
        """Returns two points which defines the minimal exterior rectangle

        Returns the pair (A, B) with A[0] <= B[0] and A[1] <= B[1]
        """
        xmin = min(point[0] for point in self.ctrlpoints)
        xmax = max(point[0] for point in self.ctrlpoints)
        ymin = min(point[1] for point in self.ctrlpoints)
        ymax = max(point[1] for point in self.ctrlpoints)
        return Box(Point2D(xmin, ymin), Point2D(xmax, ymax))

    def clean(self, tolerance: Optional[float] = 1e-9) -> Segment:
        """Reduces at maximum the degree of the bezier curve.

        If ``tolerance = None``, then it don't verify the error
        and stops with a bezier curve of degree ``1`` (linear segment)

        """
        newplanar = clean(Bezier(self.ctrlpoints))
        if newplanar.degree != self.degree:
            self.ctrlpoints = tuple(newplanar)
        return self

    def __copy__(self) -> Segment:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> Segment:
        ctrlpoints = tuple(copy(point) for point in self.ctrlpoints)
        return self.__class__(ctrlpoints)

    def invert(self) -> Segment:
        """
        Inverts the direction of the curve.
        If the curve is clockwise, it becomes counterclockwise
        """
        points = tuple(self.ctrlpoints)
        self.ctrlpoints = (points[i] for i in range(self.degree, -1, -1))
        return self

    def split(self, nodes: Tuple[float]) -> Tuple[Segment]:
        """
        Splits the curve into more segments
        """
        beziers = split(self.__planar, nodes)
        return tuple(map(Segment, beziers))


class Intersection:
    """
    Defines the methods used to compute the intersection between curves
    """

    tol_du = 1e-9  # tolerance convergence
    tol_norm = 1e-9  # tolerance convergence
    max_denom = math.ceil(1 / tol_du)

    @staticmethod
    def lines(curvea: Segment, curveb: Segment) -> Tuple[float]:
        """Finds the intersection of two line segments"""
        assert curvea.degree == 1
        assert curveb.degree == 1
        pta0, pta1 = curvea.ctrlpoints
        ptb0, ptb1 = curveb.ctrlpoints
        vector0 = pta1 - pta0
        vector1 = ptb1 - ptb0
        diff0 = ptb0 - pta0
        denom = vector0 ^ vector1
        if denom != 0:  # Lines are not parallel
            param0 = (diff0 ^ vector1) / denom
            param1 = (diff0 ^ vector0) / denom
            if param0 < 0 or 1 < param0:
                return tuple()
            if param1 < 0 or 1 < param1:
                return tuple()
            return param0, param1
        # Lines are parallel
        if vector0 ^ diff0 != 0:
            return tuple()  # Parallel, but not colinear
        return tuple()

    # pylint: disable=too-many-locals
    @staticmethod
    def bezier_and_bezier(
        curvea: Segment, curveb: Segment, pairs: Tuple[Tuple[float]]
    ) -> Tuple[Tuple[float]]:
        """Finds all the pairs (u*, v*) such A(u*) = B(v*)

        Uses newton's method
        """
        dcurvea = curvea.derivate()
        ddcurvea = dcurvea.derivate()
        dcurveb = curveb.derivate()
        ddcurveb = dcurveb.derivate()

        # Start newton iteration
        for _ in range(20):  # Number of newton iteration
            new_pairs = set()
            for u, v in pairs:
                ssu = curvea(u)
                dsu = dcurvea(u)
                ddu = ddcurvea(u)
                oov = curveb(v)
                dov = dcurveb(v)
                ddv = ddcurveb(v)

                dif = ssu - oov
                vect0 = dsu @ dif
                vect1 = -dov @ dif
                mat00 = dsu @ dsu + ddu @ dif
                mat01 = -dsu @ dov
                mat11 = dov @ dov - ddv @ dif
                deter = mat00 * mat11 - mat01**2
                if abs(deter) < 1e-6:
                    continue
                newu = u - (mat11 * vect0 - mat01 * vect1) / deter
                newv = v - (mat00 * vect1 - mat01 * vect0) / deter
                pair = (min(1, max(0, newu)), min(1, max(0, newv)))
                new_pairs.add(pair)
            pairs = list(new_pairs)
            for i, (ui, vi) in enumerate(pairs):
                if Is.instance(ui, Fraction):
                    ui = ui.limit_denominator(10000)
                if Is.instance(vi, Fraction):
                    vi = vi.limit_denominator(10000)
                pairs[i] = (ui, vi)
        return pairs

    @staticmethod
    def filter_distance(
        curvea: Segment,
        curveb: Segment,
        pairs: Tuple[Tuple[float]],
        max_dist: float,
    ) -> Tuple[Tuple[float]]:
        """
        Filter the pairs values, since the intersection pair
        (0.5, 1) is almost the same as (1e-6, 0.99999)
        """
        pairs = list(pairs)
        index = 0
        while index < len(pairs):
            ui, vi = pairs[index]
            diff = curvea(ui) - curveb(vi)
            if abs(diff) < max_dist:
                index += 1
            else:
                pairs.pop(index)
        return tuple(pairs)

    @staticmethod
    def filter_parameters(
        pairs: Tuple[Tuple[float]], max_dist: float
    ) -> Tuple[Tuple[float]]:
        """
        Filter the parameters values, cause 0 is almost the same as 1e-6
        """
        pairs = list(pairs)
        index = 0
        while index < len(pairs):
            ui, vi = pairs[index]
            j = index + 1
            while j < len(pairs):
                uj, vj = pairs[j]
                dist2 = (ui - uj) ** 2 + (vi - vj) ** 2
                if dist2 < max_dist**2:
                    pairs.pop(j)
                else:
                    j += 1
            index += 1
        return tuple(pairs)


class Projection:
    """
    Defines the methods used to find the projection of a point into a curve
    """

    @staticmethod
    def point_on_curve(point: Point2D, curve: Segment) -> float:
        """Finds parameter u* such abs(C(u*)) is minimal

        Find the parameter by reducing the distance J(u)

        J(u) = abs(curve(u) - point)^2
        dJ/du = 0 ->  <C'(u), C(u) - P> = 0

        We find it by Newton's iteration


        """
        point = To.point(point)
        assert Is.instance(curve, Segment)
        nsample = 2 + curve.degree
        usample = closed_linspace(nsample)
        usample = Projection.newton_iteration(point, curve, usample)
        curvals = tuple(cval - point for cval in curve(usample))
        distans2 = tuple(curval @ curval for curval in curvals)
        mindist2 = min(distans2)
        params = []
        for i, dist2 in enumerate(distans2):
            if abs(dist2 - mindist2) < 1e-6:  # Tolerance
                params.append(usample[i])
        return tuple(params)

    # pylint: disable=too-many-locals
    @staticmethod
    def newton_iteration(
        point: Point2D, curve: Segment, usample: Tuple[float]
    ) -> Tuple[float]:
        """
        Uses newton iterations to find the parameters ``usample``
        such <C'(u), C(u) - P> = 0 stabilizes
        """
        point = To.point(point)
        dcurve = curve.derivate()
        ddcurve = dcurve.derivate()
        usample = list(usample)
        zero, one = To.rational(0), To.rational(1)
        for _ in range(10):  # Number of iterations
            curvals = tuple(cval - point for cval in curve(usample))
            dcurvals = dcurve(usample)
            ddcurvals = ddcurve(usample)
            for k, uk in enumerate(usample):
                curval = curvals[k]
                deriva = dcurvals[k]
                fuk = deriva @ curval
                dfuk = ddcurvals[k] @ curval
                dfuk += deriva @ deriva
                dfuk = dfuk if abs(dfuk) > 1e-6 else 1e-6
                newu = uk - fuk / dfuk
                usample[k] = min(one, max(newu, zero))
            usample = list(set(usample))
            if len(usample) == 1:
                break
        return usample
