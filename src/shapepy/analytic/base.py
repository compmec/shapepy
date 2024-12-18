"""
This file contains the class BaseAnalytic that serves as base class for other
analytic functions like Polynomial, Trignomial and Hypernomial

It states the natural relations of iteration, __sub__, __pow__, etc
"""
from __future__ import annotations

from abc import abstractmethod
from functools import lru_cache
from typing import Any, Iterable, Union

from ..core import IAnalytic, Parameter, Scalar


@lru_cache
def keys_pow(exp):
    """
    Computes the degrees of pow that needs to use in __pow__

    keys(1)  # {}
    keys(2)  # {2}
    keys(3)  # {2, 3}
    keys(4)  # {2, 4}
    keys(12)  # {2, 3, 6, 12}
    keys(18)  # {2, 3, 4, 5, 9, 18}
    """
    if exp == 1:
        return set()
    return keys_pow(exp // 2) | keys_pow(exp - exp // 2) | {exp}


class BaseAnalytic(IAnalytic):
    """
    BaseAnalytic class serves as base class for other analytic classes
    like Polynomial, Trignomial and Hypernomial.
    """

    def __init__(self, coefs: Iterable[Scalar]):
        self.__coefs = list(coefs)

    def __iter__(self):
        yield from self.__coefs

    def __len__(self):
        return len(self.__coefs)

    def __getitem__(self, index):
        return self.__coefs[index]

    def __setitem__(self, key, newvalue):
        self.__coefs[key] = newvalue

    def __floordiv__(self, other: Union[Any, BaseAnalytic]) -> BaseAnalytic:
        return self.__divmod__(other)[0]

    def __mod__(self, other: Union[Any, BaseAnalytic]) -> BaseAnalytic:
        return self.__divmod__(other)[1]

    def __truediv__(self, other: Scalar) -> BaseAnalytic:
        div, res = self.__divmod__(other)
        if res != 0:
            raise ValueError(f"Cannot divide {self} by {other}")
        return div

    def __pow__(self, exponent: int) -> BaseAnalytic:
        exponent = int(exponent)
        if exponent < 0:
            raise ValueError
        if exponent == 0:
            return self.__class__([1 + 0 * sum(self)])
        needs = sorted(keys_pow(exponent))
        cache = {1: self}
        for need in needs:
            cache[need] = cache[need // 2] * cache[need - need // 2]
        return cache[exponent]

    @abstractmethod
    def __add__(self, other: Any) -> BaseAnalytic:
        raise NotImplementedError

    @abstractmethod
    def __neg__(self) -> BaseAnalytic:
        raise NotImplementedError

    @abstractmethod
    def __mul__(self, other: Any) -> BaseAnalytic:
        raise NotImplementedError

    @abstractmethod
    def __divmod__(self, other: Any) -> BaseAnalytic:
        raise NotImplementedError

    def __sub__(self, other: Union[Any, BaseAnalytic]) -> BaseAnalytic:
        return self.__add__(-other)

    def __rsub__(self, other: Any) -> BaseAnalytic:
        return (-self).__add__(other)

    def __radd__(self, other: Any) -> BaseAnalytic:
        return self.__add__(other)

    def __rmul__(self, other: Any) -> BaseAnalytic:
        return self.__mul__(other)

    def __call__(self, node: Parameter) -> Any:
        return self.eval(node, 0)

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IAnalytic):
            other = self.__class__([other])
        if not isinstance(other, self.__class__):
            return False
        if len(self) != len(other):
            return False
        return all(abs(coi - coj) < 1e-12 for coi, coj in zip(self, other))
