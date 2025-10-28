"""
Defines the basis structure to store subsets of real line.
The main purpose of this module is to be returned from analytics roots
or when concatenating piecewise curves

Here we define 5 classes:
* EmptyR1 : Represents an empty set {} of the real line R1
* WholeR1 : Represents the entire real line R1
* SingleR1 : Represents a subset of R1 with only one finite element
* IntervalR1 : Represents a subset of R1 with continuous points
* DisjointR1 : Represents the union of some SingleR1 and IntervalR1

With them, we can verify if one subset contains another subset
It's possible to make the standard boolean operations, like union,
intersection, inversion, xor and so on
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple, Union

from ..scalar.reals import Math, Real
from ..tools import Is, NotExpectedError, To


class Future:
    """
    Class that stores methods that are further defined.
    They are overrided by other methods in __init__.py file
    """

    @staticmethod
    def convert(obj: object) -> SubSetR1:
        """
        Converts an object to a SubSetR1 instance.

        This function is overrided by a function defined
        in the `converter.py` file

        Example
        -------
        >>> type(convert("{}"))
        <class "shapepy.rbool.base.EmptyR1">
        """
        raise NotExpectedError

    @staticmethod
    def unite(*subsets: SubSetR1) -> SubSetR1:
        """
        Computes the union of some SubSetR1 instances

        This function is overrided by a function defined
        in the `shapepy.rbool.bool1d.py` file
        """
        raise NotExpectedError

    @staticmethod
    def intersect(*subsets: SubSetR1) -> SubSetR1:
        """
        Computes the intersection of some SubSetR1 instances

        This function is overrided by a function defined
        in the `shapepy.rbool.bool1d.py` file
        """
        raise NotExpectedError

    @staticmethod
    def invert(subset: SubSetR1) -> SubSetR1:
        """
        Computes the inversion of a SubSetR1 instance

        This function is overrided by a function defined
        in the `shapepy.rbool.bool1d.py` file
        """
        raise NotExpectedError

    @staticmethod
    def contains(subseta: SubSetR1, subsetb: SubSetR1) -> bool:
        """
        Checks if the subsetb is contained by subseta

        This function is overrided by a function defined
        in the `shapepy.rbool.bool1d.py` file
        """
        raise NotExpectedError

    @staticmethod
    def move(subset: SubSetR1, vector: Tuple[Real, Real]) -> SubSetR1:
        """
        Moves the SubSetR1 instance by given vector

        This function is overrided by a function defined
        in the `shapepy.rbool.transform.py` file
        """
        raise NotExpectedError

    @staticmethod
    def scale(
        subset: SubSetR1, amount: Union[Real, Tuple[Real, Real]]
    ) -> SubSetR1:
        """
        Scales the SubSetR1 instance by given amount

        This function is overrided by a function defined
        in the `shapepy.rbool.transform.py` file
        """
        raise NotExpectedError


class SubSetR1(ABC):
    """
    General class to be parent of some others.

    It represents an arbitrary subset of R1.
    """

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __contains__(self, other):
        raise NotImplementedError

    def move(self, amount: Real) -> SubSetR1:
        """
        Translates the entire subset of R1 to the right by given amount

        new_set = {x + a for x in old_set}

        Parameters
        ----------
        amount : Real
            The quantity to be translated

        Return
        ------
        SubSetR1
            The translated subset

        """
        return Future.move(self, amount)

    def scale(self, amount: Real) -> SubSetR1:
        """
        Scales the entire subset of R1 to the right by given amount

        new_set = {a * x for x in old_set}

        Negative values are valid.

        Parameters
        ----------
        amount : Real
            The quantity to be scaled. Cannot be zero.

        Return
        ------
        SubSetR1
            The scaled subset
        """
        return Future.scale(self, amount)

    def __invert__(self):
        return Future.invert(self)

    def __or__(self, other):
        return Future.unite(self, Future.convert(other))

    def __and__(self, other):
        return Future.intersect(self, Future.convert(other))

    def __ror__(self, other):
        return self.__or__(Future.convert(other))

    def __rand__(self, other):
        return self.__and__(Future.convert(other))

    def __xor__(self, other):
        other = Future.convert(other)
        return (self & (~other)) | (other & (~self))

    def __sub__(self, other):
        return self & (~Future.convert(other))

    def __rsub__(self, other):
        return (~self) & Future.convert(other)

    def __rxor__(self, other):
        return self ^ Future.convert(other)

    def __repr__(self):
        return self.__str__()

    def __ne__(self, other):
        return not self == other


class EmptyR1(SubSetR1):
    """
    EmptyR1 class is a singleton that represents an empty set

    It's equivalent to: EmptyR1 = {}
    """

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __contains__(self, other) -> bool:
        if Is.real(other):
            return False
        return Future.convert(other) is self

    def move(self, amount: Real) -> SubSetR1:
        To.finite(amount)  # Checks if it's finite
        return self

    def scale(self, amount: Real) -> SubSetR1:
        To.finite(amount)  # Checks if it's finite
        return self

    def __invert__(self):
        return WholeR1()

    def __and__(self, other):
        Future.convert(other)
        return self

    def __or__(self, other):
        return Future.convert(other)

    def __rand__(self, other):
        Future.convert(other)
        return self

    def __ror__(self, other):
        return Future.convert(other)

    def __str__(self):
        return r"{}"

    def __repr__(self):
        return "EmptyR1"

    def __eq__(self, other):
        return self is Future.convert(other)

    def __hash__(self):
        return 0


class WholeR1(SubSetR1):
    """
    WholeR1 class is a singleton that represents the entire real line

    It's equivalent to: WholeR1 = (-inf, +inf)
    """

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __contains__(self, other) -> bool:
        if Is.real(other):
            return True
        Future.convert(other)
        return True

    def move(self, amount: Real) -> SubSetR1:
        To.finite(amount)  # Checks if it's finite
        return self

    def scale(self, amount: Real) -> SubSetR1:
        To.finite(amount)  # Checks if it's finite
        return self

    def __invert__(self):
        return EmptyR1()

    def __and__(self, other):
        return Future.convert(other)

    def __or__(self, other):
        Future.convert(other)
        return self

    def __rand__(self, other):
        return Future.convert(other)

    def __ror__(self, other):
        Future.convert(other)
        return self

    def __str__(self):
        return "(" + str(Math.NEGINF) + ", " + str(Math.POSINF) + ")"

    def __repr__(self):
        return "WholeR1"

    def __eq__(self, other):
        return self is Future.convert(other)

    def __hash__(self):
        return 1
