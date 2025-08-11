"""
Defines the base classes used in the bool2d submodule

* SubSetR2: Base class for all classes
* EmptyShape: Represents an empty set
* WholeShape: Represents the entire plane
"""

from __future__ import annotations

from abc import abstractmethod
from copy import copy


class SubSetR2:
    """
    Base class for all SubSetR2 classes
    """

    def __init__(self):
        pass

    @abstractmethod
    def __invert__(self) -> SubSetR2:
        """Invert shape"""

    @abstractmethod
    def __or__(self, other: SubSetR2) -> SubSetR2:
        """Union shapes"""

    @abstractmethod
    def __and__(self, other: SubSetR2) -> SubSetR2:
        """Intersection shapes"""

    @abstractmethod
    def __copy__(self) -> SubSetR2:
        """Creates a shallow copy"""

    @abstractmethod
    def __deepcopy__(self, memo) -> SubSetR2:
        """Creates a deep copy"""

    def __neg__(self) -> SubSetR2:
        """Invert the SubSetR2"""
        return ~self

    def __add__(self, other: SubSetR2):
        """Union of SubSetR2"""
        return self | other

    def __mul__(self, value: SubSetR2):
        """Intersection of SubSetR2"""
        return self & value

    def __sub__(self, value: SubSetR2):
        """Subtraction of SubSetR2"""
        return self & (~value)

    def __xor__(self, other: SubSetR2):
        """XOR of SubSetR2"""
        return (self - other) | (other - self)

    def __bool__(self) -> bool:
        """Area is positive ?"""
        return float(self) > 0


class EmptyShape(SubSetR2):
    """EmptyShape is a singleton class to represent an empty shape

    Example use
    -----------
    >>> from shapepy import EmptyShape
    >>> empty = EmptyShape()
    >>> print(empty)
    EmptyShape
    >>> print(float(empty))  # Area
    0.0
    >>> (0, 0) in empty
    False
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(EmptyShape, cls).__new__(cls)
        return cls.__instance

    def __copy__(self) -> EmptyShape:
        return self

    def __deepcopy__(self, memo) -> EmptyShape:
        return self

    def __or__(self, other: SubSetR2) -> SubSetR2:
        return copy(other)

    def __and__(self, other: SubSetR2) -> SubSetR2:
        return self

    def __sub__(self, other: SubSetR2) -> SubSetR2:
        return self

    def __float__(self) -> float:
        return float(0)

    def __invert__(self) -> SubSetR2:
        return WholeShape()

    def __contains__(self, other: SubSetR2) -> bool:
        return self is other

    def __str__(self) -> str:
        return "EmptyShape"

    def __repr__(self) -> str:
        return self.__str__()


class WholeShape(SubSetR2):
    """WholeShape is a singleton class to represent all plane

    Example use
    -----------
    >>> from shapepy import WholeShape
    >>> whole = WholeShape()
    >>> print(whole)
    WholeShape
    >>> print(float(whole))  # Area
    inf
    >>> (0, 0) in whole
    True
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(WholeShape, cls).__new__(cls)
        return cls.__instance

    def __copy__(self) -> WholeShape:
        return self

    def __deepcopy__(self, memo) -> WholeShape:
        return self

    def __or__(self, other: SubSetR2) -> WholeShape:
        return self

    def __and__(self, other: SubSetR2) -> SubSetR2:
        return copy(other)

    def __float__(self) -> float:
        return float("inf")

    def __invert__(self) -> SubSetR2:
        return EmptyShape()

    def __contains__(self, other: SubSetR2) -> bool:
        return True

    def __str__(self) -> str:
        return "WholeShape"

    def __repr__(self) -> str:
        return self.__str__()

    def __sub__(self, other: SubSetR2) -> SubSetR2:
        return ~other
