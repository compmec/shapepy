from __future__ import annotations

from abc import abstractmethod
from typing import Tuple

from ..core import IObject2D, Parameter, Scalar
from ..point import GeneralPoint, Point2D


class IBaseCurve(IObject2D):

    @property
    @abstractmethod
    def lenght(self) -> Scalar:
        raise NotImplementedError


class IOpenCurve(IBaseCurve):
    pass


class IClosedCurve(IBaseCurve):

    @property
    @abstractmethod
    def area(self) -> Scalar:
        raise NotImplementedError

    @abstractmethod
    def winding(self, point: GeneralPoint) -> Scalar:
        raise NotImplementedError


class IParameterCurve(IBaseCurve):

    @abstractmethod
    def knots(self) -> Tuple[Parameter, ...]:
        raise NotImplementedError

    @abstractmethod
    def eval(self, node: Parameter, derivate: int = 0) -> Point2D:
        raise NotImplementedError

    @abstractmethod
    def section(self, nodea: Parameter, nodeb: Parameter) -> IParameterCurve:
        raise NotImplementedError

    def __call__(self, node: Parameter) -> Point2D:
        return self.eval(node, 0)


class IJordanCurve(IClosedCurve):

    @property
    @abstractmethod
    def param_curve(self) -> IParameterCurve:
        raise NotImplementedError
