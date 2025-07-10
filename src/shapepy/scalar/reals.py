"""
This file contains the default math functions and constant mathematical values
that are used as base for the entire package.

All the mathematical functions that are not implemented, like `sin` and `cos`
are the same from the standard `math` python's package.
The standard rational number is a instance from `fractions` standard package.

Other libraries offer other options to handle numerical numbers.
To do such, you need to overwrite these base functions and hence the
package will use your numerical type.
Example of use are:
* `numpy` offers `numpy.float64` instead of float
* `mpmath` offers the `mpmath.mpf` of arbitrary precision of float
* `sympy` offers `sympy.core.numbers.Rational` instead of `fractions.Fraction`
"""

from __future__ import annotations

import math
from fractions import Fraction
from numbers import Integral, Rational, Real
from typing import Any, Callable


class Is:
    """
    Contains functions to test the objects,
    telling if an object is a number, or it's integer, etc
    """

    instance = isinstance

    @staticmethod
    def finite(number: Real) -> bool:
        """
        Check if a number is finite.

        Parameters
        ----------
        number : Real
            The number to check for being finite

        Returns
        -------
        bool
            True if the number is finite, False otherwise

        Examples
        --------
        >>> Is.finite(float("inf"))
        False
        >>> Is.finite(0)
        True
        """
        return Is.real(number) and math.isfinite(number)

    @staticmethod
    def infinity(number: Real) -> bool:
        """
        Check if a number is negative or positive infinity.

        Parameters
        ----------
        number : Real
            The number to check for being infinity

        Returns
        -------
        bool
            True if the number is infinity, False otherwise

        Examples
        --------
        >>> Is.infinity(-float("inf"))
        True
        >>> Is.infinity(float("inf"))
        True
        >>> Is.infinity(0)
        False
        """
        return Is.real(number) and math.isinf(number)

    @staticmethod
    def integer(number: Real) -> bool:
        """
        Check if a number is integer.

        Parameters
        ----------
        number : Real
            The number to check for being an integer

        Returns
        -------
        bool
            True if the number is integer, False otherwise

        Examples
        --------
        >>> Is.integer(1)
        True
        >>> Is.integer(1.2)
        False
        """
        return Is.instance(number, Integral)

    @staticmethod
    def rational(number: Real) -> bool:
        """
        Check if a number is integer or rational.

        Parameters
        ----------
        number : Real
            The number to check for rationality

        Returns
        -------
        bool
            True if the number is rational, False otherwise

        Examples
        --------
        >>> Is.rational(1)
        True
        >>> Is.rational(Fraction(1, 2))
        True
        >>> Is.rational(0.5)
        """
        return Is.real(number) and Is.instance(number, Rational)

    @staticmethod
    def real(value: object) -> bool:
        """
        Check if a number is a real number.

        Parameters
        ----------
        value : object
            The object to check for being a number

        Returns
        -------
        bool
            True if the number is a number, False otherwise

        Examples
        --------
        >>> Is.real(float("inf"))
        True
        >>> Is.real(0)
        True
        >>> Is.real("asd")
        False
        """
        return Is.instance(value, Real)


class To:
    """
    Contains static methods to transform objects to some type numbers
    """

    @staticmethod
    def real(number: Any) -> Real:
        """
        Converts the number to a real number.

        Parameters
        ----------
        number : Any
            Number to be converted to a real number

        Returns
        -------
        Real
            The converted real number

        Examples
        --------
        >>> To.real(-1)
        -1
        >>> To.real(0)
        0
        >>> To.real(1)
        1
        >>> To.real(1.5)
        1.5
        >>> To.real(float("inf"))
        inf
        >>> To.real("inf")
        inf
        """
        if Is.instance(number, Real):
            return number
        return float(number)

    @staticmethod
    def finite(number: Any) -> Real:
        """
        Converts the number to an finite number.

        Parameters
        ----------
        number : Any
            Number to be converted to an integer

        Returns
        -------
        Real
            The converted number in integer

        Raises
        ------
        ValueError
            If the number is not finite

        Examples
        --------
        >>> To.finite(-1)
        -1
        >>> To.finite(0)
        0
        >>> To.finite(1)
        1
        >>> To.finite(1.5)
        1.5
        """
        number = To.real(number)
        if not Is.finite(number):
            raise ValueError(f"{number} is not finite")
        return number

    @staticmethod
    def rational(numerator: Rational, denominator: Rational) -> Rational:
        """
        Divide two rational numbers and return the result as a fraction.
        If any input is not integer/rational, performs standard division.

        Parameters
        ----------
        numerator : int or rational or float
            The numerator number
        denominator : int or rational or float
            The divisor number

        Returns
        -------
        Rational
            A  instance if inputs are integers/rational

        Raises
        ------
        ZeroDivisionError
            If denominator is zero
        TypeError
            If inputs are not numeric types

        Notes
        -----
        This function preserves exact rational representation when inputs are
        integers or rational numbers. For example:


        Examples
        --------
        >>> To.rational(1, 2)
        Fraction(1, 2)
        >>> To.rational(12, 9)
        Fraction(4, 3)
        >>> To.rational(22, 7)
        Fraction(22, 7)
        """
        numerator = To.real(numerator)
        denominator = To.real(denominator)
        return Fraction(numerator, denominator)

    @staticmethod
    def integer(number: Any) -> Integral:
        """
        Converts the number to an integer.

        Parameters
        ----------
        number : Real
            Number to be converted to an integer

        Returns
        -------
        int
            The converted number in integer

        Examples
        --------
        >>> To.integer(-1)
        -1
        >>> To.integer(0)
        0
        >>> To.integer(1)
        1
        """
        if Is.instance(number, Integral):
            return number
        return int(number)


class Math:
    """
    Contains static methods for mathematical functions
    """

    tau: Real = math.tau
    radsin: Callable[[Real], Real] = math.sin
    radcos: Callable[[Real], Real] = math.cos

    sinh: Callable[[Real], Real] = math.sinh
    cosh: Callable[[Real], Real] = math.cosh

    NEGINF = -math.inf
    POSINF = math.inf

    binom: Callable[[int, int], int] = math.comb
    factorial: Callable[[int], int] = math.factorial
    sqrt: Callable[[Real], Real] = math.sqrt

    @staticmethod
    def tursin(angle: Real):
        """
        Compute the sine of an angle in unitary form (turns).

        This function is equivalent to `math.sin(2*math.pi*angle)`

        Reference:
        * https://en.wikipedia.org/wiki/Turn_(angle)

        Parameters
        ----------
        angle : Real
            Angle in turns measure

        Returns
        -------
        float
            Sine of the unitary angle

        Examples
        --------
        >>> tursin(0)  # sine of 0 degrees
        0
        >>> tursin(0.25)  # sine of 90 degrees
        1
        >>> tursin(0.5)  # sine of 180 degrees
        0
        >>> tursin(0.75)  # sine of 270 degrees
        -1
        >>> tursin(1)  # sine of 360 degrees
        0
        """
        return Math.radsin(Math.tau * angle)

    @staticmethod
    def turcos(angle: Real):
        """
        Compute the cossinus of an angle in unitary form (turns).

        This function is equivalent to `math.cos(2*math.pi*angle)`

        Reference:
        * https://en.wikipedia.org/wiki/Turn_(angle)

        Parameters
        ----------
        angle : Real
            Angle in turns measure

        Returns
        -------
        float
            Cossinus of the unitary angle

        Examples
        --------
        >>> turcos(0)  # cossinus of 0 degrees
        1
        >>> turcos(0.25)  # cossinus of 90 degrees
        0
        >>> turcos(0.5)  # cossinus of 180 degrees
        -1
        >>> turcos(0.75)  # cossinus of 270 degrees
        0
        >>> turcos(1)  # cossinus of 360 degrees
        1
        """
        return Math.radcos(Math.tau * angle)

    @staticmethod
    def fmod(numer: Real, denom: Real) -> Real:
        """
        Returns the floating-point remainder of division x1/x2.

        Parameters
        ----------
        numer : float
            Dividend
        denom : float
            Divisor

        Returns
        -------
        float
            The remainder of x divided by y, with the same sign as x.

        Examples
        --------
        >>> fmod(5.0, 2.0)
        1.0
        >>> fmod(-5.0, 2.0)
        -1.0
        >>> fmod(5.0, -2.0)
        1.0
        """
        return To.real(math.fmod(numer, denom))

    @staticmethod
    def hypot(xcoord: Real, ycoord: Real) -> Real:
        """
        Calculate Euclidean distance from origin point (0,0).

        Parameters
        ----------
        xcoord : float
            The x-coordinate of the point
        ycoord : float
            The y-coordinate of the point

        Returns
        -------
        float
            The Euclidean distance from the origin point (0,0)

        Examples
        --------
        >>> calculate_distance_from_origin(3, 4)
        5.0
        >>> calculate_distance_from_origin(0, 0)
        0.0
        """
        return To.real(math.hypot(xcoord, ycoord))

    @staticmethod
    def atan2(ycoord: Real, xcoord: Real) -> Real:
        """
        Compute the arc tangent of y/x choosing the quadrant correctly.

        Parameters
        ----------
        ycoord : Real
            The y-coordinate of the point
        xcoord : Real
            The x-coordinate of the point

        Returns
        -------
        float
            Array of angles in radians in the range [-pi, pi)

        Examples
        --------
        >>> arctan2(1, 1)  # 45 degrees = π/4 radians
        0.7853981633974483
        >>> arctan2(-1, 1)  # -45 degrees = -π/4 radians
        -0.7853981633974483
        >>> arctan2(1, -1)  # 135 degrees = 3π/4 radians
        2.3561944901923448
        """
        return To.finite(math.atan2(ycoord, xcoord))

    @staticmethod
    def degrees(angle: Real) -> Real:
        """
        Convert an angle from radians to degrees.

        This function performs the angular conversion using the mathematical
        relationship that pi radians equals 180 degrees.
        The conversion factor is calculated as 180/pi, ensuring precise
        transformation between the two angular measurement systems.

        Parameters
        ----------
        angle : Real
            The angle in radians to convert

        Returns
        -------
        Real
            The equivalent angle in degrees

        Examples
        --------
        >>> degrees(0)
        0
        >>> degrees(pi / 2)
        90
        >>> degrees(pi)
        180

        Notes
        -----
        This function uses the math module's degrees() function internally,
        which handles edge cases and provides optimal numerical precision
        for the conversion.

        Raises:
            TypeError: If the input is not a numeric type
        """
        return To.finite(math.degrees(angle))
