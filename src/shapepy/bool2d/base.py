"""
Defines the base classes used in the bool2d submodule

* SubSetR2: Base class for all classes
* EmptyShape: Represents an empty set
* WholeShape: Represents the entire plane
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Iterable, Tuple, Union

from ..geometry.point import Point2D
from ..loggers import debug
from ..scalar.angle import Angle
from ..scalar.reals import Real
from .config import Config
from .density import Density


class SubSetR2:
    """
    Base class for all SubSetR2 classes
    """

    def __init__(self):
        pass

    @debug("shapepy.bool2d.base")
    def __invert__(self) -> SubSetR2:
        """Invert shape"""
        result = Future.invert(self)
        return Future.clean(result) if Config.clean["inv"] else result

    @debug("shapepy.bool2d.base")
    def __or__(self, other: SubSetR2) -> SubSetR2:
        """Union shapes"""
        result = Future.unite((self, other))
        return Future.clean(result) if Config.clean["or"] else result

    @debug("shapepy.bool2d.base")
    def __and__(self, other: SubSetR2) -> SubSetR2:
        """Intersection shapes"""
        result = Future.intersect((self, other))
        return Future.clean(result) if Config.clean["and"] else result

    @abstractmethod
    def __copy__(self) -> SubSetR2:
        """Creates a shallow copy"""

    @abstractmethod
    def __deepcopy__(self, memo) -> SubSetR2:
        """Creates a deep copy"""

    def __neg__(self) -> SubSetR2:
        """Invert the SubSetR2"""
        result = Future.invert(self)
        return Future.clean(result) if Config.clean["neg"] else result

    @debug("shapepy.bool2d.base")
    def __add__(self, other: SubSetR2):
        """Union of SubSetR2"""
        result = Future.unite((self, other))
        return Future.clean(result) if Config.clean["add"] else result

    @debug("shapepy.bool2d.base")
    def __mul__(self, other: SubSetR2):
        """Intersection of SubSetR2"""
        result = Future.intersect((self, other))
        return Future.clean(result) if Config.clean["mul"] else result

    @debug("shapepy.bool2d.base")
    def __sub__(self, other: SubSetR2):
        """Subtraction of SubSetR2"""
        result = Future.intersect((self, Future.invert(other)))
        return Future.clean(result) if Config.clean["sub"] else result

    @debug("shapepy.bool2d.base")
    def __xor__(self, other: SubSetR2):
        """XOR of SubSetR2"""
        result = Future.xor((self, other))
        return Future.clean(result) if Config.clean["xor"] else result

    def __repr__(self) -> str:  # pragma: no cover
        return str(self)

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError

    @debug("shapepy.bool2d.base")
    def __contains__(self, other: SubSetR2) -> bool:
        return Future.contains(self, other)

    def clean(self) -> SubSetR2:
        """
        Cleans the subset, changing its representation into a simpler form

        Parameters
        ----------
        :return: The same instance
        :rtype: SubSetR2

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()
        >>> circle.clean()
        """
        return Future.clean(self)

    @abstractmethod
    def move(self, vector: Point2D) -> SubSetR2:
        """
        Moves/translate entire shape by an amount

        Parameters
        ----------

        point : Point2D
            The amount to move

        :return: The same instance
        :rtype: SubSetR2

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()
        >>> circle.move(1, 2)

        """
        raise NotImplementedError

    @abstractmethod
    def scale(self, amount: Union[Real, Tuple[Real, Real]]) -> SubSetR2:
        """
        Scales entire subset by an amount

        Parameters
        ----------

        amount : Real | Tuple[Real, Real]
            The amount to scale in horizontal and vertical direction

        :return: The same instance
        :rtype: SubSetR2

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()
        >>> circle.scale((2, 3))

        """
        raise NotImplementedError

    @abstractmethod
    def rotate(self, angle: Angle) -> SubSetR2:
        """
        Rotates entire shape around the origin by an amount

        Parameters
        ----------

        angle : Angle
            The amount to rotate around origin

        :return: The same instance
        :rtype: SubSetR2

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()
        >>> circle.rotate(degrees(90))

        """
        raise NotImplementedError

    @abstractmethod
    def density(self, center: Point2D) -> Density:
        """
        Computes the density of the subset around given point

        Parameters
        ----------

        center : Point2D
            The position to measure the density

        :return: The density in the interval [0, 1]
        :rtype: Real

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle(radius=1)
        >>> circle.density((0, 0))
        1
        >>> circle.density((5, 0))
        0
        >>> circle.density((1, 0))
        0.5
        """
        raise NotImplementedError


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
        return Future.convert(other)

    def __add__(self, other: SubSetR2) -> SubSetR2:
        return Future.convert(other)

    def __and__(self, _: SubSetR2) -> SubSetR2:
        return self

    def __mul__(self, _: SubSetR2) -> SubSetR2:
        return self

    def __sub__(self, _: SubSetR2) -> SubSetR2:
        return self

    def __neg__(self) -> SubSetR2:
        return WholeShape()

    def __invert__(self) -> SubSetR2:
        return WholeShape()

    def __xor__(self, other: SubSetR2) -> SubSetR2:
        return Future.convert(other)

    def __contains__(self, other: SubSetR2) -> bool:
        return self is Future.convert(other)

    def __str__(self) -> str:
        return "EmptyShape"

    def __bool__(self) -> bool:
        return False

    def __hash__(self):
        return 0

    def move(self, _):
        return self

    def scale(self, _):
        return self

    def rotate(self, _):
        return self

    @debug("shapepy.bool2d.base")
    def density(self, center: Point2D) -> Density:
        return Density.zero


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

    def __add__(self, _: SubSetR2) -> WholeShape:
        return self

    def __and__(self, other: SubSetR2) -> SubSetR2:
        return Future.convert(other)

    def __mul__(self, other: SubSetR2) -> WholeShape:
        return Future.convert(other)

    def __neg__(self) -> SubSetR2:
        return EmptyShape()

    def __invert__(self) -> SubSetR2:
        return EmptyShape()

    def __xor__(self, other: SubSetR2) -> SubSetR2:
        result = ~Future.convert(other)
        return Future.clean(result) if Config.clean["xor"] else result

    def __contains__(self, other: SubSetR2) -> bool:
        return True

    def __str__(self) -> str:
        return "WholeShape"

    def __sub__(self, other: SubSetR2) -> SubSetR2:
        result = ~Future.convert(other)
        return Future.clean(result) if Config.clean["xor"] else result

    def __bool__(self) -> bool:
        return True

    def __hash__(self):
        return 1

    def move(self, _):
        return self

    def scale(self, _):
        return self

    def rotate(self, _):
        return self

    def density(self, center: Point2D) -> Density:
        return Density.one


# pylint: disable=duplicate-code
class Future:
    """
    Class that stores methods that are further defined.
    They are overrided by other methods in __init__.py file

    Although the classes EmptyShape and WholeShape don't need the
    child classes to make the union/intersection, or to verify
    if a SubSetR2 instance is inside WholeShape for example,
    the command bellow
    >>> (0, 0) in WholeShape()
    that checks if a point is inside WholeShape, needs the conversion
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
    def convert(subset: SubSetR2) -> SubSetR2:
        """
        Converts an object into a SubSetR2
        """
        raise NotImplementedError

    @staticmethod
    def unite(subsets: Iterable[SubSetR2]) -> SubSetR2:
        """
        Computes the union of some SubSetR2 instances

        This function is overrided by a function defined
        in the `shapepy.bool2d.boolean.py` file
        """
        raise NotImplementedError

    @staticmethod
    def intersect(subsets: Iterable[SubSetR2]) -> SubSetR2:
        """
        Computes the intersection of some SubSetR2 instances

        This function is overrided by a function defined
        in the `shapepy.bool2d.boolean.py` file
        """
        raise NotImplementedError

    @staticmethod
    def invert(subset: SubSetR2) -> SubSetR2:
        """
        Computes the complementar set of given SubSetR2 instance

        This function is overrided by a function defined
        in the `shapepy.bool2d.boolean.py` file
        """
        raise NotImplementedError

    @staticmethod
    def xor(subset: SubSetR2) -> SubSetR2:
        """
        Computes the exclusive union of given subsets

        This function is overrided by a function defined
        in the `shapepy.bool2d.boolean.py` file
        """
        raise NotImplementedError

    @staticmethod
    def clean(subset: SubSetR2) -> SubSetR2:
        """
        Cleans and simplifies given subset

        This function is overrided by a function defined
        in the `shapepy.bool2d.boolean.py` file
        """
        raise NotImplementedError

    @staticmethod
    def contains(subseta: SubSetR2, subsetb: SubSetR2) -> bool:
        """
        Checks if subsetb is contained in subseta

        This function is overrided by a function defined
        in the `shapepy.bool2d.boolean.py` file
        """
        raise NotImplementedError
