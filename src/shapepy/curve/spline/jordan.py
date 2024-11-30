"""
This modules contains a powerful class called JordanCurve which
is in fact, stores a list of spline-curves.
"""

from __future__ import annotations

from typing import Tuple

from ...core import Scalar
from ...point import GeneralPoint, Point2D
from ..abc import IJordanCurve
from .knotvector import KnotVector
from .spline import SplineClosedCurve


class JordanSpline(IJordanCurve):
    """
    Jordan Curve is an arbitrary closed curve which doesn't intersect itself.
    It stores a list of 'segments', each segment is a bezier curve
    """

    def __init__(
        self,
        knotvector: KnotVector,
        ctrlpoints: Tuple[GeneralPoint],
    ):
        param_curve = SplineClosedCurve(knotvector, ctrlpoints)
        self.__param_curve = param_curve

    @property
    def knotvector(self) -> KnotVector:
        return self.param_curve.knotvector

    @property
    def ctrlpoints(self) -> Tuple[Point2D, ...]:
        return self.param_curve.ctrlpoints

    @property
    def param_curve(self) -> SplineClosedCurve:
        return self.__param_curve

    @property
    def lenght(self) -> Scalar:
        return self.param_curve.lenght

    @property
    def area(self) -> Scalar:
        return self.param_curve.area

    @property
    def vertices(self) -> Tuple[Point2D, ...]:
        raise NotImplementedError

    def __str__(self) -> str:
        degree, npts = self.knotvector.degree, self.knotvector.npts
        msg = f"Jordan Spline of degree {degree} and {npts} points\n"
        msg += str(self.vertices)
        return msg

    def __repr__(self) -> str:
        degree, npts = self.knotvector.degree, self.knotvector.npts
        return f"JordanCurve (deg {degree}, {npts})"

    def winding(self, point: GeneralPoint) -> Scalar:
        return self.param_curve.winding(point)
