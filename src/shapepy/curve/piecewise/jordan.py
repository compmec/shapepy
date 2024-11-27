from __future__ import annotations

from typing import Iterable, Tuple

from ...core import IAnalytic, Scalar
from ...point import GeneralPoint, Point2D
from ..abc import IJordanCurve
from .curve import PiecewiseClosedCurve


class JordanPiecewise(IJordanCurve):

    def __init__(self, functions: Iterable[Tuple[IAnalytic, IAnalytic]]):
        self.__param_curve = PiecewiseClosedCurve(functions)

    @property
    def param_curve(self) -> PiecewiseClosedCurve:
        return self.__param_curve

    @property
    def area(self) -> Scalar:
        return self.param_curve.area

    @property
    def lenght(self) -> Scalar:
        return self.param_curve.lenght

    @property
    def vertices(self) -> Tuple[Point2D, ...]:
        return self.param_curve.vertices

    def winding(self, point: GeneralPoint) -> Scalar:
        return self.param_curve.winding(point)
