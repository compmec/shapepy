import math
from functools import lru_cache
from typing import Iterable


@lru_cache
def factorial(n: int) -> int:
    return math.factorial(int(n))


@lru_cache
def binom(n: int, i: int) -> int:
    return math.comb(n, i)


@lru_cache
def keys_pow(exp):
    if exp == 1:
        return set()
    return keys_pow(exp // 2) | keys_pow(exp - exp // 2) | {exp}


def gcd(*numbers: int) -> int:
    """
    Greates common division
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
    """
    if number == 2:
        return (2,)
    if number == 3:
        return (2, 3)
    primes = [2, 3, 5, 7]
    for nb in range(primes[-1] + 2, math.floor(number) + 1, 2):
        for pr in primes:
            if not (nb % pr):
                break
        else:
            primes.append(nb)
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
        while not (number % prime):
            factors.append(prime)
            number //= prime
    return tuple(factors)


def divisors(number: int) -> Iterable[int]:
    factors = factorate(number)
    divs = {1} | set(factors)
    if len(factors) > 1:
        for factor in factors:
            divs.add(factor)
            divs.add(number // factor)
            divs |= set(divisors(number // factor))
    return tuple(sorted(divs))
