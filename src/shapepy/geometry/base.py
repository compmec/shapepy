"""
Defines the base class for Geometric curves
"""

from abc import abstractmethod
from typing import Tuple

from ..scalar.reals import Real
from .box import Box
from .point import Point2D


class IGeometricCurve:
    """
    Class interface for geometric curves
    """

    @property
    @abstractmethod
    def knots(self) -> Tuple[Real, ...]:
        """
        Defines the breakpoints of the geometric curve

        The curve is only defined within the given intervals
        """
        raise NotImplementedError

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
    def __call__(self, node: Real) -> Point2D:
        raise NotImplementedError
