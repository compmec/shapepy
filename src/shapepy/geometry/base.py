"""
Defines the base class for Geometric curves
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Tuple, Union

from ..rbool import IntervalR1, WholeR1
from ..scalar.reals import Real
from ..tools import vectorize
from .box import Box
from .point import Point2D


# pylint: disable=too-few-public-methods
class Future:
    """
    Static class that contains the methods that are further implemented
    """

    @staticmethod
    def intersect(curvea: IGeometricCurve, curveb: IGeometricCurve):
        """Method that computes the intersection between two curves

        It is overwritten to `intersect` function in `intersection.py`
        """
        raise NotImplementedError

    @staticmethod
    def concatenate(
        curves: Iterable[IParametrizedCurve],
    ) -> IParametrizedCurve:
        """Method that computes the concatenation of two curves

        It is overwritten to `concatenate` function in `concatenate.py`
        """
        raise NotImplementedError


class IGeometricCurve(ABC):
    """
    Class interface for geometric curves
    """

    @property
    @abstractmethod
    def length(self) -> Real:
        """
        The length of the curve
        If the curve is not bounded, returns infinity
        """
        raise NotImplementedError

    @abstractmethod
    def box(self) -> Box:
        """
        Gives the box that encloses the curve
        """
        raise NotImplementedError

    @abstractmethod
    def parametrize(self) -> IParametrizedCurve:
        """Gives a parametrized curve"""
        raise NotImplementedError

    def __or__(self, other: IGeometricCurve) -> IGeometricCurve:
        return Future.concatenate((self, other))


class IParametrizedCurve(IGeometricCurve):
    """
    Class interface for parametrized curves
    """

    @property
    @abstractmethod
    def domain(self) -> Union[IntervalR1, WholeR1]:
        """
        The domain where the curve is defined.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def knots(self) -> Tuple[Real, ...]:
        """
        The subdivisions on the domain
        """
        raise NotImplementedError

    @abstractmethod
    def eval(self, node: Real, derivate: int = 0) -> Point2D:
        """Evaluates the curve at given node"""
        raise NotImplementedError

    @vectorize(1, 0)
    def __call__(self, node: Real) -> Point2D:
        return self.eval(node, 0)

    def __and__(self, other: IParametrizedCurve):
        return Future.intersect(self, other)

    def parametrize(self) -> IParametrizedCurve:
        """Gives a parametrized curve"""
        return self

    @abstractmethod
    def section(
        self, domain: Union[IntervalR1, WholeR1]
    ) -> IParametrizedCurve:
        """Gives the section of the curve"""
        raise NotImplementedError
