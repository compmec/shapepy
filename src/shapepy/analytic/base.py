"""
Defines the IAnalytic class to serve as base for other
analytic functions, such as Polynomial, Bezier, Trigonometric, etc
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Iterable, Set, Union

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


# pylint: disable=too-few-public-methods
class IAnalytic(ABC):
    """
    Interface Class for Analytic classes
    """

    @abstractmethod
    def __call__(self, node: Real) -> Real:
        raise NotImplementedError

    @abstractmethod
    def __add__(self, other: Union[Real, IAnalytic]) -> IAnalytic:
        raise NotImplementedError

    @abstractmethod
    def __mul__(self, other: Union[Real, IAnalytic]) -> IAnalytic:
        raise NotImplementedError

    @abstractmethod
    def __matmul__(self, other: Union[Real, IAnalytic]) -> IAnalytic:
        raise NotImplementedError


class BaseAnalytic(IAnalytic):
    """
    Base class parent of Analytic classes
    """

    def __init__(self, coefs: Iterable[Real]):
        if not Is.iterable(coefs):
            raise TypeError("Expected an iterable of coefficients")
        coefs = tuple(coefs)
        if len(coefs) == 0:
            raise ValueError("Cannot receive an empty tuple")
        self.__coefs = coefs

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
        return str(self)


def is_analytic(obj: object) -> bool:
    """
    Tells if given object is an analytic function
    """
    return Is.instance(obj, IAnalytic)


Is.analytic = is_analytic
