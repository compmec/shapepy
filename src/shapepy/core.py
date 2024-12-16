"""
Core file, with the basics classes and interfaces used in the package
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Iterable, Optional, Tuple, Union

Scalar = Union[int, float]
Parameter = Union[int, float]


class IObject2D(ABC):
    transform = None

    @property
    @abstractmethod
    def ndim(self) -> int:
        raise NotImplementedError

    def move(self, vector: Tuple[Scalar, Scalar]) -> IObject2D:
        return self.transform.move(self, vector)

    def scale(self, xscale: Scalar, yscale: Scalar) -> IObject2D:
        return self.transform.scale(self, xscale, yscale)

    def rotate(self, angle: Scalar, degrees: bool = False) -> IObject2D:
        if degrees:
            angle = (angle * math.pi) / 180
        return self.transform.rotate(self, angle)


class IBoolean2D(IObject2D):
    booloperate = None

    def __contains__(self, other: IObject2D) -> IBoolean2D:
        return self.booloperate.contains(self, other)

    def __invert__(self) -> IBoolean2D:
        return self.booloperate.invert(self)

    def __and__(self, other: IBoolean2D) -> IBoolean2D:
        return self.booloperate.intersect(self, other)

    def __or__(self, other: IBoolean2D) -> IBoolean2D:
        return self.booloperate.union(self, other)

    def __neg__(self) -> IBoolean2D:
        return ~self

    def __xor__(self, other: IBoolean2D) -> IBoolean2D:
        return (self & (~other)) | (other & (~self))

    def __sub__(self, other: IBoolean2D) -> IBoolean2D:
        return self & (~other)

    def __add__(self, other: IBoolean2D) -> IBoolean2D:
        return self.__or__(other)

    def __mul__(self, other: IBoolean2D) -> IBoolean2D:
        return self.__and__(other)


class Empty(IBoolean2D):
    """Empty is a singleton class to represent an empty shape

    Example use
    -----------
    >>> from shapepy import Empty
    >>> empty = Empty()
    >>> print(empty)
    Empty
    >>> (0, 0) in empty
    False
    """

    __instance = None

    @property
    def ndim(self) -> int:
        return 5

    def __new__(cls) -> Empty:
        if cls.__instance is None:
            cls.__instance = super(Empty, cls).__new__(cls)
        return cls.__instance

    def __str__(self) -> str:
        return "Empty"

    def __repr__(self) -> str:
        return self.__str__()


class Whole(IBoolean2D):
    """Whole is a singleton class to represent all plane

    Example use
    -----------
    >>> from shapepy import Whole
    >>> whole = Whole()
    >>> print(whole)
    Whole
    >>> (0, 0) in whole
    True
    """

    __instance = None

    @property
    def ndim(self) -> int:
        return 5

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Whole, cls).__new__(cls)
        return cls.__instance

    def __str__(self) -> str:
        return "Whole"

    def __repr__(self) -> str:
        return self.__str__()


class ICurve(IBoolean2D):
    @property
    def ndim(self) -> int:
        return 1

    @property
    @abstractmethod
    def lenght(self) -> Scalar:
        raise NotImplementedError


class IShape(IBoolean2D):
    @property
    def ndim(self) -> int:
        return 2

    @property
    @abstractmethod
    def area(self) -> Scalar:
        raise NotImplementedError


class IAnalytic(ABC):
    @abstractmethod
    def eval(self, node: Parameter, derivate: int = 0) -> Scalar:
        raise NotImplementedError

    @abstractmethod
    def derivate(self, times: int = 1) -> IAnalytic:
        raise NotImplementedError

    @abstractmethod
    def defintegral(self, lower: Parameter, upper: Parameter) -> Scalar:
        raise NotImplementedError

    @abstractmethod
    def roots(
        self, inflim: Optional[Parameter], suplim: Optional[Parameter]
    ) -> Iterable[Parameter]:
        raise NotImplementedError

    @abstractmethod
    def shift(self, amount: Parameter) -> IAnalytic:
        raise NotImplementedError

    @abstractmethod
    def scale(self, amount: Scalar) -> IAnalytic:
        raise NotImplementedError
