"""
Defines the Angle class

This class is used to handle conversions between radians/degrees/turns
It is an abstraction that to not handle float angle measured in radians
"""

from __future__ import annotations

from numbers import Integral, Real

from . import default


class Angle:
    """
    Class that stores an angle.

    Handles the operations such as __add__, __sub__, etc
    """

    @classmethod
    def radians(cls, value: Real) -> Angle:
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
        >>> Angle.radians(0)
        0 deg
        >>> Angle.radians(math.pi/2)
        90 deg
        >>> Angle.radians(math.pi)
        180 deg
        >>> Angle.radians(3*math.pi/2)
        270 deg
        >>> Angle.radians(2*math.pi)
        0 deg
        """
        value = default.finite(default.fmod(value, default.tau))
        return cls.degrees(default.degrees(value))

    @classmethod
    def degrees(cls, value: Real) -> Angle:
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
        >>> Angle.degrees(0)
        0 deg
        >>> Angle.degrees(90)
        90 deg
        >>> Angle.degrees(180)
        180 deg
        >>> Angle.degrees(270)
        270 deg
        >>> Angle.degrees(360)
        0 deg
        >>> Angle.degrees(720)
        0 deg
        """
        value %= 360
        value = (
            default.rational(value, 360)
            if default.isinteger(value)
            else (value / 360)
        )
        return cls.turns(value)

    @classmethod
    def turns(cls, value: Real) -> Angle:
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
        >>> Angle.turns(0)
        0 deg
        >>> Angle.turns(0.25)
        90 deg
        >>> Angle.turns(0.50)
        180 deg
        >>> Angle.turns(0.75)
        270 deg
        >>> Angle.turns(1)
        0 deg
        >>> Angle.turns(2)
        0 deg
        """
        quad, part = divmod(4 * value, 1)
        return cls(int(quad), part)

    @classmethod
    def atan2(cls, ycoord: Real, xcoord: Real):
        """
        Compute the complex argument of the point (x, y)

        Parameters
        ----------
        ycoord : Real
            The y-coordinate of the point
        xcoord : Real
            The x-coordinate of the point

        Returns
        -------
        Angle
            The Angle instance such tangent gives y/x

        Examples
        --------
        >>> Angle.atan2(0, 1)  # 0 degrees
        0 deg
        >>> Angle.atan2(1, 1)  # 45 degrees
        45 deg
        >>> Angle.atan2(1, -1)  # 135 degrees
        135 deg
        >>> Angle.atan2(-1, 1)  # -45 degrees
        315 deg
        """
        if ycoord == 0:
            return cls(0, 0) if xcoord >= 0 else cls(2, 0)
        if xcoord == 0:
            return cls(1, 0) if ycoord > 0 else cls(3, 0)
        return cls.radians(default.atan2(ycoord, xcoord))

    @classmethod
    def arg(cls, xcoord: Real, ycoord: Real):
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
        >>> Angle.arg(1, 0)  # 0 degrees
        0 deg
        >>> Angle.arg(1, 1)  # 45 degrees
        45 deg
        >>> Angle.arg(0, 1)  # 90 degrees
        90 deg
        >>> Angle.arg(-1, 1)  # 135 degrees
        135 deg
        """
        return cls.atan2(ycoord, xcoord)

    def __init__(self, quad: int = 0, part: Real = 0):
        if not isinstance(quad, Integral):
            raise TypeError(f"Expected integer value, got {type(quad)}")
        if not isinstance(part, Real):
            raise TypeError(f"Expected numeric value, got {type(part)}")
        self.quad: int = quad % 4
        self.part: Real = part

    def __eq__(self, other: object):
        if isinstance(other, Angle):
            return self.quad == other.quad and (self.part - other.part == 0)
        return self == Angle.radians(other)

    def __float__(self):
        return float(default.tau * (self.quad + self.part) / 4)

    def __add__(self, other):
        if not isinstance(other, Angle):
            raise TypeError(f"Cannot add {type(self)} with {type(other)}")
        return self.__class__.turns(
            ((self.quad + other.quad) + (self.part + other.part)) / 4
        )

    def __sub__(self, other):
        if not isinstance(other, Angle):
            raise TypeError(f"Cannot sub {type(self)} with {type(other)}")
        return self.__class__.turns(
            ((self.quad - other.quad) + (self.part - other.part)) / 4
        )

    def __mul__(self, other: Real) -> Angle:
        return self.turns(other * (self.quad + self.part) / 4)

    def __rmul__(self, other: Real) -> Angle:
        return self.__mul__(other)

    def __str__(self):
        return f"{90 * (self.quad + self.part)} deg"

    def __repr__(self):
        return f"Angle({str(self)})"

    def sin(self) -> Real:
        """
        Computes the sinus value for the angle

        Return
        ------
        Real
            The sinus result of the angle

        Example
        -------
        >>> Angle.degrees(0).sin()
        0
        >>> Angle.degrees(45).sin()
        0.7071067811865476
        >>> Angle.degrees(90).sin()
        1
        """
        if self.part == 0:
            if self.quad % 2:
                return default.finite(1 if self.quad == 1 else -1)
            return default.finite(0)

        if self.quad % 2:
            result = default.turcos(self.part / 4)
        else:
            result = default.tursin(self.part / 4)
        if self.quad > 1:
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
        >>> Angle.degrees(0).cos()
        1
        >>> Angle.degrees(45).cos()
        0.7071067811865476
        >>> Angle.degrees(90).cos()
        0
        """
        if self.part == 0:
            if self.quad % 2:
                return default.finite(0)
            return default.finite(1 if self.quad == 0 else -1)

        if self.quad % 2:
            result = default.tursin(self.part / 4)
        else:
            result = default.turcos(self.part / 4)
        if 0 < self.quad < 3:
            result *= -1
        return result
