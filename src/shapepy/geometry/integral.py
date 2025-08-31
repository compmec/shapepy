"""
Contains functions to integrate over a segment
"""

from __future__ import annotations

from functools import partial
from typing import Optional, Union

from ..analytic.base import IAnalytic
from ..analytic.tools import find_minimum
from ..common import derivate
from ..loggers import debug
from ..scalar.angle import arg
from ..scalar.quadrature import AdaptativeIntegrator, IntegratorFactory
from ..scalar.reals import Math
from ..tools import Is, To
from .jordancurve import JordanCurve
from .point import Point2D, cross, inner
from .segment import Segment


# pylint: disable=too-few-public-methods
class IntegrateSegment:
    """
    Defines methods to integrates over a segment
    """

    @staticmethod
    def polynomial(curve: Segment, expx: int, expy: int):
        """
        Computes the integral

        I = int_D x^expx * y^expy * dA

        """
        assert Is.instance(curve, Segment)
        xfunc = curve.xfunc
        yfunc = curve.yfunc
        pcrossdp = xfunc * yfunc.derivate() - yfunc * xfunc.derivate()
        function = (xfunc**expx) * (yfunc**expy) * pcrossdp
        assert Is.analytic(function)
        ipoly = function.integrate()
        return (ipoly(1) - ipoly(0)) / (expx + expy + 2)


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
        assert Is.jordan(jordan)
        return sum(
            IntegrateSegment.polynomial(usegment.parametrize(), expx, expy)
            for usegment in jordan.usegments
        )


# pylint: disable=too-many-locals
@debug("shapepy.geometry.integral")
def lebesgue_density_jordan(
    jordan: JordanCurve, point: Optional[Point2D] = (0.0, 0.0)
) -> Union[int, float]:
    """Computes the lebesgue density number from jordan curve

    Returns a value in the interval [0, 1]:
    * 0 -> means the point is outside the interior region
    * 1 -> means the point is completly inside the interior
    * between 0 and 1, it's on the boundary
    """
    point = To.point(point)
    box = jordan.box()
    if point not in box:
        density = 0 if jordan.area > 0 else 1
        return density

    segments = tuple(jordan.parametrize())
    for i, segmenti in enumerate(segments):
        if point == segmenti(0):
            segmentj = segments[(i - 1) % len(segments)]
            deltapi = segmenti(0, 1)
            deltapj = segmentj(1, 1)
            innerval = inner(deltapi, deltapj)
            crossval = cross(deltapi, deltapj)
            angle = arg(-innerval, -crossval)
            return angle.turns % 1

    direct = IntegratorFactory.closed_newton_cotes(3)
    integrator = AdaptativeIntegrator(direct, 1e-6)
    radangle = 0
    for segment in segments:
        deltax: IAnalytic = segment.xfunc - point.xcoord
        deltay: IAnalytic = segment.yfunc - point.ycoord
        radius_square = deltax * deltax + deltay * deltay
        if find_minimum(radius_square, [0, 1]) < 1e-6:
            return 0.5
        crossf = deltax * derivate(deltay) - deltay * derivate(deltax)
        function = partial(
            lambda t, cf, rs: cf(t) / rs(t), cf=crossf, rs=radius_square
        )
        radangle += integrator.integrate(function, [0, 1])
    density = round(radangle / Math.tau)
    return density if jordan.area > 0 else 1 + density
