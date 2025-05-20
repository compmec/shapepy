"""
Defines the interfaces and required methods that are used to define a curve

It allows defining the curves however we want, like using analytics for
the x and y coordinates, but also define a curve only by its vertices,
like polygonal curves, which may speed up some evaluations
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from numbers import Real
from typing import Optional

from ..analytic import IAnalytic1D
from ..bool1d import SubSetR1
from .cage import BoxCage
from .point import GeometricPoint


class IContinuousCurve(ABC):
    """
    Defines the interface of a continous curve, which may be stored by a
    SingleCurveR2 boolean object that is defined further in `bool2d` module
    """

    @abstractmethod
    def __getitem__(self, index) -> IAnalytic1D:
        raise NotImplementedError

    @property
    @abstractmethod
    def domain(self) -> SubSetR1:
        """
        Gives the curve's domain

        :getter: Returns the defined domain of the curve
        :type: SubSetR1
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def lenght(self) -> Real:
        """
        Gives the curve's length

        :getter: Returns the length of the curve
        :type: Real
        """
        raise NotImplementedError

    @property
    def cage(self) -> BoxCage:
        """
        Gives a cage that contains entirely the curve

        :getter: Returns the box that contains the curve
        :type: BoxCage
        """
        raise NotImplementedError

    @abstractmethod
    def section(
        self, subdomain: Optional[SubSetR1] = None
    ) -> IContinuousCurve:
        """
        Gives a copy of a new curve with restricted domain

        If no subdomain is given, only returns a copy

        Parameters
        ----------
        subdomain: Optional[SubSetR1], default = None
            The subdomain to get the section
            A copy is returned if no subdomain is given

        Return
        ------
        IContinuousCurve
            A copy of the curve with restriced domain
        """
        raise NotImplementedError

    @abstractmethod
    def eval(self, node: Real, derivate: int = 0) -> GeometricPoint:
        """
        Evaluate the curve at given node 't':

            C(t) = (x(t), y(t))

        Parameters
        ----------
        node: Real
            The t-value used to evaluate the curve
        derivate: int, default = 0
            Used when the derivate is required

        Return
        ------
        GeometricPoint
            The evaluated point C(t) = (x(t), y(t))
        """
        raise NotImplementedError

    @abstractmethod
    def projection(self, point: GeometricPoint) -> SubSetR1:
        """
        Computes the projection of a point in the given curve.

        Finds all the values 't' such minimizes the distance between the
        curve and the point

            min_t <C(t)-P, C(t)-P>

        It's possible to not have a projection point.
        In that case, gives an EmptyR1 instance.

        Parameters
        ----------
        point: GeometricPoint
            The point to be projected

        Return
        ------
        SubSetR1
            The values 't' that minimizes the distance
        """
        raise NotImplementedError


class IClosedCurve(IContinuousCurve):
    """
    Defines the interface of a closed curve, that can evaluate
    winding numbers for example, which are used to check if point
    is inside a region
    """

    @property
    @abstractmethod
    def area(self) -> Real:
        """
        Gives the area enclosed by the curve

        :getter: Returns the area enclosed by the curve
        :type: Real
        """

    @abstractmethod
    def winding(self, point: GeometricPoint) -> Real:
        """
        Computes the winding number with respect to a point.
        It gives a real value that depends

        For this function, we consider that
        """


class IJordanCurve(IClosedCurve):
    """
    Class that defines the required methods to define a Jordan Curve
    """
