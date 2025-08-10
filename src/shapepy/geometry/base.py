"""
Defines the base class for Geometric curves
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Tuple

from ..scalar.reals import Real
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


class IParametrizedCurve(ABC):
    """
    Class interface for parametrized curves
    """

    @property
    @abstractmethod
    def knots(self) -> Tuple[Real, ...]:
        """
        The length of the curve
        If the curve is not bounded, returns infinity
        """
        raise NotImplementedError

    @abstractmethod
    def __call__(self, node: Real, derivate: int = 0) -> Point2D:
        raise NotImplementedError

    def __or__(self, other: IParametrizedCurve) -> IParametrizedCurve:
        return Future.concatenate((self, other))


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

    def __and__(self, other: IGeometricCurve):
        return Future.intersect(self, other)
