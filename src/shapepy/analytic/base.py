"""
Defines the IAnalytic class to serve as base for other
analytic functions, such as Polynomial, Bezier, Trigonometric, etc
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Set, Union

from ..rbool import SubSetR1
from ..scalar.reals import Real
from ..tools import Is, vectorize


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
    def eval(self, node: Real, derivate: int = 0) -> Real:
        """
        Evaluates the given analytic function at given node.

        The optional parameter 'derivate' gives if a derivative is required

        Example
        -------
        >>> polynomial = Polynomial([1, 2, 3])  # p(x) = 1 + 2 * x + 3 * x^2
        >>> polynomial.eval(0)  # p(0) = 1 + 2 * 0 + 3 * 0^2
        1
        >>> polynomial.eval(1)  # p(1) = 1 + 2 * 1 + 3 * 1^2
        6
        >>> polynomial.eval(1, 1)  # p'(1) = 2 + 6 * 1
        8
        """
        raise NotImplementedError

    @vectorize(1, 0)
    def __call__(self, node: Real) -> Real:
        return self.eval(node, 0)

    @abstractmethod
    def __add__(self, other: Union[Real, IAnalytic]) -> IAnalytic:
        raise NotImplementedError

    @abstractmethod
    def __mul__(self, other: Union[Real, IAnalytic]) -> IAnalytic:
        raise NotImplementedError

    def __neg__(self) -> IAnalytic:
        return -1 * self

    def __sub__(self, other: Union[Real, IAnalytic]) -> IAnalytic:
        return self.__add__(-other)

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

    def __rsub__(self, other: Real) -> IAnalytic:
        return (-self).__add__(other)

    def __radd__(self, other: Real) -> IAnalytic:
        return self.__add__(other)

    def __rmul__(self, other: Real) -> IAnalytic:
        return self.__mul__(other)
