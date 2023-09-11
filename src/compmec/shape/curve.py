from __future__ import annotations

import math
from fractions import Fraction
from functools import lru_cache
from typing import Any, Optional, Tuple, Union

import numpy as np

from compmec import nurbs
from compmec.shape.polygon import Point2D


class Math:
    @staticmethod
    @lru_cache(maxsize=None)
    def comb(n: int, i: int) -> int:
        """Computes binom(n, i)"""
        value = 1
        for j in range(n - i + 1, n + 1):
            value *= j
        for j in range(2, i + 1):
            value //= j
        return value

    @staticmethod
    def horner_method(node: float, coefs: Tuple[float]) -> float:
        """Computes the polynomial for given coefs

        coefs = [an, ..., a2, a1, a0]
        return a0 + a1*xi + a2*xi^2 + ... + an*xi^n
        """
        value = 0 * coefs[0]
        for coef in coefs:
            value *= node
            value += coef
        return value

    @staticmethod
    @lru_cache(maxsize=None)
    def bezier_caract_matrix(degree: int) -> Tuple[Tuple[int]]:
        """Returns the matrix [M] with the polynomial coefficients

        [M]_{ij} = coef(x^{degree-j} from B_{i,p}(x))

        p = degree

        B_{i, p} = binom(p, i) * (1-u)^{p-i} * u^i
                 = binom(p, i) * sum_{j=0}^{p-i} (-1)^{} * u^{i+(p-i)}

        """
        assert isinstance(degree, int)
        assert degree >= 0
        npts = degree + 1
        matrix = np.zeros((npts, npts), dtype="object")
        for i in range(npts):
            for j in range(degree - i + 1):
                val = Math.comb(degree, i) * Math.comb(degree - i, j)
                matrix[i, j] = -val if (degree + i + j) % 2 else val
        return tuple(tuple(line) for line in matrix)


class BaseCurve(object):
    def __call__(self, nodes: Union[float, Tuple[float]]) -> Union[Any, Tuple[Any]]:
        try:
            iter(nodes)
            return self.eval(nodes)
        except TypeError:
            return self.eval((nodes,))[0]


class BezierCurve(BaseCurve):
    """BezierCurve object"""

    def __init__(self, ctrlpoints: Tuple[Any]):
        self.ctrlpoints = ctrlpoints
        if self.degree > 2:
            raise NotImplementedError

    @property
    def degree(self) -> int:
        return self.npts - 1

    @property
    def npts(self) -> int:
        return len(self.ctrlpoints)

    @property
    def ctrlpoints(self) -> Tuple[Point2D]:
        return self.__ctrlpoints

    @ctrlpoints.setter
    def ctrlpoints(self, other: Tuple[Any]):
        self.__ctrlpoints = tuple(other)

    def __str__(self) -> str:
        msg = f"BezierCurve of degree {self.degree} and "
        msg += "control points {str(self.ctrlpoints)}"
        return msg

    def __repr__(self) -> str:
        return self.__str__()

    def eval(self, nodes: Tuple[float]) -> Tuple[Any]:
        """
        Evaluates

                              [ 1 ]
        [P0, ..., Pn] * [M] * [   ]
                              [x^n]

        """
        iter(nodes)
        results = [0] * len(nodes)
        matrix = Math.bezier_caract_matrix(self.degree)
        canon_pts = np.dot(self.ctrlpoints, matrix)
        for k, node in enumerate(nodes):
            results[k] = Math.horner_method(node, canon_pts)
        return tuple(results)

    def derivate(self, times: Optional[int] = 1) -> BezierCurve:
        assert isinstance(times, int)
        assert times > 0
        matrix = Derivate.non_rational_bezier(self.degree, times)
        new_ctrlpoints = np.dot(matrix, self.ctrlpoints)
        return self.__class__(new_ctrlpoints)

    def clean(self, tolerance: Optional[float] = 1e-9):
        """Reduces at maximum the degree of the bezier curve.

        If ``tolerance = None``, then it don't verify the error
        and stops with a bezier curve of degree ``1`` (segment)

        """
        degree = self.degree
        times = 0
        points = self.ctrlpoints
        while degree - times > 1:
            _, materror = Operations.degree_decrease(degree, times + 1)
            error = np.dot(points, np.dot(materror, points))
            if tolerance and error > tolerance:
                break
            times += 1
        if times == 0:
            return
        mattrans, _ = Operations.degree_decrease(degree, times)
        self.ctrlpoints = tuple(np.dot(mattrans, points))


class PlanarCurve(BaseCurve):
    def __init__(self, ctrlpoints: Tuple[Point2D]):
        ctrlpoints = list(ctrlpoints)
        for i, point in enumerate(ctrlpoints):
            ctrlpoints[i] = Point2D(point)
        self.__planar = BezierCurve(ctrlpoints)

    def __str__(self) -> str:
        msg = f"Planar curve of degree {self.degree} and "
        msg += f"control points {self.ctrlpoints}"
        return msg

    def __repr__(self) -> str:
        msg = f"PlanarCurve (deg {self.degree}, npts {self.npts})"
        return msg

    def __eq__(self, other: PlanarCurve) -> bool:
        assert isinstance(other, PlanarCurve)
        if self.degree != other.degree:
            return False
        for pta, ptb in zip(self.ctrlpoints, other.ctrlpoints):
            if pta != ptb:
                return False
        return True

    def __ne__(self, other: PlanarCurve) -> bool:
        return not self.__eq__(other)

    def __iadd__(self, point: Point2D) -> PlanarCurve:
        point = Point2D(point)
        for ctrlpoint in self.ctrlpoints:
            ctrlpoint += point
        return self

    def __isub__(self, point: Point2D) -> PlanarCurve:
        return self.__iadd__(-Point2D(point))

    def __contains__(self, point: Point2D) -> bool:
        point = Point2D(point)
        pta, ptb = self.box()
        dx, dy = 1e-6, 1e-6  # Tolerance
        if point[0] < pta[0] - dx or point[1] < pta[1] - dy:
            return False
        if ptb[0] + dx < point[0] or ptb[1] + dy < point[1]:
            return False
        self -= point
        print("After moved : ")
        print(self)
        params = Projection.origin_on_curve(self)
        print("params = ", params)
        vectors = self.eval(params)
        self += point
        distances = tuple(abs(vector) for vector in vectors)
        print("vectors = ")
        print(vectors)
        for dist in distances:
            if dist < 1e-6:  # Tolerance
                return True
        return False

    @property
    def degree(self) -> int:
        return self.__planar.degree

    @property
    def npts(self) -> int:
        return self.__planar.npts

    @property
    def ctrlpoints(self) -> Tuple[Point2D]:
        return self.__planar.ctrlpoints

    @property
    def weights(self) -> Tuple[float]:
        raise NotImplementedError

    def eval(self, nodes: Tuple[float]) -> Tuple[Any]:
        return self.__planar.eval(nodes)

    def derivate(self, times: Optional[int] = 1) -> PlanarCurve:
        assert isinstance(times, int)
        assert times > 0
        matrix = Derivate.non_rational_bezier(self.degree, times)
        new_ctrlpoints = np.dot(matrix, self.ctrlpoints)
        return self.__class__(new_ctrlpoints)

    def box(self) -> Tuple[Point2D]:
        """Returns two points which defines the minimal exterior rectangle

        Returns the pair (A, B) with A[0] <= B[0] and A[1] <= B[1]
        """
        xmin = min(point[0] for point in self.ctrlpoints)
        xmax = max(point[0] for point in self.ctrlpoints)
        ymin = min(point[1] for point in self.ctrlpoints)
        ymax = max(point[1] for point in self.ctrlpoints)
        return Point2D(xmin, ymin), Point2D(xmax, ymax)

    def clean(self, tolerance: Optional[float] = 1e-9):
        """Reduces at maximum the degree of the bezier curve.

        If ``tolerance = None``, then it don't verify the error
        and stops with a bezier curve of degree ``1`` (segment)

        """
        self.__planar.clean(tolerance)

    def copy(self) -> PlanarCurve:
        ctrlpoints = tuple(point.copy() for point in self.ctrlpoints)
        return self.__class__(ctrlpoints)

    def invert(self) -> PlanarCurve:
        points = self.ctrlpoints
        npts = len(points)
        new_ctrlpoints = tuple(points[i] for i in range(npts - 1, -1, -1))
        self.__planar.ctrlpoints = new_ctrlpoints
        return self

    def split(self, nodes: Tuple[float]) -> Tuple[PlanarCurve]:
        knotvector = nurbs.GeneratorKnotVector.bezier(self.degree)
        curve = nurbs.Curve(knotvector, self.ctrlpoints)
        beziers = curve.split(nodes)
        planars = tuple(PlanarCurve(bezier.ctrlpoints) for bezier in beziers)
        return planars


class Operations:
    @staticmethod
    @lru_cache(maxsize=None)
    def degree_increase(degree: int, times: int) -> Tuple[Tuple[float]]:
        """Returns the transformation matrix [T] such

        A(u) = sum_{i=0}^{p} B_{i,p}(u) * P_i
        C(u) = sum_{i=0}^{p+t} B_{i,p+t}(u) * Q_i
        [Q] = [T] * [P]

        [T].shape = (p+t+1, p+1)

        """
        assert isinstance(degree, int)
        assert degree >= 0
        assert isinstance(times, int)
        assert times > 0
        matrix = nurbs.heavy.Operations.degree_increase_bezier(degree, times)
        return tuple(tuple(line) for line in matrix)

    @staticmethod
    @lru_cache(maxsize=None)
    def degree_decrease(degree: int, times: int) -> Tuple[Tuple[Tuple[float]]]:
        """Returns the transformation and error matrix such

        A(u) = sum_{i=0}^{p} B_{i,p}(u) * P_i
        B(u) = sum_{i=0}^{p-t} B_{i,p-t}(u) * Q_i

        [Q] = [T] * [P]
        error = [P]^T * [E] * [P]

        """
        assert isinstance(degree, int)
        assert degree > 0
        assert isinstance(times, int)
        assert times > 0
        assert degree - times >= 0
        old_knotvector = nurbs.GeneratorKnotVector.bezier(degree, Fraction)
        new_knotvector = nurbs.GeneratorKnotVector.bezier(degree - times, Fraction)
        matrix, error = nurbs.heavy.LeastSquare.spline2spline(
            old_knotvector, new_knotvector
        )
        matrix = tuple(tuple(line) for line in matrix)
        error = tuple(tuple(line) for line in error)
        return matrix, error

    @staticmethod
    def split(degree: int, node: float) -> Tuple[Tuple[Tuple[float]]]:
        """Returns two matrices [T1], [T2] to split the curve at node

        A(u) -> C(u) and D(u)
        A(u) = sum_{i=0}^{p} B_{i,p}(u) * P_i
        C(u) = sum_{i=0}^{p} B_{i,p}(u) * Q_i
        D(u) = sum_{i=0}^{p} B_{i,p}(u) * R_i

        [Q] = [T1] * [P]
        [R] = [T2] * [P]

        """
        raise NotImplementedError

    @staticmethod
    def unite(degree: int, node: float) -> Tuple[Tuple[Tuple[float]]]:
        raise NotImplementedError


class Intersection:
    @staticmethod
    def bezier_and_bezier(
        curvea: PlanarCurve, curveb: PlanarCurve
    ) -> Tuple[Tuple[float]]:
        """Finds the pairs (u*, v*) such A(u*) = B(v*)

        Uses newton's method
        """
        raise NotImplementedError


class Projection:
    @staticmethod
    def origin_on_curve(curve: PlanarCurve) -> float:
        """Finds parameter u* such abs(C(u*)) is minimal

        Find the parameter by reducing the distance J(u)

        J(u) = abs(curve(u) - point)^2
        dJ/du = 0 ->  <C'(u), C(u) - P> = 0

        We find it by Newton's iteration


        """
        assert isinstance(curve, PlanarCurve)
        nsample = 2 + curve.degree
        usample = nurbs.heavy.NodeSample.closed_linspace(nsample)
        usample = Projection.newton_iteration(curve, usample)
        curvals = curve(usample)
        distans2 = tuple(curval.inner(curval) for curval in curvals)
        mindist2 = min(distans2)
        params = []
        for i, dist2 in enumerate(distans2):
            if abs(dist2 - mindist2) < 1e-6:  # Tolerance
                params.append(usample[i])
        return tuple(params)

    @staticmethod
    def newton_iteration(curve: PlanarCurve, usample: Tuple[float]) -> Tuple[float]:
        """
        Uses newton iterations to find the parameters ``usample``
        such <C'(u), C(u)> = 0 stabilizes
        """
        dcurve = curve.derivate()
        ddcurve = dcurve.derivate()
        usample = list(usample)
        zero, one = Fraction(0), Fraction(1)
        for _ in range(10):  # Number of iterations
            curvals = curve(usample)
            dcurvals = dcurve(usample)
            ddcurvals = ddcurve(usample)
            for k, uk in enumerate(usample):
                curval = curvals[k]
                deriva = dcurvals[k]
                fuk = deriva.inner(curval)
                dfuk = ddcurvals[k].inner(curval)
                dfuk += deriva.inner(deriva)
                newu = uk - fuk / dfuk
                usample[k] = min(one, max(newu, zero))
            usample = list(set(usample))
            if len(usample) == 1:
                break
        return usample


class Derivate:
    @lru_cache(maxsize=None)
    @staticmethod
    def non_rational_bezier_once(degree: int) -> Tuple[Tuple[float]]:
        """Derivate a bezier curve of given degree

        Returns the transformation matrix [T] such

        A(u) = sum_{i=0}^{p} B_{i,p}(u) * P_i
        C(u) = sum_{i=0}^{q} B_{i,q}(u) * Q_i

        C(u) = (d^t A)/(du^t)

        [Q] = [T] * [P]
        [T].shape = (q+1, p+1)
        q = p - 1
        """
        knotvector = nurbs.GeneratorKnotVector.bezier(degree, Fraction)
        matrix = nurbs.heavy.Calculus.derivate_nonrational_bezier(knotvector)
        return matrix

    @staticmethod
    def non_rational_bezier(degree: int, times: int) -> Tuple[Tuple[float]]:
        """Derivate a bezier curve of given degree

        Returns the transformation matrix [T] such

        A(u) = sum_{i=0}^{p} B_{i,p}(u) * P_i
        C(u) = sum_{i=0}^{q} B_{i,q}(u) * Q_i

        C(u) = (d^t A)/(du^t)

        [Q] = [T] * [P]
        [T].shape = (q+1, p+1)
        """
        assert isinstance(degree, int)
        assert degree >= 0
        assert isinstance(times, int)
        assert times > 0
        if degree - times < 0:
            return ((0,) * (degree + 1),)
        matrix = np.eye(degree + 1, dtype="int64")
        for i in range(times):
            derive = Derivate.non_rational_bezier_once(degree - i)
            matrix = np.dot(derive, matrix)
        return tuple(tuple(line) for line in matrix)

    @staticmethod
    def rational_bezier(degree: int, times: int):
        raise NotImplementedError


class Integrate:
    """
    This class compute the integral of a function f(x, y)
    over a bezier curve.
    It can be used in three forms:

        * int_C f(x, y) abs(ds)
        * int_C < f(x, y), ds >
        * int_C f(x, y) x ds
    """

    @staticmethod
    def horizontal(
        curve: PlanarCurve,
        expx: Optional[int] = 0,
        expy: Optional[int] = 0,
        nnodes: Optional[int] = None,
    ):
        """Computes the integral I

        I = int_{0}^{1} x^expx * y^expy * dx

        """
        assert isinstance(curve, PlanarCurve)
        assert isinstance(expx, int)
        assert isinstance(expy, int)
        if nnodes is None:
            nnodes = 3 + expx + expy + curve.degree
        assert isinstance(nnodes, int)
        assert nnodes >= 0
        assert expx >= 0
        assert expy >= 0
        dcurve = curve.derivate()
        nodes = nurbs.heavy.NodeSample.open_linspace(nnodes)
        poids = nurbs.heavy.IntegratorArray.open_newton_cotes(nnodes)
        points = curve(nodes)
        xvals = tuple(point[0] ** expx for point in points)
        yvals = tuple(point[0] ** expy for point in points)
        dxvals = tuple(point[0] for point in dcurve(nodes))
        funcvals = tuple(map(np.prod, (xvals, yvals, dxvals)))
        return np.inner(poids, funcvals)

    @staticmethod
    def vertical(
        curve: PlanarCurve,
        expx: Optional[int] = 0,
        expy: Optional[int] = 0,
        nnodes: Optional[int] = None,
    ):
        """Computes the integral I

        I = int_{0}^{1} x^expx * y^expy * dy

        """
        assert isinstance(curve, PlanarCurve)
        assert isinstance(expx, int)
        assert isinstance(expy, int)
        if nnodes is None:
            nnodes = 3 + expx + expy + curve.degree
        assert isinstance(nnodes, int)
        assert nnodes >= 0
        assert expx >= 0
        assert expy >= 0
        dcurve = curve.derivate()
        nodes = nurbs.heavy.NodeSample.open_linspace(nnodes)
        poids = nurbs.heavy.IntegratorArray.open_newton_cotes(nnodes)
        points = curve(nodes)
        xvals = tuple(point[0] ** expx for point in points)
        yvals = tuple(point[0] ** expy for point in points)
        dxvals = tuple(point[0] for point in dcurve(nodes))
        funcvals = tuple(map(np.prod, (xvals, yvals, dxvals)))
        return np.inner(poids, funcvals)

    @staticmethod
    def winding_number(curve: PlanarCurve, nnodes: Optional[int] = None) -> float:
        """
        Computes the integral for a bezier curve of given control points
        """
        assert isinstance(curve, PlanarCurve)
        if nnodes is None:
            nnodes = 5 + curve.degree
        assert isinstance(nnodes, int)
        curvex = BezierCurve(point[0] for point in curve.ctrlpoints)
        curvey = BezierCurve(point[1] for point in curve.ctrlpoints)
        dcurvex = curvex.derivate()
        dcurvey = curvey.derivate()
        nodes = nurbs.heavy.NodeSample.open_linspace(nnodes)
        poids = nurbs.heavy.IntegratorArray.open_newton_cotes(nnodes)
        xvals = np.array(curvex(nodes))
        yvals = np.array(curvey(nodes))
        dxvals = np.array(dcurvex(nodes))
        dyvals = np.array(dcurvey(nodes))
        numer = xvals * dyvals - yvals * dxvals
        denom = xvals**2 + yvals**2
        funcvals = tuple(numer / denom)
        integral = np.inner(poids, funcvals)
        return integral / math.tau

    @staticmethod
    def lenght(curve: PlanarCurve, nnodes: int = 5):
        """Computes the integral I

            I = int_{C} x^a * y^b * ds

        Given the control points P of a bezier curve C(u) of
        degree p

            C(u) = sum_{i=0}^{p} B_{i,p}(u) * P_i

            B_{i,p} = binom(p, i)*(1-u)^{p-i} * u^i

            I = int_{0}^{1} x(u)^a * y(u)^b * abs(C'(u)) * du

        """
        assert isinstance(curve, PlanarCurve)
        assert isinstance(nnodes, int)
        assert nnodes >= 0
        dcurve = curve.derivate()
        nodes = nurbs.heavy.NodeSample.open_linspace(nnodes)
        poids = nurbs.heavy.IntegratorArray.open_newton_cotes(nnodes)
        funcvals = tuple(abs(point) for point in dcurve(nodes))
        val = np.inner(poids, funcvals)
        return val

    @staticmethod
    def area(curve: PlanarCurve, nnodes: Optional[int] = None):
        """Computes the integral I

        I = int_0^1 x * dy

        """
        return Integrate.vertical(curve, 1, 0, nnodes)
