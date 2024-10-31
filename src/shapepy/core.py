"""
Core file, with the basics classes and interfaces used in the package
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Union

Scalar = Union[int, float]
Parameter = Union[int, float]


class IObject2D(ABC):
    pass


class IBoolean2D(IObject2D):

    @abstractmethod
    def __invert__(self) -> IBoolean2D:
        raise NotImplementedError

    def __and__(self, other: IBoolean2D) -> IBoolean2D:
        return other.__rand__(self)

    @abstractmethod
    def __rand__(self, other: IBoolean2D) -> IBoolean2D:
        raise NotImplementedError

    def __or__(self, other: IBoolean2D) -> IBoolean2D:
        return other.__ror__(self)

    @abstractmethod
    def __ror__(self, other: IBoolean2D) -> IBoolean2D:
        raise NotImplementedError

    def __neg__(self) -> IBoolean2D:
        return ~self

    def __xor__(self, other: IBoolean2D) -> IBoolean2D:
        return other.__rxor__(self)

    def __rxor__(self, other: IBoolean2D) -> IBoolean2D:
        return (self & (~other)) | (other & (~self))

    def __sub__(self, other: IBoolean2D) -> IBoolean2D:
        return ~(other.__rsub__(self))

    def __rsub__(self, other: IBoolean2D) -> IBoolean2D:
        return other & (~self)

    def __add__(self, other: IBoolean2D) -> IBoolean2D:
        return other.__radd__(self)

    def __radd__(self, other: IBoolean2D) -> IBoolean2D:
        return self.__ror__(other)

    def __mul__(self, other: IBoolean2D) -> IBoolean2D:
        return other.__rmul__(self)

    def __rmul__(self, other: IBoolean2D) -> IBoolean2D:
        return self.__rand__(other)


class Empty(IBoolean2D):
    """Empty is a singleton class to represent an empty shape

    Example use
    -----------
    >>> from shapepy import Empty
    >>> empty = Empty()
    >>> print(empty)
    Empty
    >>> print(float(empty))  # Area
    0.0
    >>> (0, 0) in empty
    False
    """

    __instance = None

    def __new__(cls) -> Empty:
        if cls.__instance is None:
            cls.__instance = super(Empty, cls).__new__(cls)
        return cls.__instance

    def __or__(self, other: IBoolean2D) -> IBoolean2D:
        return other

    def __ror__(self, other: IBoolean2D) -> IBoolean2D:
        return other

    def __and__(self, _: IBoolean2D) -> Empty:
        return self

    def __rand__(self, _: IBoolean2D) -> Empty:
        return self

    def __sub__(self, _: IBoolean2D) -> Empty:
        return self

    def __rsub__(self, other: IBoolean2D) -> IBoolean2D:
        return other

    def __xor__(self, other: IBoolean2D) -> IBoolean2D:
        return other

    def __rxor__(self, other: IBoolean2D) -> IBoolean2D:
        return other

    def __float__(self) -> float:
        return float(0)

    def __invert__(self) -> Whole:
        return Whole()

    def __contains__(self, other: IObject2D) -> bool:
        return self is other

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
    >>> print(float(whole))  # Area
    inf
    >>> (0, 0) in whole
    True
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Whole, cls).__new__(cls)
        return cls.__instance

    def __or__(self, _: IBoolean2D) -> Whole:
        return self

    def __ror__(self, _: IBoolean2D) -> Whole:
        return self

    def __and__(self, other: IBoolean2D) -> IBoolean2D:
        return other

    def __rand__(self, other: IBoolean2D) -> IBoolean2D:
        return other

    def __sub__(self, other: IBoolean2D) -> IBoolean2D:
        return ~other

    def __rsub__(self, _: IBoolean2D) -> Empty:
        return Empty()

    def __xor__(self, other: IBoolean2D) -> IBoolean2D:
        return ~other

    def __rxor__(self, other: IBoolean2D) -> IBoolean2D:
        return ~other

    def __invert__(self) -> Empty:
        return Empty()

    def __contains__(self, _: IObject2D) -> bool:
        return True

    def __str__(self) -> str:
        return "Whole"

    def __repr__(self) -> str:
        return self.__str__()


class ICurve(IObject2D):
    @property
    @abstractmethod
    def lenght(self) -> Scalar:
        raise NotImplementedError


class IShape(IObject2D):
    @property
    @abstractmethod
    def area(self) -> Scalar:
        raise NotImplementedError
