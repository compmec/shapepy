"""
This file contains some useful functions used to compute analytic functions
"""

import math
from functools import lru_cache
from typing import Iterable, Tuple

from ..core import Math, Scalar


@lru_cache
def factorial(number: int) -> int:
    """
    Computes the factorial of a function:

    * factorial(0) = 1
    * factorial(n) = n * factorial(n-1)

    Example
    -------
    >>> factorial(0)
    1
    >>> factorial(1)
    1
    >>> factorial(2)
    2
    >>> factorial(3)
    6
    >>> factorial(5)
    120
    """
    return math.factorial(int(number))


@lru_cache
def binom(numer: int, denom: int) -> int:
    """
    Computes the binomial function

    binom(n, i) = n! / (i! * (n-i)!)

    Example
    -------
    >>> binom(1, 0)
    1
    >>> binom(4, 2)
    6
    """
    return math.comb(numer, denom)


def gcd(*numbers: int) -> int:
    """
    Computes the greatest common division

    Example
    -------
    >>> gcd(1, 2)
    1
    >>> gcd(16, 24)
    8
    """
    if len(numbers) == 1:
        return abs(numbers[0])
    numbers = tuple(map(abs, numbers))
    nnbs = len(numbers)
    if nnbs > 2:
        middle = nnbs // 2
        numbers = gcd(*numbers[:middle]), gcd(*numbers[middle:])
    return math.gcd(numbers[0], numbers[1])


def lcm(*numbers: int) -> int:
    """
    Computes the least common multiple

    Example
    -------
    >>> lc,(1, 2)
    2
    >>> lcm(16, 24)
    48
    """
    if len(numbers) == 1:
        return abs(numbers[0])
    numbers = tuple(map(abs, numbers))
    nnbs = len(numbers)
    if nnbs > 2:
        middle = nnbs // 2
        numbers = lcm(*numbers[:middle]), lcm(*numbers[middle:])
    return (numbers[0] * numbers[1]) // gcd(*numbers)


def find_primes(number: int) -> int:
    """
    Find all primes that are bellow or equal number

    Example
    -------
    >>> find_primes(2)
    (2, )
    >>> find_primes(3)
    (2, 3)
    >>> find_primes(12)
    (2, 3, 5, 7, 11)
    """
    if number == 2:
        return (2,)
    if number == 3:
        return (2, 3)
    primes = [2, 3, 5, 7]
    for numb in range(primes[-1] + 2, math.floor(number) + 1, 2):
        for prime in primes:
            if not numb % prime:
                break
        else:
            primes.append(numb)
    return tuple(pr for pr in primes if pr <= number)


def factorate(number: int) -> Iterable[int]:
    """
    Factorate a number in the primes

    Example
    --------
    >>> factorate(2)
    (2, )
    >>> factorate(6)
    (2, 3)
    >>> factorate(24)
    (2, 2, 2, 3)
    """
    number = int(abs(number))
    factors = []
    for prime in find_primes(number):
        while not number % prime:
            factors.append(prime)
            number //= prime
    return tuple(factors)


def divisors(number: int) -> Iterable[int]:
    """
    Computes all divisors of given number

    Example
    --------
    >>> divisors(2)
    (1, 2)
    >>> divisors(6)
    (1, 2, 3, 6)
    >>> factorate(24)
    (1, 2, 3, 4, 6, 8, 12, 24)
    """
    factors = factorate(number)
    divs = {1} | set(factors)
    if len(factors) > 1:
        for factor in factors:
            divs.add(factor)
            divs.add(number // factor)
            divs |= set(divisors(number // factor))
    return tuple(sorted(divs))


def rsin(rad_angle: Scalar) -> Scalar:
    """
    Computes the sinus of given angle.
    The angule mesure is in radians
    """
    return Math.sin(rad_angle)


def rcos(rad_angle: Scalar) -> Scalar:
    """
    Computes the cossinus of given angle.
    The angule mesure is in radians
    """
    return Math.cos(rad_angle)


def usin(uangle: Scalar) -> Scalar:
    """
    Computes the sinus of given angle.
    The angle mesure is unitary, meaning

        sin(x) = sin(1+x) for all x

    Parameters
    ----------
    uangle: Scalar
        Given angle to compute sinus

    Example
    -------
    >>> Trignomial.sin(0)
    0
    >>> Trignomial.sin(0.25)
    1
    >>> Trignomial.sin(0.5)
    0
    >>> Trignomial.sin(0.75)
    -1
    >>> Trignomial.sin(1)
    0
    >>> Trignomial.sin(0.125)
    0.7071067811865
    """
    uangle %= 1
    quad, subangle = divmod(4 * uangle, 1)
    if not subangle:
        if not quad % 2:
            return 0
        return 1 - 2 * (quad == 3)
    return rsin(uangle * Math.tau)


def ucos(uangle: Scalar) -> Scalar:
    """
    Computes the cossinus of given angle.
    The angle mesure is unitary, meaning

        cos(x) = cos(1+x) for all x

    Parameters
    ----------
    uangle: Scalar
        Given angle to compute cossinus

    Example
    -------
    >>> Trignomial.cos(0)
    1
    >>> Trignomial.cos(0.25)
    0
    >>> Trignomial.cos(0.5)
    -1
    >>> Trignomial.cos(0.75)
    0
    >>> Trignomial.cos(1)
    1
    >>> Trignomial.cos(0.125)
    0.7071067811865
    """
    uangle %= 1
    quad, subangle = divmod(4 * uangle, 1)
    if not subangle:
        if quad % 2:
            return 0
        return 1 - 2 * (quad == 2)
    return rcos(uangle * Math.tau)


def usincos(uangle: Scalar) -> Tuple[Scalar, Scalar]:
    """
    Computes the sinus and cossinus of given angle at same time.
    The angle mesure is unitary, meaning

        sin(x) = cos(1+x) for all x
        cos(x) = cos(1+x) for all x

    Parameters
    ----------
    uangle: Scalar
        Given angle to compute sin and cos

    Example
    -------
    >>> Trignomial.sincos(0)
    (1, 0)
    >>> Trignomial.sincos(0.25)
    (0, 1)
    >>> Trignomial.sincos(0.5)
    (-1, 0)
    >>> Trignomial.sincos(0.75)
    (0, -1)
    >>> Trignomial.sincos(1)
    (1, 0)
    >>> Trignomial.sincos(0.125)
    (0.7071067811865, 0.7071067811865)
    """
    uangle %= 1
    return usin(uangle), ucos(uangle)


def uarctan2(yval: Scalar, xval: Scalar) -> Scalar:
    """
    Computes the unitary angle such tangent gives yval/xval.

    The given result is in the interval [-0.5, 0.5)

    Examples
    --------
    >>> uarctan2(yval=0, xval=-1)
    -0.5
    >>> uarctan2(yval=-1, xval=-1)
    -0.375
    >>> uarctan2(yval=-1, xval=0)
    -0.25
    >>> uarctan2(yval=-1, xval=1)
    -0.125
    >>> uarctan2(yval=0, xval=1)
    0
    >>> uarctan2(yval=1, xval=1)
    0.125
    >>> uarctan2(yval=1, xval=0)
    0.25
    >>> uarctan2(yval=1, xval=-1)
    0.375
    """
    if not yval:
        return 0 if xval > 0 else -0.5
    if not xval:
        return 0.25 if yval > 0 else -0.25
    return Math.arctan2(float(yval), float(xval)) / Math.tau


def unit_angle(xval: Scalar, yval: Scalar) -> Scalar:
    """
    Given a point, it computes the 'unitary angle' used in winding
    In fact this function is wrong, but it works when
    computing the winding number
    """
    if yval == 0:
        return 0 if xval >= 0 else -1
    if xval == 0:
        return 0.25 if yval > 0 else 0.75
    return uarctan2(yval, xval)
