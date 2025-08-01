"""
Contains functions to integrate over a segment
"""

from __future__ import annotations

from typing import Optional, Union

import numpy as np

from ..scalar.bezier import Bezier, bezier2polynomial
from ..scalar.calculus import derivate, integrate
from ..scalar.quadrature import closed_linspace
from ..scalar.reals import Math
from ..tools import Is
from .jordancurve import JordanCurve
from .point import Point2D
from .segment import Segment


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
        if not Is.instance(curve, Segment):
            raise TypeError

        xfunc = bezier2polynomial(Bezier(pt[0] for pt in curve.ctrlpoints))
        yfunc = bezier2polynomial(Bezier(pt[1] for pt in curve.ctrlpoints))

        poly = (xfunc**expx) * (yfunc**expy)
        poly *= xfunc * derivate(yfunc) - yfunc * derivate(xfunc)
        poly = integrate(poly)
        return (poly(1) - poly(0)) / (expx + expy + 2)

    @staticmethod
    def winding_number(
        curve: Segment,
        center: Point2D = (0.0, 0.0),
        nnodes: Union[None, int] = None,
    ) -> float:
        """
        Computes the integral for a bezier curve of given control points
        """
        assert Is.instance(curve, Segment)
        nnodes = curve.npts if nnodes is None else nnodes
        nodes = closed_linspace(nnodes)
        total = 0
        for nodea, nodeb in zip(nodes[:-1], nodes[1:]):
            pointa = curve(nodea)
            pointb = curve(nodeb)
            total += winding_number_linear(pointa, pointb, center)
        return total


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
            IntegrateSegment.polynomial(segment, expx, expy)
            for segment in jordan.segments
        )

    @staticmethod
    def winding_number(
        jordan: JordanCurve,
        center: Optional[Point2D] = (0.0, 0.0),
        nnodes: Optional[int] = None,
    ) -> Union[int, float]:
        """Computes the winding number from jordan curve

        Returns [-1, -0.5, 0, 0.5 or 1]
        """
        wind = 0
        if center in jordan.box():
            for bezier in jordan.segments:
                if center in bezier:
                    return 0.5 if float(jordan) > 0 else -0.5
        for bezier in jordan.segments:
            wind += IntegrateSegment.winding_number(bezier, center, nnodes)
        return round(wind)


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
    wind = (angleb - anglea) / Math.tau
    if abs(wind) < 0.5:
        return wind
    return wind - 1 if wind > 0 else wind + 1
