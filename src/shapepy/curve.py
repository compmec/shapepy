"""
File that defines the classes

* Math: to store mathematical methods used
* BaseCurve: Defines a parent of BezierCurve and PlanarCurve
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
from typing import Any, Optional, Tuple, Union

import numpy as np
import pynurbs

from shapepy.polygon import Box, Point2D


class Math:
    """
    Defines the mathematical functions used for the package

    The methods are
    * comb
    * horner_method
    * bezier_caract_matrix
    * closed_linspace
    * open_linspace
    """

    __caract_matrix = {}

    @staticmethod
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
    def bezier_caract_matrix(degree: int) -> Tuple[Tuple[int]]:
        """Returns the matrix [M] with the polynomial coefficients

        [M]_{ij} = coef(x^{degree-j} from B_{i,p}(x))

        p = degree

        B_{i, p} = binom(p, i) * (1-u)^{p-i} * u^i
                 = binom(p, i) * sum_{j=0}^{p-i} (-1)^{} * u^{i+(p-i)}

        """
        assert isinstance(degree, int)
        assert degree >= 0
        if degree not in Math.__caract_matrix:
            matrix = np.zeros((degree + 1, degree + 1), dtype="object")
            for i in range(degree + 1):
                for j in range(degree - i + 1):
                    val = Math.comb(degree, i) * Math.comb(degree - i, j)
                    matrix[i, j] = -val if (degree + i + j) % 2 else val
            matrix = tuple(tuple(line) for line in matrix)
            Math.__caract_matrix[degree] = matrix
        return Math.__caract_matrix[degree]

    @staticmethod
    def closed_linspace(npts: int) -> Tuple[Fraction]:
        """
        Gives a set of numbers in interval [0, 1]

        Example
        -------
        >>> closed_linspace(2)
        (0, 1)
        >>> closed_linspace(3)
        (0, 0.5, 1)
        >>> closed_linspace(4)
        (0, 0.33, 0.66, 1)
        >>> closed_linspace(5)
        (0, 0.25, 0.5, 0.75, 1)
        """
        assert isinstance(npts, int)
        assert npts >= 2
        return tuple(Fraction(num, npts - 1) for num in range(npts))

    @staticmethod
    def open_linspace(npts: int) -> Tuple[Fraction]:
        """
        Gives a set of numbers in interval (0, 1)

        Example
        -------
        >>> open_linspace(1)
        (0.5, )
        >>> open_linspace(2)
        (0.33, 0.66)
        >>> open_linspace(3)
        (0.25, 0.50, 0.75)
        """
        assert isinstance(npts, int)
        assert npts >= 1
        return tuple(
            Fraction(num) / (2 * npts) for num in range(1, 2 * npts, 2)
        )


class BezierCurve:
    """BezierCurve object"""

    def __init__(self, ctrlpoints: Tuple[Any]):
        self.ctrlpoints = ctrlpoints

    @property
    def degree(self) -> int:
        """
        The polynomial degree used by the Bezier Curve
        """
        return self.npts - 1

    @property
    def npts(self) -> int:
        """
        The number of control points used by the curve
        """
        return len(self.ctrlpoints)

    @property
    def ctrlpoints(self) -> Tuple[Point2D]:
        """
        The control points that defines the cdurve
        """
        return self.__ctrlpoints

    @ctrlpoints.setter
    def ctrlpoints(self, other: Tuple[Any]):
        self.__ctrlpoints = tuple(other)

    def __call__(
        self, nodes: Union[float, Tuple[float]]
    ) -> Union[Any, Tuple[Any]]:
        try:
            iter(nodes)
            return self.eval(nodes)
        except TypeError:
            return self.eval((nodes,))[0]

    def __str__(self) -> str:
        msg = f"BezierCurve of degree {self.degree} and "
        msg += f"control points {str(self.ctrlpoints)}"
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
        """
        Computes the derivative of the Bezier Curve
        """
        assert isinstance(times, int)
        assert times > 0
        matrix = Derivate.non_rational_bezier(self.degree, times)
        new_ctrlpoints = np.dot(matrix, self.ctrlpoints)
        return self.__class__(new_ctrlpoints)

    def clean(self, tolerance: Optional[float] = 1e-9) -> BezierCurve:
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
            return self
        mattrans, _ = Operations.degree_decrease(degree, times)
        self.ctrlpoints = tuple(np.dot(mattrans, points))
        return self

    def split(self, nodes: Tuple[float]) -> Tuple[BezierCurve]:
        """
        Splits the Bezier Curve into the given segments
        """
        knotvector = pynurbs.GeneratorKnotVector.bezier(self.degree)
        curve = pynurbs.Curve(knotvector, self.ctrlpoints)
        beziers = curve.split(nodes)
        planars = tuple(BezierCurve(bezier.ctrlpoints) for bezier in beziers)
        return planars


class PlanarCurve:
    """
    Defines a planar curve in the plane,
    that contains a bezier curve inside it
    """

    def __init__(self, ctrlpoints: Tuple[Point2D]):
        ctrlpoints = list(ctrlpoints)
        for i, point in enumerate(ctrlpoints):
            ctrlpoints[i] = Point2D(point)
        self.__planar = BezierCurve(ctrlpoints)

    def __or__(self, other: PlanarCurve) -> PlanarCurve:
        """Computes the union of two bezier curves"""
        assert isinstance(other, PlanarCurve)
        assert self.degree == other.degree
        assert self.ctrlpoints[-1] == other.ctrlpoints[0]
        # Last point of first derivative
        dapt = self.ctrlpoints[-1] - self.ctrlpoints[-2]
        # First point of first derivative
        dbpt = other.ctrlpoints[1] - other.ctrlpoints[0]
        if abs(dapt.cross(dbpt)) > 1e-6:
            node = Fraction(1, 2)
        else:
            dsumpt = dapt + dbpt
            denomin = dsumpt.inner(dsumpt)
            node = dapt.inner(dsumpt) / denomin
        knotvectora = pynurbs.GeneratorKnotVector.bezier(self.degree, Fraction)
        knotvectora.scale(node)
        knotvectorb = pynurbs.GeneratorKnotVector.bezier(
            other.degree, Fraction
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

    def __and__(self, other: PlanarCurve) -> Union[None, Tuple[Tuple[int]]]:
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
        usample = list(Math.closed_linspace(self.npts + 3))
        vsample = list(Math.closed_linspace(other.npts + 3))
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
        msg = f"PlanarCurve (deg {self.degree})"
        return msg

    def __eq__(self, other: PlanarCurve) -> bool:
        assert isinstance(other, PlanarCurve)
        if self.npts != other.npts:
            return False
        for pta, ptb in zip(self.ctrlpoints, other.ctrlpoints):
            if pta != ptb:
                return False
        return True

    def __contains__(self, point: Point2D) -> bool:
        point = Point2D(point)
        if point not in self.box():
            return False
        params = Projection.point_on_curve(point, self)
        vectors = tuple(cval - point for cval in self.eval(params))
        distances = tuple(abs(vector) for vector in vectors)
        for dist in distances:
            if dist < 1e-6:  # Tolerance
                return True
        return False

    def __call__(
        self, nodes: Union[float, Tuple[float]]
    ) -> Union[Any, Tuple[Any]]:
        try:
            iter(nodes)
            return self.eval(nodes)
        except TypeError:
            return self.eval((nodes,))[0]

    @property
    def degree(self) -> int:
        """
        The degree of the bezier curve

        Degree = 1 -> Linear curve
        Degree = 2 -> Quadratic
        """
        return self.__planar.degree

    @property
    def npts(self) -> int:
        """
        The number of control points used by the curve
        """
        return self.__planar.npts

    @property
    def ctrlpoints(self) -> Tuple[Point2D]:
        """
        The control points that defines the planar curve
        """
        return self.__planar.ctrlpoints

    @property
    def weights(self) -> Tuple[float]:
        """
        The weights of the control points, used for rational curves
        """
        raise NotImplementedError

    @ctrlpoints.setter
    def ctrlpoints(self, points: Tuple[Point2D]):
        points = list(points)
        for i, point in enumerate(points):
            points[i] = Point2D(point)
        self.__planar.ctrlpoints = points

    def eval(self, nodes: Tuple[float]) -> Tuple[Any]:
        """
        Evaluates the nodes, giving the points
        """
        return self.__planar.eval(nodes)

    def derivate(self, times: Optional[int] = 1) -> PlanarCurve:
        """
        Gives the first derivative of the curve
        """
        assert isinstance(times, int)
        assert times > 0
        matrix = Derivate.non_rational_bezier(self.degree, times)
        new_ctrlpoints = np.dot(matrix, self.ctrlpoints)
        return self.__class__(new_ctrlpoints)

    def box(self) -> Box:
        """Returns two points which defines the minimal exterior rectangle

        Returns the pair (A, B) with A[0] <= B[0] and A[1] <= B[1]
        """
        xmin = min(point[0] for point in self.ctrlpoints)
        xmax = max(point[0] for point in self.ctrlpoints)
        ymin = min(point[1] for point in self.ctrlpoints)
        ymax = max(point[1] for point in self.ctrlpoints)
        return Box(Point2D(xmin, ymin), Point2D(xmax, ymax))

    def clean(self, tolerance: Optional[float] = 1e-9) -> PlanarCurve:
        """Reduces at maximum the degree of the bezier curve.

        If ``tolerance = None``, then it don't verify the error
        and stops with a bezier curve of degree ``1`` (linear segment)

        """
        self.__planar.clean(tolerance)
        return self

    def __copy__(self) -> PlanarCurve:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> PlanarCurve:
        ctrlpoints = tuple(copy(point) for point in self.ctrlpoints)
        return self.__class__(ctrlpoints)

    def invert(self) -> PlanarCurve:
        """
        Inverts the direction of the curve.
        If the curve is clockwise, it becomes counterclockwise
        """
        points = self.ctrlpoints
        npts = len(points)
        new_ctrlpoints = tuple(points[i] for i in range(npts - 1, -1, -1))
        self.__planar.ctrlpoints = new_ctrlpoints
        return self

    def split(self, nodes: Tuple[float]) -> Tuple[PlanarCurve]:
        """
        Splits the curve into more segments
        """
        beziers = self.__planar.split(nodes)
        planars = tuple(PlanarCurve(bezier.ctrlpoints) for bezier in beziers)
        return planars


# pylint: disable=too-few-public-methods
class Operations:
    """
    Defines the operation of over the bezier curves
    """

    __degree_decre = {}

    @staticmethod
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
        if (degree, times) not in Operations.__degree_decre:
            old_knotvector = pynurbs.GeneratorKnotVector.bezier(
                degree, Fraction
            )
            new_knotvector = pynurbs.GeneratorKnotVector.bezier(
                degree - times, Fraction
            )
            matrix, error = pynurbs.heavy.LeastSquare.spline2spline(
                old_knotvector, new_knotvector
            )
            matrix = tuple(tuple(line) for line in matrix)
            error = tuple(tuple(line) for line in error)
            Operations.__degree_decre[(degree, times)] = matrix, error
        return Operations.__degree_decre[(degree, times)]


class Intersection:
    """
    Defines the methods used to compute the intersection between curves
    """

    tol_du = 1e-9  # tolerance convergence
    tol_norm = 1e-9  # tolerance convergence
    max_denom = math.ceil(1 / tol_du)

    @staticmethod
    def lines(curvea: PlanarCurve, curveb: PlanarCurve) -> Tuple[float]:
        """Finds the intersection of two line segments"""
        assert curvea.degree == 1
        assert curveb.degree == 1
        pta0, pta1 = curvea.ctrlpoints
        ptb0, ptb1 = curveb.ctrlpoints
        vector0 = pta1 - pta0
        vector1 = ptb1 - ptb0
        diff0 = ptb0 - pta0
        denom = vector0.cross(vector1)
        if denom != 0:  # Lines are not parallel
            param0 = diff0.cross(vector1) / denom
            param1 = diff0.cross(vector0) / denom
            if param0 < 0 or 1 < param0:
                return tuple()
            if param1 < 0 or 1 < param1:
                return tuple()
            return param0, param1
        # Lines are parallel
        if vector0.cross(diff0):
            return tuple()  # Parallel, but not colinear
        return tuple()

    # pylint: disable=too-many-locals
    @staticmethod
    def bezier_and_bezier(
        curvea: PlanarCurve, curveb: PlanarCurve, pairs: Tuple[Tuple[float]]
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
                vect0 = dsu.inner(dif)
                vect1 = -dov.inner(dif)
                mat00 = dsu.inner(dsu) + ddu.inner(dif)
                mat01 = -dsu.inner(dov)
                mat11 = dov.inner(dov) - ddv.inner(dif)
                deter = mat00 * mat11 - mat01**2
                if abs(deter) < 1e-6:
                    continue
                newu = u - (mat11 * vect0 - mat01 * vect1) / deter
                newv = v - (mat00 * vect1 - mat01 * vect0) / deter
                pair = (min(1, max(0, newu)), min(1, max(0, newv)))
                new_pairs.add(pair)
            pairs = list(new_pairs)
            for i, (ui, vi) in enumerate(pairs):
                if isinstance(ui, Fraction):
                    ui = ui.limit_denominator(10000)
                if isinstance(vi, Fraction):
                    vi = vi.limit_denominator(10000)
                pairs[i] = (ui, vi)
        return pairs

    @staticmethod
    def filter_distance(
        curvea: PlanarCurve,
        curveb: PlanarCurve,
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
    def point_on_curve(point: Point2D, curve: PlanarCurve) -> float:
        """Finds parameter u* such abs(C(u*)) is minimal

        Find the parameter by reducing the distance J(u)

        J(u) = abs(curve(u) - point)^2
        dJ/du = 0 ->  <C'(u), C(u) - P> = 0

        We find it by Newton's iteration


        """
        point = Point2D(point)
        assert isinstance(curve, PlanarCurve)
        nsample = 2 + curve.degree
        usample = Math.closed_linspace(nsample)
        usample = Projection.newton_iteration(point, curve, usample)
        curvals = tuple(cval - point for cval in curve(usample))
        distans2 = tuple(curval.inner(curval) for curval in curvals)
        mindist2 = min(distans2)
        params = []
        for i, dist2 in enumerate(distans2):
            if abs(dist2 - mindist2) < 1e-6:  # Tolerance
                params.append(usample[i])
        return tuple(params)

    # pylint: disable=too-many-locals
    @staticmethod
    def newton_iteration(
        point: Point2D, curve: PlanarCurve, usample: Tuple[float]
    ) -> Tuple[float]:
        """
        Uses newton iterations to find the parameters ``usample``
        such <C'(u), C(u) - P> = 0 stabilizes
        """
        point = Point2D(point)
        dcurve = curve.derivate()
        ddcurve = dcurve.derivate()
        usample = list(usample)
        zero, one = Fraction(0), Fraction(1)
        for _ in range(10):  # Number of iterations
            curvals = tuple(cval - point for cval in curve(usample))
            dcurvals = dcurve(usample)
            ddcurvals = ddcurve(usample)
            for k, uk in enumerate(usample):
                curval = curvals[k]
                deriva = dcurvals[k]
                fuk = deriva.inner(curval)
                dfuk = ddcurvals[k].inner(curval)
                dfuk += deriva.inner(deriva)
                dfuk = dfuk if abs(dfuk) > 1e-6 else 1e-6
                newu = uk - fuk / dfuk
                usample[k] = min(one, max(newu, zero))
            usample = list(set(usample))
            if len(usample) == 1:
                break
        return usample


class Derivate:
    """
    Defines the functions to derivate the bezier curve
    """

    __non_rat_bezier_once = {}

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
        if degree not in Derivate.__non_rat_bezier_once:
            knotvector = pynurbs.GeneratorKnotVector.bezier(degree, Fraction)
            matrix = pynurbs.heavy.Calculus.derivate_nonrational_bezier(
                knotvector
            )
            Derivate.__non_rat_bezier_once[degree] = tuple(matrix)
        return Derivate.__non_rat_bezier_once[degree]

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


class IntegratePlanar:
    """
    This class compute the integral of a function f(x, y)
    over a bezier curve.
    """

    @staticmethod
    def vertical(
        curve: PlanarCurve,
        expx: Optional[int] = 0,
        expy: Optional[int] = 0,
        nnodes: Optional[int] = None,
    ):
        """Computes the integral I

        I = int_C x^expx * y^expy * dy

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
        nodes = Math.open_linspace(nnodes)
        poids = pynurbs.heavy.IntegratorArray.open_newton_cotes(nnodes)
        points = curve(nodes)
        xvals = tuple(point[0] ** expx for point in points)
        yvals = tuple(point[1] ** expy for point in points)
        dyvals = tuple(point[1] for point in dcurve(nodes))
        funcvals = tuple(map(np.prod, zip(xvals, yvals, dyvals)))
        return np.inner(poids, funcvals)

    @staticmethod
    def polynomial(
        curve: PlanarCurve, expx: int, expy: int, nnodes: Optional[int] = None
    ):
        """
        Computes the integral

        I = int_C x^expx * y^expy * ds
        """
        assert isinstance(curve, PlanarCurve)
        if nnodes is None:
            nnodes = 3 + expx + expy + curve.degree
        assert isinstance(nnodes, int)
        assert nnodes >= 0
        assert expx == 0
        assert expy == 0
        dcurve = curve.derivate()
        nodes = Math.open_linspace(nnodes)
        poids = pynurbs.heavy.IntegratorArray.open_newton_cotes(nnodes)
        funcvals = tuple(abs(point) for point in dcurve(nodes))
        return float(np.inner(poids, funcvals))

    @staticmethod
    def lenght(curve: PlanarCurve, nnodes: int = 5):
        """Computes the integral I

            I = int_{C} ds

        Given the control points P of a bezier curve C(u) of
        degree p

            C(u) = sum_{i=0}^{p} B_{i,p}(u) * P_i

            I = int_{0}^{1} abs(C'(u)) * du

        """
        return IntegratePlanar.polynomial(curve, 0, 0, nnodes)

    @staticmethod
    def area(curve: PlanarCurve, nnodes: Optional[int] = None):
        """Computes the integral I

        I = int_0^1 x * dy

        """
        return IntegratePlanar.vertical(curve, 1, 0, nnodes)

    @staticmethod
    def winding_number_linear(
        pointa: Point2D, pointb: Point2D, center: Point2D
    ) -> float:
        """
        Computes the winding number defined by the given points.
        It means, it's the angle made between the vector
        (pointb - center) and (pointa - center)
        """
        anglea = np.arctan2(
            float(pointa[1] - center[1]), float(pointa[0] - center[0])
        )
        angleb = np.arctan2(
            float(pointb[1] - center[1]), float(pointb[0] - center[0])
        )
        wind = (angleb - anglea) / math.tau
        if abs(wind) < 0.5:
            return wind
        return wind - 1 if wind > 0 else wind + 1

    @staticmethod
    def winding_number(
        curve: PlanarCurve,
        center: Optional[Point2D] = (0.0, 0.0),
        nnodes: Optional[int] = None,
    ) -> float:
        """
        Computes the integral for a bezier curve of given control points
        """
        assert isinstance(curve, PlanarCurve)
        nnodes = curve.npts if nnodes is None else nnodes
        nodes = Math.closed_linspace(nnodes)
        total = 0
        for pair_node in zip(nodes[:-1], nodes[1:]):
            pointa, pointb = curve.eval(pair_node)
            total += IntegratePlanar.winding_number_linear(
                pointa, pointb, center
            )
        return total
