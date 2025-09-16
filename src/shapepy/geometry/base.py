"""
Defines the base class for Geometric curves
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Tuple, Union

from ..rbool import IntervalR1
from ..scalar.angle import Angle
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

    def move(self, vector: Point2D) -> IGeometricCurve:
        """
        Moves/translate entire shape by an amount

        Parameters
        ----------

        point : Point2D
            The amount to move

        :return: The same instance
        :rtype: SubSetR2

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()
        >>> circle.move(1, 2)

        """
        raise NotImplementedError

    def scale(self, amount: Union[Real, Tuple[Real, Real]]) -> IGeometricCurve:
        """
        Scales entire subset by an amount

        Parameters
        ----------

        amount : Real | Tuple[Real, Real]
            The amount to scale in horizontal and vertical direction

        :return: The same instance
        :rtype: SubSetR2

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()
        >>> circle.scale(2, 3)

        """
        raise NotImplementedError

    def rotate(self, angle: Angle) -> IGeometricCurve:
        """
        Rotates entire shape around the origin by an amount

        Parameters
        ----------

        angle : Angle
            The amount to rotate around origin

        :return: The same instance
        :rtype: SubSetR2

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()
        >>> circle.rotate(degrees(90))

        """
        raise NotImplementedError


class IParametrizedCurve(IGeometricCurve):
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

    def __and__(self, other: IParametrizedCurve):
        return Future.intersect(self, other)

    def parametrize(self) -> IParametrizedCurve:
        """Gives a parametrized curve"""
        return self

    @abstractmethod
    def section(self, interval: IntervalR1) -> IParametrizedCurve:
        """Gives the section of the curve"""
        raise NotImplementedError
