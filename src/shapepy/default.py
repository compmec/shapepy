from __future__ import annotations

import math
from fractions import Fraction
from numbers import Integral, Rational, Real
from typing import Any, Callable


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
    if isinstance(node, Real):
        return node
    return float(node)


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
    node = real(node)
    if not isfinite(node):
        raise ValueError(f"{node} is not finite")
    return node


def integer(node: number) -> Integral:
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
    if isinstance(node, Integral):
        return node
    return int(node)


tau: Real = math.tau
radsin: Callable[[Real], Real] = math.sin
radcos: Callable[[Real], Real] = math.cos

sinh: Callable[[Real], Real] = math.sinh
cosh: Callable[[Real], Real] = math.cosh

neginf = -math.inf
posinf = math.inf

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
    return radsin(tau * node)


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
    return radcos(tau * node)


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


def isfinite(node: Real) -> bool:
    """
    Check if a number is finite.

    Parameters
    ----------
    node : Real
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
    return isreal(node) and math.isfinite(node)


def isinfinity(node: Real) -> bool:
    """
    Check if a number is negative or positive infinity.

    Parameters
    ----------
    node : Real
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
    return isreal(node) and math.isinf(node)


def isinteger(node: Real) -> bool:
    """
    Check if a number is integer.

    Parameters
    ----------
    node : Real
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
    return isinstance(node, Integral)


def isrational(node: Real) -> bool:
    """
    Check if a number is integer or rational.

    Parameters
    ----------
    node : Real
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
    return isreal(node) and isinstance(node, Rational)


def fmod(xcoord: Real, ycoord: Real) -> Real:
    """
    Returns the floating-point remainder of division x1/x2.

    Parameters
    ----------
    xcoord : float
        Dividend
    ycoord : float
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
    return real(math.fmod(x, y))


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
    return real(math.hypot(*coords))


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
    return finite(math.atan2(y, x))


def degrees(value: Real) -> Real:
    """
    Convert an angle from radians to degrees.

    This function performs the angular conversion using the mathematical
    relationship that pi radians equals 180 degrees.
    The conversion factor is calculated as 180/pi, ensuring precise
    transformation between the two angular measurement systems.

    Parameters
    ----------
    radians : float
        The angle in radians to convert

    Returns
    -------
    float
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
    return finite(math.degrees(value))
