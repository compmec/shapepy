"""
Core file, with the basics classes and interfaces used in the package
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Iterable, Optional, Tuple, Union

Scalar = Union[int, float]
Parameter = Union[int, float]


class Math:
    """
    Contains math functions, to easy change everywhere
    """

    # General math
    arctan2 = math.atan2
    sqrt = math.sqrt
    floor = math.floor
    ceil = math.ceil
    inf = math.inf

    # Trigonometric
    tau = math.tau
    sin = math.sin
    cos = math.cos

    # Hyperbolic
    sinh = math.sinh
    cosh = math.cosh


class Configuration:
    """
    Configuration class for the package
    """

    AUTOEXPAND = True
    AUTOSIMPLIFY = True


class IObject2D(ABC):
    """
    The 2D base class, to be parent of the other classes.
    An object that inherits from it means it's a plane object
    """

    transform = None

    @property
    @abstractmethod
    def ndim(self) -> int:
        """
        Tells the number of dimensions the object has.
        * A point is a 0-D object
        * A curve is a 1-D object
        * A shape is a 2-D object
        """
        raise NotImplementedError

    def move(self, vector: Tuple[Scalar, Scalar]) -> IObject2D:
        """
        Moves the object in the plane by the given vector

        Parameters
        ----------
        vector: Point
            The pair (x, y) that must be added to the coordinates

        Example
        -------
        >>> mypoint = Point(0, 0)
        >>> mypoint.move((1, 2))
        (1, 2)
        """
        raise NotImplementedError

    def scale(self, xscale: Scalar, yscale: Scalar) -> IObject2D:
        """
        Scales the object in the X and Y directions

        Parameters
        ----------
        xscale: Scalar
            The amount to be scaled in the X direction
        yscale: Scalar
            The amount to be scaled in the Y direction

        Example
        -------
        >>> mypoint = Point(2, 3)
        >>> mypoint.scale(5, 3)
        (10, 9)
        """
        raise NotImplementedError

    def rotate(self, uangle: Scalar) -> IObject2D:
        """
        Rotates the object around the origin.

        The angle mesure is unitary:
        * angle = 1 means 360 degrees rotation
        * angle = 0.5 means 180 degrees rotation
        * angle = 0.125 means 45 degrees rotation

        Parameters
        ----------
        angle: Scalar
            The unitary angle the be rotated

        Example
        -------
        >>> mypoint = Point(2, 3)
        >>> mypoint.rotate(180/360)  # 180 degrees
        (-2, -3)
        >>> mypoint.rotate(90/360)  # 90 degrees
        (-3, 2)
        """
        raise NotImplementedError


class IBoolean2D(IObject2D):
    """
    Boolean base class, that implements the methods responsible to make the
    boolean operations, like union, intersection, xor, invert, and so on

    It also contains the method __contains__ to check if an object is
    entirely contained in this object, meaning if it's a subset
    """

    booloperate = None

    def __contains__(self, other: IObject2D) -> IBoolean2D:
        if isinstance(other, IObject2D):
            if other.ndim > self.ndim:
                return False
            if isinstance(other, Empty):
                return True
        return self.booloperate.contains(self, other)

    def __invert__(self) -> IBoolean2D:
        return self.booloperate.invert(self)

    def __neg__(self) -> IBoolean2D:
        return ~self

    def __and__(self, other: IBoolean2D) -> IBoolean2D:
        if isinstance(other, (Empty, Whole)):
            return other.__rand__(self)
        return self.booloperate.intersect(self, other)

    def __or__(self, other: IBoolean2D) -> IBoolean2D:
        if isinstance(other, (Empty, Whole)):
            return other.__ror__(self)
        return self.booloperate.union(self, other)

    def __xor__(self, other: IBoolean2D) -> IBoolean2D:
        if isinstance(other, (Empty, Whole)):
            return other.__rxor__(self)
        return (self & (~other)) | (other & (~self))

    def __sub__(self, other: IBoolean2D) -> IBoolean2D:
        if isinstance(other, (Empty, Whole)):
            return other.__rsub__(self)
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
        return 0

    def __new__(cls) -> Empty:
        if cls.__instance is None:
            cls.__instance = super(Empty, cls).__new__(cls)
        return cls.__instance

    def __str__(self) -> str:
        return "Empty"

    def __repr__(self) -> str:
        return self.__str__()

    def __contains__(self, other):
        return other is self

    def __invert__(self):
        return Whole()

    def __and__(self, _):
        return self

    def __rand__(self, _):
        return self

    def __or__(self, other):
        return other

    def __ror__(self, other):
        return other

    def __xor__(self, other):
        return other

    def __rxor__(self, other):
        return other

    def __sub__(self, _):
        return self

    def __rsub__(self, other):
        return other

    def move(self, vector: Tuple[Scalar, Scalar]) -> Empty:
        return self

    def scale(self, xscale, yscale) -> Empty:
        return self

    def rotate(self, uangle) -> Empty:
        return self


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

    def __contains__(self, _):
        return True

    def __invert__(self):
        return Empty()

    def __and__(self, other):
        return other

    def __rand__(self, other):
        return other

    def __or__(self, _):
        return self

    def __ror__(self, _):
        return self

    def __xor__(self, other):
        return ~other

    def __rxor__(self, other):
        return ~other

    def __sub__(self, other):
        return ~other

    def __rsub__(self, _):
        return Empty()

    def move(self, vector: Tuple[Scalar, Scalar]) -> Whole:
        return self

    def scale(self, xscale, yscale) -> Whole:
        return self

    def rotate(self, uangle) -> Whole:
        return self


class IShape(IBoolean2D):
    """
    This is an abstract class, that serves as interface to create a shape
    """

    @property
    def ndim(self) -> int:
        return 2

    @property
    @abstractmethod
    def area(self) -> Scalar:
        """
        Gives the area of the curve.
        It can be negative, if the jordan curve is defined clockwise
        """
        raise NotImplementedError


class IAnalytic(ABC):
    """
    This is an abstract class that serves as interface for an analytic function

    It contains the basic methods to evaluate this function,
    to compute the derivate, find roots, shift, scale, compute integrals, etc
    """

    @abstractmethod
    def eval(self, node: Parameter, derivate: int = 0) -> Scalar:
        """
        Evaluates the given analytic function p(t) at given node t

        Parameters
        ----------
        node: Parameter
            The value of 't' which the analytic function must be evaluated
        derivate: int, default = 0
            The k-th derivative to be computed.
            As default, means the function is not derivated
        """
        raise NotImplementedError

    @abstractmethod
    def derivate(self, times: int = 1) -> IAnalytic:
        """
        Derivates the analytic function p(t), giving another analytic function

        Parameters
        ----------
        times: int
            The quantity of times to be derived
        """
        raise NotImplementedError

    @abstractmethod
    def defintegral(self, lower: Parameter, upper: Parameter) -> Scalar:
        """
        Computes the defined integral of p(t) between the intervals [a, b]

        I = int_a^b p(t) dt

        Parameters
        ----------
        lower: Parameter
            The lower bound of the integral, the value of 'a'
        upper: Parameter
            The upper bound of the integral, the value of 'b'
        """
        raise NotImplementedError

    @abstractmethod
    def roots(
        self,
        inflim: Optional[Parameter] = None,
        suplim: Optional[Parameter] = None,
    ) -> Iterable[Parameter]:
        """
        Computes the roots of the analytic function

        The parameters gives the limits of research of this function

        If no limits are given, it computes all the roots in the domain

        Parameters
        ----------
        inflim: Parameter, default = None
            The lower bound of research
        suplim: Parameter, default = None
            The upper bound of resarch
        """
        raise NotImplementedError

    @abstractmethod
    def shift(self, amount: Parameter) -> IAnalytic:
        """
        Shifts the analytic function by given amount,
        returning the function q(t) = p(t-a) which 'a' is the amount

        Parameters
        ----------
        amount: Parameter
            The value of 'a', the quantity of the function to be shifted
        """
        raise NotImplementedError

    @abstractmethod
    def scale(self, amount: Scalar) -> IAnalytic:
        """
        Scales the analytic function by given amount,
        returning the function q(t) = p(a*t) which 'a' is the amount

        Parameters
        ----------
        amount: Parameter
            The value of 'a', the quantity of the function to be scaled
        """
        raise NotImplementedError
