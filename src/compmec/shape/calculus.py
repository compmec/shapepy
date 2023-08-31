import math
from fractions import Fraction
from typing import Any, Callable, Tuple

import numpy as np
import scipy

from compmec import nurbs
from compmec.shape.polygon import Point2D


class BezierCurveIntegral:
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


class JordanCurveIntegral:
    """
    Computes the boundary integral curve
    """

    @staticmethod
    def polynomial(
        coefs: Tuple[int], beziers: Tuple[nurbs.Curve], alpha: float = 0
    ) -> float:
        """
        Computes the integral I

        I = int_D f(x, y) dA = x^a * y^b

        We transform this integral into a boundary integral by using green theorem

        I = int_D f(x, y) dA
          = int_D (dQ/dx - dP/dy) dA
          = int_C P dx + Q * dy

        P = (alpha-1) * int f(x, y) dy
        Q = alpha * int f(x, y) dx
        coefs = [a, b]
        """

        assert isinstance(coefs, (list, tuple))
        assert len(coefs) == 2
        assert isinstance(beziers, (tuple, list))
        for bezier in beziers:
            assert isinstance(bezier, nurbs.Curve)
        assert isinstance(alpha, (int, float))
        expx, expy = coefs
        assert isinstance(expx, int)
        assert isinstance(expy, int)

        allcoefs = [
            (alpha - 1) / (1 + expy),
            expx,
            1 + expy,
            alpha / (1 + expx),
            1 + expx,
            expy,
        ]
        soma = 0
        for bezier in beziers:
            points = bezier.ctrlpoints
            value = BezierCurveIntegral.polynomial_inner_bezier(allcoefs, points)
            soma += value
        return soma

    @staticmethod
    def area(beziers: Tuple[nurbs.Curve]) -> float:
        return JordanCurveIntegral.polynomial((0, 0), beziers)

    @staticmethod
    def winding_number(beziers: Tuple[nurbs.Curve]) -> float:
        """
        Compute the winding number with respect to the origin
        """
        soma = 0
        for bezier in beziers:
            points = bezier.ctrlpoints
            soma += BezierCurveIntegral.winding_number(points)
        return round(soma)
