from __future__ import annotations

from abc import abstractmethod
from typing import Iterable, Tuple

from ..core import ICurve, Parameter, Scalar
from ..point import GeneralPoint, Point2D


class IOpenCurve(ICurve):
    pass


class IClosedCurve(ICurve):
    @property
    @abstractmethod
    def area(self) -> Scalar:
        raise NotImplementedError

    @abstractmethod
    def winding(self, point: GeneralPoint) -> Scalar:
        raise NotImplementedError


class IParameterCurve(ICurve):
    @abstractmethod
    def knots(self) -> Tuple[Parameter, ...]:
        raise NotImplementedError

    @abstractmethod
    def eval(self, node: Parameter, derivate: int = 0) -> Point2D:
        raise NotImplementedError

    @abstractmethod
    def section(self, nodea: Parameter, nodeb: Parameter) -> IParameterCurve:
        raise NotImplementedError

    @abstractmethod
    def projection(self, point: GeneralPoint) -> Iterable[Parameter]:
        raise NotImplementedError

    def __call__(self, node: Parameter) -> Point2D:
        return self.eval(node, 0)


class IJordanCurve(IClosedCurve):
    @property
    @abstractmethod
    def param_curve(self) -> IParameterCurve:
        raise NotImplementedError

    @property
    @abstractmethod
    def vertices(self) -> Tuple[Point2D, ...]:
        raise NotImplementedError
