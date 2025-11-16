"""
Contains functions to integrate over a segment
"""

from __future__ import annotations

from functools import partial

from ..analytic.base import IAnalytic
from ..analytic.tools import find_minimum
from ..scalar.quadrature import AdaptativeIntegrator, IntegratorFactory
from ..scalar.reals import Math
from ..tools import Is, To
from .jordancurve import JordanCurve
from .point import Point2D
from .segment import Segment


# pylint: disable=too-few-public-methods
class IntegrateSegment:
    """
    Defines methods to integrates over a segment
    """

    direct = IntegratorFactory.closed_newton_cotes(3)
    adaptative = AdaptativeIntegrator(direct, 1e-6)

    @staticmethod
    def polynomial(curve: Segment, expx: int, expy: int):
        """
        Computes the integral

        I = int_D x^expx * y^expy * dA

        """
        assert Is.instance(curve, Segment)
        xfunc = curve.xfunc
        yfunc = curve.yfunc
        pcrossdp = xfunc * yfunc.derivate()
        pcrossdp -= yfunc * xfunc.derivate()
        function = (xfunc**expx) * (yfunc**expy) * pcrossdp
        assert Is.instance(function, IAnalytic)
        return function.integrate([0, 1]) / (expx + expy + 2)

    @staticmethod
    def turns(curve: Segment, point: Point2D) -> float:
        """
        Computes the integral

        I = int_0^1 (u * v' - v * u') / (u * u + v * v) dt

        Where

        u = curve.x - point.x
        v = curve.y - point.y
        """
        point = To.point(point)
        deltax: IAnalytic = curve.xfunc - point.xcoord
        deltay: IAnalytic = curve.yfunc - point.ycoord
        radius_square = deltax * deltax + deltay * deltay
        if find_minimum(radius_square, [0, 1]) < 1e-6:
            return To.rational(1, 2)
        crossf = deltax * deltay.derivate()
        crossf -= deltay * deltax.derivate()
        function = partial(
            lambda t, cf, rs: cf(t) / rs(t), cf=crossf, rs=radius_square
        )
        radians = IntegrateSegment.adaptative.integrate(function, [0, 1])
        return radians / Math.tau


class IntegrateJordan:
    """
    Defines functions to integrate over the internal area
    defined by the jordan curve.
    """

    @staticmethod
    def polynomial(jordan: JordanCurve, expx: int, expy: int):
        """
        Computes the integral

        I = int x^expx * y^expy * ds
        """
        assert Is.instance(jordan, JordanCurve)
        return sum(
            IntegrateSegment.polynomial(usegment.parametrize(), expx, expy)
            for usegment in jordan
        )

    @staticmethod
    def turns(jordan: JordanCurve, point: Point2D) -> float:
        """
        Computes the integral

        I = int_0^1 (u * v' - v * u') / (u * u + v * v) dt

        Where

        u = jordan.x - point.x
        v = jordan.y - point.y

        This function should return values other than
        [-1, -0.5, 0, 0.5, 1]
        It happens when the functions is discontinuous
        """
        result = 0
        for usegment in jordan:
            seg = usegment.parametrize()
            delta_result = IntegrateSegment.turns(seg, point)
            if delta_result == 0.5:
                return 0.5 if jordan.area > 0 else -0.5
            result += delta_result
        return result
