"""
This file contains the abstract classes to be inherited from
other curves, that implements the expected behaviors

It's meant to define the @abstractmethods that are needed in the code,
to make the code generic either if we use the one curve type or another
"""
from __future__ import annotations

from abc import abstractmethod
from typing import Iterable

from ..core import IBoolean2D, Parameter, Scalar
from ..point import GeneralPoint, Point2D


class ICurve(IBoolean2D):
    """
    This is an abstract class, it serves as interface to create a curve
    """

    @property
    def ndim(self) -> int:
        """
        Gives the number of dimensions of a curve, which is always 1
        """
        return 1

    @property
    @abstractmethod
    def lenght(self) -> Scalar:
        """
        Gives the lenght of curve

        Parameters
        ----------
        return: Scalar
            The numerical value of the lenght, always positive
        """
        raise NotImplementedError


class IOpenCurve(ICurve):
    """
    Defines an open curve abstract class, to be inherited
    """

    pass


class IClosedCurve(ICurve):
    """
    Defines a closed curve abstract class, to be inherited
    """

    @property
    @abstractmethod
    def area(self) -> Scalar:
        """
        Gives the area that is bounded by the curve

        If the curve's orientation is clockwise, it's negative

        Parameters
        ----------
        return: Scalar
            The value of the area
        """
        raise NotImplementedError

    @abstractmethod
    def winding(self, point: GeneralPoint) -> Scalar:
        """
        Computes the winding number of that point

        It's a mesure about the positioning of the point relative to the curve

        Parameters
        ----------
        point: Point
            The pair of values (x, y) to be computed
        return: Scalar
            The winding number, value in the interval [0, 1]
        """
        raise NotImplementedError


class IParameterCurve(ICurve):
    """
    Defines an abstract class that is parametrized
    """

    @abstractmethod
    def knots(self) -> Iterable[Parameter]:
        """
        Gives the breakpoints in the domain, which between two knots
        there's a pair of analytic functions
        """
        raise NotImplementedError

    @abstractmethod
    def eval(self, node: Parameter, derivate: int = 0) -> Point2D:
        """
        Evaluates the given analytic function p(t) at given node t

        Parameters
        ----------
        node: Parameter
            The value of 't' which the analytic function must be evaluated
        derivate: int, default = 0
            The degree of derivative to be computed.
            As default 0, means the function is not derivated
        """
        raise NotImplementedError

    @abstractmethod
    def section(self, nodea: Parameter, nodeb: Parameter) -> IParameterCurve:
        """
        Divides the actual curve in a smaller one

        Parameters
        ----------
        nodea: Parameter
            The starting node to cut
        nodeb: Paramter
            The ending node to cut
        return: IParameterCurve
            The cutted curve
        """
        raise NotImplementedError

    @abstractmethod
    def projection(self, point: GeneralPoint) -> Iterable[Parameter]:
        """
        Projects a point P into the curve p(t), giving the
        values of t* such |p(t*) - P| is minimal

        Parameters
        ----------
        point: Point
            The pair of values (x, y) to be projected
        return: Iterable[Parameter]
            The values of t*, can be more than one
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def vertices(self) -> Iterable[Point2D]:
        """
        Gives the evaluated points at the vertices

        Parameters
        ----------
        return: Iterable[Point]
            The points which were evaluated at knots
        """
        raise NotImplementedError

    def __call__(self, node: Parameter) -> Point2D:
        return self.eval(node, 0)


class IJordanCurve(IClosedCurve):
    """
    Defines a jordan curve abstract class, to be inherited
    """

    @property
    @abstractmethod
    def param_curve(self) -> IParameterCurve:
        """
        Gives the parametrized curve that defines this jordan curve
        """
        raise NotImplementedError
