"""
Defines the Angle class

This class is used to handle conversions between radians/degrees/turns
It is an abstraction that to not handle float angle measured in radians
"""

from __future__ import annotations

import re
from numbers import Real

from ..loggers import debug
from ..scalar.reals import Math
from ..tools import Is, To


@debug("shapepy.scalar.angle")
def radians(value: Real) -> Angle:
    """
    Gives an Angle instance for given value measured in radians

    Parameters
    ----------
    value : Real
        The angle measured in radians

    Return
    ------
    Angle
        The Angle instance

    Example
    -------
    >>> radians(0)
    0 deg
    >>> radians(math.pi/2)
    90 deg
    >>> radians(math.pi)
    180 deg
    >>> radians(3*math.pi/2)
    270 deg
    >>> radians(2*math.pi)
    0 deg
    """
    value = To.finite(Math.fmod(value, Math.tau))
    return degrees(Math.degrees(value))


@debug("shapepy.scalar.angle")
def degrees(value: Real) -> Angle:
    """
    Gives an Angle instance for given value measured in degrees

    Parameters
    ----------
    value : Real
        The angle measured in degrees

    Return
    ------
    Angle
        The Angle instance

    Example
    -------
    >>> degrees(0)
    0 deg
    >>> degrees(90)
    90 deg
    >>> degrees(180)
    180 deg
    >>> degrees(270)
    270 deg
    >>> degrees(360)
    0 deg
    >>> degrees(720)
    0 deg
    """
    value = To.finite(value)
    direction = To.integer(round(value / 90))
    part = value - 90 * direction
    part = To.rational(part, 360) if Is.rational(part) else part / 360
    return Angle(direction, part)


@debug("shapepy.scalar.angle")
def turns(value: Real) -> Angle:
    """
    Gives an Angle instance for given value measured in turns

    Parameters
    ----------
    value : Real
        The angle measured in turns

    Return
    ------
    Angle
        The Angle instance

    Example
    -------
    >>> turns(0)
    0 deg
    >>> turns(0.25)
    90 deg
    >>> turns(0.50)
    180 deg
    >>> turns(0.75)
    270 deg
    >>> turns(1)
    0 deg
    >>> turns(2)
    0 deg
    """
    value = 4 * To.finite(value)
    direction = To.integer(round(value))
    part = value - direction
    return Angle(int(direction), part / 4)


@debug("shapepy.scalar.angle")
def arg(xcoord: Real, ycoord: Real) -> Angle:
    """
    Compute the complex argument of the point (x, y)

    Parameters
    ----------
    xcoord : Real
        The x-coordinate of the point
    ycoord : Real
        The y-coordinate of the point

    Returns
    -------
    Angle
        The Angle instance such tangent gives y/x

    Examples
    --------
    >>> arg(1, 0)  # 0 degrees
    0 deg
    >>> arg(1, 1)  # 45 degrees
    45 deg
    >>> arg(0, 1)  # 90 degrees
    90 deg
    >>> arg(-1, 1)  # 135 degrees
    135 deg
    """
    if ycoord == 0:
        return Angle(0, 0) if xcoord >= 0 else Angle(2, 0)
    if xcoord == 0:
        return Angle(1, 0) if ycoord > 0 else Angle(3, 0)
    return radians(Math.atan2(ycoord, xcoord))


class Angle:
    """
    Class that stores an angle.

    Handles the operations such as __add__, __sub__, etc
    """

    def __init__(self, direction: int, part: Real):
        if not Is.integer(direction):
            raise TypeError(f"Expected integer value, got {type(direction)}")
        if not Is.finite(part):
            raise TypeError(f"Expected numeric value, got {type(part)}")
        if abs(part) > 0.125:
            raise ValueError(f"Expected {part} be in [-1/8, 1/8]")
        self.__direction: int = To.integer(direction % 4)
        self.__part: Real = To.finite(part)

    @debug("shapepy.scalar.angle")
    def __eq__(self, other: object) -> bool:
        other: Angle = To.angle(other)
        return (
            self.direction == other.direction
            and abs(self.part - other.part) < 1e-6
        )

    def __float__(self):
        return float(self.radians)

    def __invert__(self):
        return Angle(self.direction + 2, self.part)

    def __add__(self, other: Angle) -> Angle:
        other: Angle = To.angle(other)
        return turns(self.turns + other.turns)

    def __sub__(self, other: Angle) -> Angle:
        other: Angle = To.angle(other)
        return turns(self.turns - other.turns)

    def __mul__(self, other: Real) -> Angle:
        return turns(other * self.turns)

    def __rmul__(self, other: Real) -> Angle:
        return self.__mul__(other)

    def __str__(self):
        return f"{self.degrees} deg"

    def __repr__(self):
        return f"Angle({self.direction}, {self.part})"

    @property
    def direction(self) -> int:
        """Gives the nearest axis to the angle

        Example
        -------
        >>> degrees(0).direction  # +x axis
        0
        >>> degrees(30).direction  # +x axis
        0
        >>> degrees(60).direction  # +y axis
        1
        >>> degrees(90).direction  # +y axis
        1
        >>> degrees(120).direction  # +y axis
        1
        >>> degrees(180).direction  # -x axis
        2
        >>> degrees(270).direction  # -y axis
        3
        """
        return self.__direction

    @property
    def part(self) -> int:
        """Gives the distance between the angle and the nearest axis

        Example
        -------
        >>> degrees(0).part
        0
        >>> degrees(30).part
        0.08333333333333333
        >>> degrees(45).part
        0.125
        >>> degrees(60)
        -0.08333333333333333
        >>> degrees(90).part
        0
        >>> degrees(120).part
        0.08333333333333333
        """
        return self.__part

    @property
    def radians(self) -> Real:
        """Gives the angle measure in radians

        Example
        -------
        >>> degrees(0).radians
        0
        >>> degrees(45).radians
        0.7853981633974483
        >>> degrees(90).radians
        1.5707963267948966
        >>> degrees(180).radians
        3.141592653589793
        >>> degrees(270).radians
        4.71238898038469
        >>> degrees(360).radians
        0
        """
        return Math.tau * self.turns

    @property
    def degrees(self) -> Real:
        """Gives the angle measure in degrees

        Example
        -------
        >>> degrees(0).degrees
        0
        >>> degrees(45).degrees
        45
        >>> degrees(90).degrees
        90
        >>> degrees(180).degrees
        180
        >>> degrees(270).degrees
        270
        >>> degrees(360).degrees
        0
        """
        return 360 * self.turns

    @property
    def turns(self) -> Real:
        """Gives the angle measure in turns

        Example
        -------
        >>> degrees(0).turns
        0
        >>> degrees(45).turns
        0.125
        >>> degrees(90).turns
        0.25
        >>> degrees(180).turns
        0.5
        >>> degrees(270).turns
        0.75
        >>> degrees(360).turns
        0
        """
        if self.direction == 0 and self.part < 0:
            return To.rational(1) + self.part
        return self.part + To.rational(self.direction, 4)

    def sin(self) -> Real:
        """
        Computes the sinus value for the angle

        Return
        ------
        Real
            The sinus result of the angle

        Example
        -------
        >>> degrees(0).sin()
        0
        >>> degrees(45).sin()
        0.7071067811865476
        >>> degrees(90).sin()
        1
        """
        if self.part == 0:
            result = (
                1 if self.direction == 1 else -1 if self.direction == 3 else 0
            )
            return To.finite(result)

        if self.direction % 2:
            result = Math.turcos(self.part)
        else:
            result = Math.tursin(self.part)
        if self.direction > 1:
            result *= -1
        return result

    def cos(self) -> Real:
        """
        Computes the cossinus value for the angle

        Return
        ------
        Real
            The cossinus result of the angle

        Example
        -------
        >>> degrees(0).cos()
        1
        >>> degrees(45).cos()
        0.7071067811865476
        >>> degrees(90).cos()
        0
        """
        if self.part == 0:
            result = (
                1 if self.direction == 0 else -1 if self.direction == 2 else 0
            )
            return To.finite(result)

        if self.direction % 2:
            result = Math.tursin(self.part)
        else:
            result = Math.turcos(self.part)
        if 0 < self.direction < 3:
            result *= -1
        return result


def to_angle(obj: object) -> Angle:
    """
    Converts an object to an Angle instance

    * If it's already an angle, gives the same instance
    * If it's a string, decides depending on the content:
        * "10deg" -> degrees(10)
        * "0.25tur" -> turns(0.25)
        * "2.1rad" -> radians(2.1)
    * If it's any another type, converts to a number, and gives it in radians

    Example
    -------
    >>> angle("10deg")
    >>> angle("0.25tur")
    >>> angle("2.1rad")
    >>> angle(1.25)
    """
    if Is.instance(obj, Angle):
        return obj
    if Is.instance(obj, str):
        tipo = re.findall(r"([a-zA-Z]+)$", obj)[0]
        value = To.finite(obj.replace(tipo, ""))
        if "deg" in tipo:
            return degrees(value)
        if "tur" in tipo:
            return turns(value)
        return radians(value)
    return radians(obj)
