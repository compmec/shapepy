"""
Defines the IAnalytic class to serve as base for other
analytic functions, such as Polynomial, Bezier, Trigonometric, etc
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Iterable, Set, Union

from ..rbool import SubSetR1, WholeR1, from_any
from ..scalar.reals import Real
from ..tools import Is


@lru_cache(maxsize=None)
def pow_keys(exp: int) -> Set[int]:
    """
    Computes the basis to exponentials

    >>> pow_keys(1)
    {}
    >>> pow_keys(2)
    {2}
    >>> pow_keys(3)
    {2, 3}
    >>> pow_keys(4)
    {2, 4}
    >>> pow_keys(12)
    {2, 3, 6, 12}
    >>> pow_keys(18)
    {2, 3, 4, 5, 9, 18}
    """
    if not Is.integer(exp) or exp < 1:
        raise ValueError
    if exp == 1:
        return set()
    return pow_keys(exp // 2) | pow_keys(exp - exp // 2) | {exp}


# pylint: disable=duplicate-code
class IAnalytic(ABC):
    """
    Interface Class for Analytic classes
    """

    @property
    @abstractmethod
    def domain(self) -> SubSetR1:
        """
        Defines the domain in which the Analytic function is defined
        """
        raise NotImplementedError

    @abstractmethod
    def __call__(self, node: Real, derivate: int = 0) -> Real:
        raise NotImplementedError

    @abstractmethod
    def __add__(self, other: Union[Real, IAnalytic]) -> IAnalytic:
        raise NotImplementedError

    @abstractmethod
    def __mul__(self, other: Union[Real, IAnalytic]) -> IAnalytic:
        raise NotImplementedError

    @abstractmethod
    def shift(self, amount: Real) -> IAnalytic:
        """
        Transforms the analytic p(t) into p(t-d) by
        translating the analytic by 'd' to the right.

        Example
        -------
        >>> old_poly = Polynomial([0, 0, 0, 1])
        >>> print(old_poly)
        t^3
        >>> new_poly = shift(poly, 1)  # transform to (t-1)^3
        >>> print(new_poly)
        - 1 + 3 * t - 3 * t^2 + t^3
        """
        raise NotImplementedError

    @abstractmethod
    def scale(self, amount: Real) -> IAnalytic:
        """
        Transforms the analytic p(t) into p(A*t) by
        scaling the argument of the analytic by 'A'.

        Example
        -------
        >>> old_poly = Polynomial([0, 2, 0, 1])
        >>> print(old_poly)
        2 * t + t^3
        >>> new_poly = scale(poly, 2)
        >>> print(new_poly)
        4 * t + 8 * t^3
        """
        raise NotImplementedError

    @abstractmethod
    def clean(self) -> IAnalytic:
        """
        Cleans the curve, removing the unnecessary coefficients
        """
        raise NotImplementedError

    @abstractmethod
    def integrate(self, times: int = 1) -> IAnalytic:
        """
        Integrates the analytic function
        """
        raise NotImplementedError

    @abstractmethod
    def derivate(self, times: int = 1) -> IAnalytic:
        """
        Derivates the analytic function
        """
        raise NotImplementedError


class BaseAnalytic(IAnalytic):
    """
    Base class parent of Analytic classes
    """

    def __init__(self, coefs: Iterable[Real], domain: SubSetR1 = WholeR1()):
        if not Is.iterable(coefs):
            raise TypeError("Expected an iterable of coefficients")
        coefs = tuple(coefs)
        if len(coefs) == 0:
            raise ValueError("Cannot receive an empty tuple")
        self.__coefs = coefs
        self.domain = domain

    @property
    def domain(self) -> SubSetR1:
        return self.__domain

    @domain.setter
    def domain(self, subset: SubSetR1):
        self.__domain = from_any(subset)

    @property
    def ncoefs(self) -> int:
        """
        Returns the number of coefficients that determines the analytic
        """
        return len(self.__coefs)

    def __iter__(self):
        yield from self.__coefs

    def __getitem__(self, index):
        return self.__coefs[index]

    def __neg__(self) -> IAnalytic:
        return -1 * self

    def __pow__(self, exponent: int) -> IAnalytic:
        if not Is.integer(exponent) or exponent < 0:
            raise ValueError
        if not Is.finite(self[0]):
            raise ValueError
        if exponent == 0:
            return self.__class__([1 + 0 * self[0]])
        cache = {1: self}
        for n in pow_keys(exponent):
            cache[n] = cache[n // 2] * cache[n - n // 2]
        return cache[exponent]

    def __sub__(self, other: Union[Real, IAnalytic]) -> IAnalytic:
        return self.__add__(-other)

    def __rsub__(self, other: Real) -> IAnalytic:
        return (-self).__add__(other)

    def __radd__(self, other: Real) -> IAnalytic:
        return self.__add__(other)

    def __rmul__(self, other: Real) -> IAnalytic:
        return self.__mul__(other)

    def __repr__(self) -> str:
        if self.domain is WholeR1():
            return str(self)
        return f"{self.domain}: {self}"


def is_analytic(obj: object) -> bool:
    """
    Tells if given object is an analytic function
    """
    return Is.instance(obj, IAnalytic)


def derivate_analytic(ana: IAnalytic) -> IAnalytic:
    """
    Computes the derivative of an Analytic function
    """
    assert is_analytic(ana)
    return ana.derivate()


Is.analytic = is_analytic
