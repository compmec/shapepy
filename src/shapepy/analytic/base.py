"""
Defines the basic class to be used later when computing the coordinates
of the curves.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from numbers import Real
from typing import Optional, Union

from ..bool1d import SubSetR1


class IAnalytic1D(ABC):
    """
    This is an abstract class that serves as interface for an analytic function

    It contains the basic methods to evaluate this function,
    to compute the derivate, find roots, shift, scale, compute integrals, etc
    """

    @property
    @abstractmethod
    def domain(self) -> SubSetR1:
        """
        Gives the domain of the analytic function
        """
        raise NotImplementedError

    @abstractmethod
    def eval(self, node: Real, derivate: int = 0) -> Real:
        """
        Evaluates the given analytic function p(t) at given node t

        Parameters
        ----------
        node: Real
            The value of 't' which the analytic function must be evaluated
        derivate: int, default = 0
            The k-th derivative to be computed.
            As default, means the function is not derivated
        """
        raise NotImplementedError

    @abstractmethod
    def derivate(self, times: int = 1) -> IAnalytic1D:
        """
        Derivates the analytic function p(t), giving another analytic function

        Parameters
        ----------
        times: int
            The quantity of times to be derived
        """
        raise NotImplementedError

    @abstractmethod
    def shift(self, amount: Real) -> IAnalytic1D:
        """
        Shifts the analytic function by given amount,
        returning the function q(t) = p(t-a) which 'a' is the amount

        Parameters
        ----------
        amount: Real
            The value of 'a', the quantity of the function to be shifted
        """
        raise NotImplementedError

    @abstractmethod
    def scale(self, amount: Real) -> IAnalytic1D:
        """
        Scales the analytic function by given amount,
        returning the function q(t) = p(a*t) which 'a' is the amount

        Parameters
        ----------
        amount: Real
            The value of 'a', the quantity of the function to be scaled
        """
        raise NotImplementedError

    @abstractmethod
    def integrate(
        self,
        domain: Optional[SubSetR1] = None,
        tolerance: Optional[Real] = None,
    ) -> Real:
        """
        Computes the definite integral in the given domain

        I = int_D f(t) dt

        For unbounded domains, gives the Cauchy integral value.

        Tolerance parameter is used when numerical integration is needed.

        The function's domain is considered if no domain is given

        Parameters
        ----------
        domain: Optional[SubSetR1], default = None
            The domain to be integrated.
            If no domain is given, function's domain is taken
        tolerance: Optional[Real], default = None
            The tolerance value if numerical integration is used

        Return
        ------
        Real
            The value of the definite integral in the domain
        """
        raise NotImplementedError

    @abstractmethod
    def roots(self, domain: Optional[SubSetR1] = None) -> SubSetR1:
        """
        Find the roots in the given domain

        The function's domain is considered if no domain is given

        Parameters
        ----------
        domain: Optional[SubSetR1], default = None
            The domain to search for the roots.
            If no domain is given, function's domain is taken

        Return
        ------
        SubSetR1
            The values 't' which 'f(t)' is zero
        """
        raise NotImplementedError

    @abstractmethod
    def infimum(self, domain: Optional[SubSetR1] = None) -> Real:
        """
        Find the infimum of the function.

        For closed and bounded domains, it's equal to the minimum value.

        The function's domain is considered if no domain is given

        Parameters
        ----------
        domain: Optional[SubSetR1], default = None
            The domain to search for the infimum.
            If no domain is given, function's domain is taken

        Return
        ------
        Real
            The supremum value of the function in the domain
        """
        raise NotImplementedError

    @abstractmethod
    def supremum(self, domain: Optional[SubSetR1] = None) -> Real:
        """
        Find the supremum of the function.

        For closed and bounded domains, it's equal to the maximum value.

        The function's domain is considered if no domain is given

        Parameters
        ----------
        domain: Optional[SubSetR1], default = None
            The domain to search for the supremum.
            If no domain is given, function's domain is taken

        Return
        ------
        Real
            The supremum value of the function in the domain
        """
        raise NotImplementedError

    def __call__(self, node: Real) -> Real:
        return self.eval(node, 0)

    def __neg__(self) -> IAnalytic1D:
        return self.__mul__(-1)

    @abstractmethod
    def __add__(self, other: Union[IAnalytic1D, Real]) -> IAnalytic1D:
        raise NotImplementedError

    def __sub__(self, other: Union[IAnalytic1D, Real]) -> IAnalytic1D:
        return self.__add__(-other)

    @abstractmethod
    def __mul__(self, other: Union[IAnalytic1D, Real]) -> IAnalytic1D:
        raise NotImplementedError

    @abstractmethod
    def __truediv__(self, other: Real) -> IAnalytic1D:
        raise NotImplementedError
