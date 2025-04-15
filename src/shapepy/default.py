"""
This file contains the default functions and constant mathematical values
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

from .logger import debug


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
    >>> real(-1)
    -1
    >>> real(0)
    0
    >>> real(1)
    1
    >>> real(1.5)
    1.5
    >>> real(float("inf"))
    inf
    >>> real("inf")
    inf
    """
    if isinstance(number, Real):
        return number
    return float(number)


@debug("shapepy.default", 0)
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
    >>> finite(-1)
    -1
    >>> finite(0)
    0
    >>> finite(1)
    1
    >>> finite(1.5)
    1.5
    """
    number = real(number)
    if not isfinite(number):
        raise ValueError(f"{number} is not finite")
    return number


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
    >>> integer(-1)
    -1
    >>> integer(0)
    0
    >>> integer(1)
    1
    """
    if isinstance(number, Integral):
        return number
    return int(number)


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
    return radsin(tau * angle)


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
    return radcos(tau * angle)


def isreal(value: object) -> bool:
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
    >>> isreal(float("inf"))
    True
    >>> isreal(0)
    True
    >>> isreal("asd")
    False
    """
    return isinstance(value, Real)


def isfinite(number: Real) -> bool:
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
    >>> isfinite(float("inf"))
    False
    >>> isfinite(0)
    True
    """
    return isreal(number) and math.isfinite(number)


def isinfinity(number: Real) -> bool:
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
    >>> isinfinity(-float("inf"))
    True
    >>> isinfinity(float("inf"))
    True
    >>> isinfinity(0)
    False
    """
    return isreal(number) and math.isinf(number)


def isinteger(number: Real) -> bool:
    """
    Check if a number is integer.

    Parameters
    ----------
    number : Real
        The number to check for being an integer

    Returns
    -------
    bool
        True if the number is rational, False otherwise

    Examples
    --------
    >>> is_rational(1)
    True
    >>> is_rational(1.2)
    False
    """
    return isinstance(number, Integral)


def isrational(number: Real) -> bool:
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
    >>> isrational(1)
    True
    >>> isrational(Fraction(1, 2))
    True
    >>> isrational(0.5)
    """
    return isreal(number) and isinstance(number, Rational)


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
    return real(math.fmod(numer, denom))


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
    return real(math.hypot(xcoord, ycoord))


def rational(numerator: Real, denominator: Real) -> Real:
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
    Real
        A Fraction instance if inputs are integers/rational, otherwise a float

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
    >>> rational(1, 2)
    Fraction(1, 2)
    >>> rational(12, 9)
    Fraction(4, 3)
    >>> rational(22, 7)
    Fraction(22, 7)
    """
    numerator = real(numerator)
    denominator = real(denominator)
    if not isrational(numerator) or not isrational(denominator):
        return numerator / denominator
    return Fraction(numerator, denominator)


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
    return finite(math.atan2(ycoord, xcoord))


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
    >>> radians_to_degrees(0)
    0
    >>> radians_to_degrees(pi / 2)
    90
    >>> radians_to_degrees(pi)
    180

    Notes
    -----
    This function uses the math module's degrees() function internally,
    which handles edge cases and provides optimal numerical precision
    for the conversion.

    Raises:
        TypeError: If the input is not a numeric type
    """
    return finite(math.degrees(angle))
