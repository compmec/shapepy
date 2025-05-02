"""
Defines the base classes for planar boolean operations

Defines the classes:
* SubSetR2
* EmptyR2
* WholeR2
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from numbers import Real
from typing import Tuple, Union

from ..angle import Angle


class Future:
    """
    Class that stores methods that are further defined.
    They are overrided by other methods in __init__.py file

    Although the classes EmptyR2 and WholeR2 don't need the
    child classes to make the union/intersection, or to verify
    if a SubSetR2 instance is inside WholeR2 for example,
    the command bellow 
    >>> (0, 0) in WholeR2()
    that checks if a point is inside WholeR2, needs the conversion
    to a SinglePoint instance, which is not defined in this file

    Another example is the definition of `__add__` method,
    which must call the function `simplify` after the `__or__`.
    The function `simplify` must know all the childs classes of SubSetR2,
    but it would lead to a circular import.

    A solution, which was considered worst is:
    * Place all the classes and the functions in a single file,
    so all the classes know all the other classes and we avoid
    a circular import.
    """

    @staticmethod
    def convert(obj: object) -> SubSetR2:
        """
        Converts an object to a SubSetR2 instance.

        This function is overrided by a function defined
        in the `shapepy.bool2d.converter.py` file

        Example
        -------
        >>> type(convert("{}"))
        <class "shapepy.bool2d.base.EmptyR2">
        """
        raise NotImplementedError

    @staticmethod
    def unite(*subsets: SubSetR2) -> SubSetR2:
        """
        Computes the union of some SubSetR2 instances

        This function is overrided by a function defined
        in the `shapepy.bool2d.bool2d.py` file
        """
        raise NotImplementedError

    @staticmethod
    def intersect(*subsets: SubSetR2) -> SubSetR2:
        """
        Computes the intersection of some SubSetR2 instances

        This function is overrided by a function defined
        in the `shapepy.bool2d.bool2d.py` file
        """
        raise NotImplementedError

    @staticmethod
    def invert(subset: SubSetR2) -> SubSetR2:
        """
        Computes the inversion of a SubSetR2 instance

        This function is overrided by a function defined
        in the `shapepy.bool2d.bool2d.py` file
        """
        raise NotImplementedError

    @staticmethod
    def contains(subseta: SubSetR2, subsetb: SubSetR2) -> bool:
        """
        Checks if the subsetb is contained by subseta

        This function is overrided by a function defined
        in the `shapepy.bool2d.bool2d.py` file
        """
        raise NotImplementedError

    @staticmethod
    def move(subset: SubSetR2, vector: Tuple[Real, Real]) -> SubSetR2:
        """
        Moves the SubSetR2 instance by given vector

        This function is overrided by a function defined
        in the `shapepy.bool2d.transform.py` file
        """
        raise NotImplementedError

    @staticmethod
    def scale(
        subset: SubSetR2, amount: Union[Real, Tuple[Real, Real]]
    ) -> SubSetR2:
        """
        Scales the SubSetR2 instance by given amount

        This function is overrided by a function defined
        in the `shapepy.bool2d.transform.py` file
        """
        raise NotImplementedError

    @staticmethod
    def rotate(subset: SubSetR2, angle: Angle) -> SubSetR2:
        """
        Rotates the SubSetR2 instance by given angle,
        in the counter-clockwise direction

        This function is overrided by a function defined
        in the `shapepy.bool2d.transform.py` file
        """
        raise NotImplementedError

    @staticmethod
    def simplify(subset: SubSetR2) -> SubSetR2:
        """
        Simplifies the SubSetR2 containers.

        This function is overrided by a function defined
        in the `shapepy.bool2d.simplify.py` file
        """
        raise NotImplementedError


class SubSetR2(ABC):
    """
    Parent classe for all the base classes that are used
    to compute the planar boolean operations
    """

    @abstractmethod
    def __eq__(self, other) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError

    def __contains__(self, other) -> bool:
        return Future.contains(self, Future.convert(other))

    def __invert__(self) -> SubSetR2:
        return Future.invert(self)

    def __or__(self, other: SubSetR2) -> SubSetR2:
        return Future.unite(self, other)

    def __and__(self, other: SubSetR2) -> SubSetR2:
        return Future.intersect(self, other)

    def __ror__(self, other):
        return self.__or__(Future.convert(other))

    def __rand__(self, other):
        return self.__and__(Future.convert(other))

    def __neg__(self):
        return Future.simplify(self.__invert__())

    def __xor__(self, other):
        return Future.simplify((self & (~other)) | (other & (~self)))

    def __add__(self, other):
        return Future.simplify(self.__or__(other))

    def __sub__(self, other):
        other = Future.convert(other)
        return Future.simplify(self.__and__(~other))

    def __mul__(self, other):
        return Future.simplify(self & other)

    def move(self, vector: Tuple[Real, Real]) -> SubSetR2:
        """
        Translates the subset on the plane, by given vector

        Parameters
        ----------
        vector: Tuple[Real, Real]
            The coordinates (x, y) of the vector
        
        Return
        ------
        SubSetR2
            The translated subset, of the same type

        Example
        -------
        >>> subset = primitive.square()
        >>> subset = subset.move((3, 4))
        """
        return Future.move(self, vector)

    def scale(self, amount: Union[Real, Tuple[Real, Real]]) -> SubSetR2:
        """
        Scales the subset on the plane by given amount.

        * If a Real number is given, scales evenly on 'x' and 'y'
        * If a pair of Real is given, scales 'x' and 'y' by different amounts

        Parameters
        ----------
        amount: Union[Real, Tuple[Real, Real]]

            The coordinates (x, y) of the vector
        
        Return
        ------
        SubSetR2
            The scaled subset, of the same type

        Example
        -------
        >>> subset = primitive.square()
        >>> subset = subset.scale(3)  # Area is 9 times bigger
        >>> subset = subset.scale((5, 2))  # Scale x by 5 times, y by 2 times
        """
        return Future.scale(self, amount)

    def rotate(self, angle: Angle) -> SubSetR2:
        """
        Rotates the subset on the clockwise direction arount the origin

        Parameters
        ----------
        angle: Angle
            The angle to rotate
        
        Return
        ------
        SubSetR2
            The rotated subset, of the same type

        Example
        -------
        >>> subset = primitive.square()
        >>> subset = subset.rotate(Angle.degrees(90))
        """
        return Future.rotate(self, angle)


class EmptyR2(SubSetR2):
    """
    Class that represents an empty set, with no points inside it

    Singleton pattern is used.
    Hence, only one instance of this class exists
    """

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __contains__(self, other) -> bool:
        return Future.convert(other) is self

    def __invert__(self):
        return WholeR2()

    def __and__(self, _):
        return self

    def __or__(self, other):
        return Future.convert(other)

    def __str__(self):
        return "EmptyR2"

    def __repr__(self):
        return "EmptyR2"

    def __eq__(self, other):
        return self is Future.convert(other)

    def __hash__(self):
        return 0


class WholeR2(SubSetR2):
    """
    Class that represents all the points on the plane R2.

    Singleton pattern is used.
    Hence, only one instance of this class exists
    """

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __contains__(self, _) -> bool:
        return True

    def __invert__(self):
        return EmptyR2()

    def __and__(self, other):
        return Future.convert(other)

    def __or__(self, other):
        Future.convert(other)
        return self

    def __str__(self):
        return "WholeR2"

    def __repr__(self):
        return "WholeR2"

    def __eq__(self, other):
        return self is Future.convert(other)

    def __hash__(self):
        return 1
