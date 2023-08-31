import math
from fractions import Fraction
from typing import Any, Callable, Tuple

import numpy as np
import scipy

from compmec import nurbs
from compmec.shape.polygon import Point2D


class DistributedNodes:
    @staticmethod
    def linspace_nodes(npts: int) -> Tuple[float]:
        """
        Returns equally distributed nodes in [-1, 1]
        Include the extremities

        npts = 2 -> [-1, 1]
        npts = 3 -> [-1, 0, 1]
        npts = 4 -> [-1, -1/3, 1/3, 1]
        npts = 5 -> [-1, -1/2, 0, 1/2, 1]
        npts = 6 -> [-1, -2/2, 0, 1/2, 1]
        """
        assert isinstance(npts, int)
        assert npts > 1
        nums = 1 + 2 * np.arange(npts) - npts
        nums = tuple([Fraction(num, npts - 1) for num in nums])
        return nums

    @staticmethod
    def uniform_nodes(npts: int) -> Tuple[float]:
        """
        Returns equally distributed nodes in [-1, 1]
        Don't include the extremities

        npts = 1 -> [0]
        npts = 2 -> [-1/2, 1/2]
        npts = 3 -> [-2/3, 0, 2/3]
        npts = 4 -> [-3/4, -1/4, 1/4, 3/4]
        """
        assert isinstance(npts, int)
        assert npts > 0
        nums = 1 + 2 * np.arange(npts) - npts
        nums = tuple([Fraction(num, npts) for num in nums])
        return nums

    @staticmethod
    def chebyshev_nodes(npts: int) -> Tuple[float]:
        """
        Returns chebyshev nodes in the space [-1, 1]
        https://en.wikipedia.org/wiki/Chebyshev_nodes

        npts = 1 -> [0]
        npts = 2 -> [-0.707, 0.707]
        npts = 3 -> [-0.866, 0, 0.866]
        npts = 4 -> [-0.924, -0.383, 0.383, 0.924]
        """
        assert isinstance(npts, int)
        assert npts > 0
        nums = np.arange(npts - 1, -1, -1)
        nums = np.pi * (2 * nums + 1) / (2 * npts)
        return tuple(np.cos(nums))

    @staticmethod
    def normalize(nodes: Tuple[float]) -> Tuple[float]:
        """
        Converts the nodes to be in the interval [0, 1]
        """
        minnode = min(nodes)
        maxnode = max(nodes)
        diff = maxnode - minnode
        nodes0to1 = [(node - minnode) / diff for node in nodes]
        return tuple(nodes0to1)


class OneDimIntegration:
    linsp_integ_array = {}
    unifo_integ_array = {}
    cheby_integ_array = {}

    @staticmethod
    def interpolator_bezier_matrix(nodes: Tuple[float]) -> Tuple[Tuple[float]]:
        """
        This function returns the inverse of matrix [M] which
        interpolates a bezier curve C at the given nodes

            C(u) = sum_{i=0}^{p} B_{i,p}(u) * P_{i}
            B_{i,p}(u) = binom(p, i) * (1-u)^{p-i} * u^i
            [M]_{i,k} = B_{i,p}(u_k)
            [M] * [P] = [f(x_k)]

        """
        assert isinstance(nodes, tuple)
        for node in nodes:
            float(node)
            assert 0 <= node
            assert node <= 1
        degree = len(nodes) - 1
        matrix_bezier = np.zeros((degree + 1, degree + 1), dtype="float64")
        for k, uk in enumerate(nodes):
            for i in range(degree + 1):
                matrix_bezier[i, k] = (
                    math.comb(degree, i) * (1 - uk) ** (degree - i) * (uk**i)
                )
        inverse = np.linalg.inv(matrix_bezier)
        classe = nodes[0].__class__
        inverse = tuple([tuple([classe(numb) for numb in line]) for line in inverse])
        return inverse

    @staticmethod
    def integrator_array(nodes: Tuple[float]) -> Tuple[float]:
        """
        Given a list of nodes [u_i] in [0, 1],
        we compute the integrator array [w_i] such

        I = int_{0}^{1} f(x) dx = sum_{i=0}^{p} w_i * f(x_i)
        """
        npts = len(nodes)
        matrix = OneDimIntegration.interpolator_bezier_matrix(nodes)
        array = [sum(line) / npts for line in np.transpose(matrix)]
        return tuple(array)

    @staticmethod
    def linspace_integrator_array(npts: int) -> Tuple[float]:
        """
        Given a function f(x) defined on the interval [0, 1]
        It's wanted the numerical integral I

        I = int_0^1 f(x) dx = sum_{i=1}^{npts} f(x_i) * w_i

        This function returns the weights [w] for such
        x_i nodes are equally spaced in [0, 1]
        """
        assert isinstance(npts, int)
        assert 0 < npts
        if npts not in OneDimIntegration.linsp_integ_array:
            linsp_nodes = DistributedNodes.linspace_nodes(npts)
            integ_array = OneDimIntegration.integrator_array(linsp_nodes)
            OneDimIntegration.linsp_integ_array[npts] = integ_array
        return OneDimIntegration.linsp_integ_array[npts]

    @staticmethod
    def uniform_integrator_array(npts: int) -> Tuple[float]:
        """
        Given a function f(x) defined on the interval [0, 1]
        It's wanted the numerical integral I

        I = int_0^1 f(x) dx = sum_{i=1}^{npts} f(x_i) * w_i

        This function returns the weights [w] for such x_i
        nodes are equally spaced in [0, 1] without extremities
        """
        assert isinstance(npts, int)
        assert 0 < npts
        if npts not in OneDimIntegration.unifo_integ_array:
            unifo_nodes = DistributedNodes.uniform_nodes(npts)
            integ_array = OneDimIntegration.integrator_array(unifo_nodes)
            OneDimIntegration.unifo_integ_array[npts] = integ_array
        return OneDimIntegration.unifo_integ_array[npts]

    @staticmethod
    def chebyshev_integrator_array(npts: int) -> Tuple[float]:
        """
        Given a function f(x) defined on the interval [0, 1]
        It's wanted the numerical integral I

        I = int_0^1 f(x) dx = sum_{i=1}^{npts} f(x_i) * w_i

        This function returns the weights [w] for such
        x_i is a chebyshev nodes
        npts = 1 -> [x] = [0.5]
        npts = 1
        """
        assert isinstance(npts, int)
        assert 0 < npts
        if npts not in OneDimIntegration.cheby_integ_array:
            cheby_nodes = DistributedNodes.chebyshev_nodes(npts)
            cheby_0to1 = [(1 + node) / 2 for node in cheby_nodes]
            integ_array = OneDimIntegration.integrator_array(cheby_0to1)
            OneDimIntegration.cheby_integ_array[npts] = integ_array
        return OneDimIntegration.cheby_integ_array[npts]


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
        npts = len(ctrlpoints) - 1
        knotvector = nurbs.GeneratorKnotVector.bezier(degree=npts - 1)
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
    def polynomial_cross_bezier(coefs: Tuple[int], ctrlpoints: Tuple[Point2D]) -> float:
        """
        Given the control points P of a bezier curve C(u) of
        degree p, this function computes the integral I

            C(u) = sum_{i=0}^{p} B_{i,p}(u) * P_i

            B_{i,p} = binom(p, i)*(1-u)^{p-i} * u^i

            vector = (a * x^b * y^c) * e_x + (d * x^e * y^f) * e_y
            I = int_{C} vector x ds
            I = int_{C} - vector[1] * dx + vector[0] * dy
            I = int_{C} - d * x^e * y^f * dx + a * x^b * y^c * dy

            I = int_{0}^{1} vector(u) x C'(u) du

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
        scalar_dx, expx, expy = coefs[3:]
        function = lambda t: (px(t)) ** expx * (py(t)) ** expy * dpx(t)
        integ_dx, _ = scipy.integrate.quad(function, 0, 1)
        scalar_dy, expx, expy = coefs[:3]
        function = lambda t: (px(t)) ** expx * (py(t)) ** expy * dpy(t)
        integ_dy, _ = scipy.integrate.quad(function, 0, 1)
        return scalar_dy * integ_dy - scalar_dx * integ_dx

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
