from __future__ import annotations

from abc import abstractmethod
from typing import Iterable, Tuple

from ..core import IBoolean2D, Parameter, Scalar
from ..point import GeneralPoint, Point2D


class ICurve(IBoolean2D):
    """
    This is an abstract class, it serves as interface to create a curve
    """

    @property
    def ndim(self) -> int:
        return 1

    @property
    @abstractmethod
    def lenght(self) -> Scalar:
        """
        Gives the lenght of the curve.
        It's always positive
        """
        raise NotImplementedError


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

    @property
    @abstractmethod
    def vertices(self) -> Iterable[Point2D]:
        raise NotImplementedError

    def __call__(self, node: Parameter) -> Point2D:
        return self.eval(node, 0)


class IJordanCurve(IClosedCurve):
    @property
    @abstractmethod
    def param_curve(self) -> IParameterCurve:
        raise NotImplementedError
