from fractions import Fraction
from typing import Any, Tuple, Union

import numpy as np

from compmec import nurbs
from compmec.shape.polygon import Point2D


class Math:
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
        value = 0
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
        npts = degree + 1
        matrix = np.zeros((npts, npts), dtype="object")
        for i in range(npts):
            for j in range(degree - i + 1):
                val = Math.comb(degree, i) * Math.comb(degree - i, j)
                matrix[i, j] = -val if (degree + i + j) % 2 else val
        return tuple(tuple(line) for line in matrix)


class BaseCurve(object):
    def __call__(self, nodes: Union[float, Tuple[float]]) -> Union[Any, Tuple[Any]]:
        one_value = False
        try:
            iter(nodes)
        except TypeError:
            one_value = True
            nodes = (nodes,)
        result = self.eval(nodes)
        return result[0] if one_value else result


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
        assert isinstance(other, (tuple, list))
        self.__ctrlpoints = tuple(other)
        self.__matrix = Math.bezier_caract_matrix(self.degree)

    def eval(self, nodes: Tuple[float]) -> Tuple[Any]:
        """
        Evaluates

                              [ 1 ]
        [P0, ..., Pn] * [M] * [   ]
                              [x^n]

        """
        assert isinstance(nodes, (tuple, list))
        results = [0] * len(nodes)
        matrix = self.__matrix
        for k, node in enumerate(nodes):
            coefs = np.dot(self.ctrlpoints, matrix)
            results[k] = Math.horner_method(node, coefs)
        return tuple(results)


class PlanarCurve(BaseCurve):
    def __init__(self, planar: BezierCurve):
        assert isinstance(planar, BezierCurve)
        for point in planar.ctrlpoints:
            assert isinstance(point, Point2D)
        self.__planar = planar

    @property
    def degree(self) -> int:
        return self.__planar.degree

    @property
    def npts(self) -> int:
        return self.__planar.npts

    def eval(self, nodes: Tuple[float]) -> Tuple[Any]:
        return self.__planar.eval(nodes)


class Operations:
    @staticmethod
    def degree_increase(degree: int, times: int) -> Tuple[Tuple[float]]:
        """Returns the transformation matrix such"""
        raise NotImplementedError

    @staticmethod
    def degree_decrease(degree: int, times: int) -> Tuple[Tuple[Tuple[float]]]:
        """Returns the transformation and error matrix such

        A(u) = sum_{i=0}^{p} B_{i,p}(u) * P_i
        B(u) = sum_{i=0}^{p-t} B_{i,p-t}(u) * Q_i

        [Q] = [T] * [P]
        error = [P]^T * [E] * [P]

        """
        raise NotImplementedError

    @staticmethod
    def split(degree: int, node: int) -> Tuple[Tuple[Tuple[float]]]:
        """Returns two matrices to split the curve"""
        raise NotImplementedError


class Intersection:
    @staticmethod
    def bezier_and_bezier(
        curvea: PlanarCurve, curveb: PlanarCurve
    ) -> Tuple[Tuple[float]]:
        """Finds the pairs (u*, v*) such A(u*) = B(v*)

        Uses newton's method
        """
        degreea = curvea.degree
        degreeb = curveb.degree


class Derivate:
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
        assert isinstance(times, int)
        assert times > 0
        knotvector = nurbs.GeneratorKnotVector.bezier(degree, Fraction)
        matrix = nurbs.heavy.Calculus.derivate_nonrational_bezier(knotvector)
        return tuple(tuple(line) for line in matrix)


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
    def polynomial_scalar_bezier(coefs: Tuple[int], ctrlpoints: Tuple[Point2D]):
        """
        Given the control points P of a bezier curve C(u) of
        degree p, this function computes the integral I

            C(u) = sum_{i=0}^{p} B_{i,p}(u) * P_i

            B_{i,p} = binom(p, i)*(1-u)^{p-i} * u^i

            I = int_{C} x^a * y^b * ds

            I = int_{0}^{1} x(u)^a * y(u)^b * abs(C'(u)) * du

            coefs = [a, b]
        """
        assert isinstance(coefs, (tuple, list))
        assert isinstance(ctrlpoints, (tuple, list))
        assert len(coefs) == 2
        expx, expy = coefs
        assert isinstance(expx, int)
        assert isinstance(expy, int)
        knotvector = nurbs.GeneratorKnotVector.bezier(len(ctrlpoints) - 1)
        px = nurbs.Curve(knotvector, [point[0] for point in ctrlpoints])
        py = nurbs.Curve(knotvector, [point[1] for point in ctrlpoints])
        dpx = nurbs.calculus.Derivate.bezier(px)
        dpy = nurbs.calculus.Derivate.bezier(py)
        function = (
            lambda t: (px(t)) ** expx
            * (py(t)) ** expy
            * np.sqrt(dpx(t) ** 2 + dpy(t) ** 2)
        )
        integral, _ = scipy.integrate.quad(function, 0, 1)
        return integral

    @staticmethod
    def polynomial_inner_bezier(coefs: Tuple[int], ctrlpoints: Tuple[Point2D]) -> float:
        """
        Given the control points P of a bezier curve C(u) of
        degree p, this function computes the integral I

            C(u) = sum_{i=0}^{p} B_{i,p}(u) * P_i

            B_{i,p} = binom(p, i)*(1-u)^{p-i} * u^i

            vector = (a * x^b * y^c) * e_x + (d * x^e * y^f) * e_y
            I = int_{C} < vector, ds >
            I = int_{C} vector[0] * dx + vector[1] * dy
            I = int_{C} a * x^b * y^c * dx + d * x^e * y^f * dy

            I = int_{0}^{1} < vector(u), C'(u) > du

            coefs = [a, b, c, d, e, f]
        """
        assert isinstance(coefs, (tuple, list))
        assert isinstance(ctrlpoints, (tuple, list))
        assert len(coefs) == 6
        knotvector = nurbs.GeneratorKnotVector.bezier(degree=len(ctrlpoints) - 1)
        px = nurbs.Curve(knotvector, [point[0] for point in ctrlpoints])
        py = nurbs.Curve(knotvector, [point[1] for point in ctrlpoints])
        dpx = nurbs.calculus.Derivate.bezier(px)
        dpy = nurbs.calculus.Derivate.bezier(py)
        scalar_dx, expx, expy = coefs[:3]
        function = lambda t: (px(t)) ** expx * (py(t)) ** expy * dpx(t)
        integ_dx, _ = scipy.integrate.quad(function, 0, 1)
        scalar_dy, expx, expy = coefs[3:]
        function = lambda t: (px(t)) ** expx * (py(t)) ** expy * dpy(t)
        integ_dy, _ = scipy.integrate.quad(function, 0, 1)
        return scalar_dx * integ_dx + scalar_dy * integ_dy

    @staticmethod
    def winding_number(ctrlpoints: Tuple[Point2D]) -> float:
        """
        Computes the integral for a bezier curve of given control points
        """
        assert isinstance(ctrlpoints, (tuple, list))
        knotvector = nurbs.GeneratorKnotVector.bezier(degree=len(ctrlpoints) - 1)
        px = nurbs.Curve(knotvector, [point[0] for point in ctrlpoints])
        py = nurbs.Curve(knotvector, [point[1] for point in ctrlpoints])
        dpx = nurbs.calculus.Derivate.bezier(px)
        dpy = nurbs.calculus.Derivate.bezier(py)
        numer = px * dpy - py * dpx
        denom = px * px + py * py
        function = lambda t: numer(t) / denom(t)
        integral, _ = scipy.integrate.quad(function, 0, 1)
        return integral / math.tau
