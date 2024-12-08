"""
This file contains a class Trignomial that allows evaluating and
making operations with trignomios, like adding, multiplying, etc

A trignomio is similar to a polynomial, but uses trignometic functions

Example
-------
>>> trig = Trignomial([1, 2, 3])
>>> print(trig)
1 + 2 * sin(tau*x) + 3 * cos(tau*x)
>>> trig = Trignomial([1, 2, 3, 4])
>>> print(trig)
1 + 2 * sin(tau*x) + 3 * cos(tau*x) + 4 * sin(2*tau*x)
"""

from __future__ import annotations

import math
from fractions import Fraction
from functools import lru_cache
from typing import Iterable, Optional, Tuple, Union

from ..core import IAnalytic

Parameter = Union[int, float]
Scalar = Union[int, float]


@lru_cache
def keys(exp):
    if exp == 1:
        return set()
    return keys(exp // 2) | keys(exp - exp // 2) | {exp}


class Trignomial(IAnalytic):
    """
    Defines a trignometric version of a polynomial

    Meaning, if a polynomial can be defined as
    P(x) = a0 + a1 * x + a2 * x^2 + ... + ap * x^p

    We can define a trignometric version:
    T(x) = a0 + a1 * sin(w*x) + a2 * cos(w*x) + ...
           + a_{2p-1} * sin(p*w*x) + a_{2p} * cos(p*w*x)

    Example
    -------
    >>> trig = Trignomial([1, 0, 1])
    >>> print(trig)
    1 + cos(x)
    >>> trig.eval(0)
    2.0
    >>> trig.eval(np.pi/2)
    1.0
    >>> trig = Trignomial([1, 2, 0, -3])
    >>> print(trig)
    1 + 2 * sin(x) - 3*sin(2*x)

    """

    TAU = math.tau
    SIN = math.sin
    COS = math.cos

    @staticmethod
    def sin(unit_angle: Scalar) -> Scalar:
        unit_angle %= 1
        quad, subangle = divmod(4 * unit_angle, 1)
        if not subangle:
            if not (quad % 2):
                return 0
            return 1 - 2 * (quad == 3)
        return Trignomial.SIN(unit_angle * Trignomial.TAU)

    @staticmethod
    def cos(unit_angle: Scalar) -> Scalar:
        unit_angle %= 1
        quad, subangle = divmod(4 * unit_angle, 1)
        if not subangle:
            if quad % 2:
                return 0
            return 1 - 2 * (quad == 2)
        return Trignomial.COS(unit_angle * Trignomial.TAU)

    @staticmethod
    def sincos(unit_angle: Scalar) -> Tuple[Scalar, Scalar]:
        unit_angle %= 1
        return Trignomial.sin(unit_angle), Trignomial.cos(unit_angle)

    def __init__(self, values: Iterable[Scalar], frequency: Scalar = 1):
        values = tuple(values)
        if not values:
            raise ValueError("Cannot pass empty tuple")
        degree = max((i for i, ci in enumerate(values) if ci), default=0)
        values = list(values[: degree + 1])
        if not len(values) % 2:
            values.append(0 * sum(values))
        for i, value in enumerate(values):
            if isinstance(value, int):
                values[i] = Fraction(value)
        self.__values = values
        self.__freq = frequency

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IAnalytic):
            return self.pmax == 0 and self[0] == other
        if not isinstance(other, Trignomial):
            return False
        if self.pmax != other.pmax or self.frequency != other.frequency:
            return False
        atol = 1e-9
        return all(abs(ci - cj) < atol for ci, cj in zip(self, other))

    @property
    def pmax(self) -> int:
        """
        Returns the maximum harmonic value of the trignomio

        Example
        -------
        >>> trig = Trignomial([1, 0, 1])  # 1 + cos(x)
        >>> trig.pmax
        1
        >>> trig = Trignomial([1, 0, 1, 2])  # 1 + cos(x) + sin(2*x)
        >>> trig.pmax
        2
        """
        return len(self.__values) // 2

    @property
    def frequency(self) -> Scalar:
        """
        Returns the frequency of the trignomio

        Example
        -------
        >>> trig = Trignomial([1, 0, 1])  # 1 + cos(tau*x)
        >>> trig.frequency
        1
        >>> trig = Trignomial([1, 0, 1], 3)  # 1 + cos(3*tau*x)
        >>> trig.frequency
        3
        """
        return self.__freq

    @property
    def omega(self) -> Scalar:
        """
        Returns the harmonic of the trignomio

        Example
        -------
        >>> trig = Trignomial([1, 0, 1])  # 1 + cos(tau*x)
        >>> trig.omega
        3.14159265
        >>> trig = Trignomial([1, 0, 1], 3)  # 1 + cos(3*tau*x)
        >>> trig.omega
        9.42477796
        """
        return self.TAU * self.frequency

    def __iter__(self):
        yield from self.__values

    def __getitem__(self, index):
        return self.__values[index]

    def __setitem__(self, key, newvalue):
        self.__values[key] = newvalue

    def __neg__(self) -> Trignomial:
        return self.__class__(tuple(-coef for coef in self), self.frequency)

    def __add__(self, other: Union[Scalar, Trignomial]):
        if not isinstance(other, Trignomial):
            coefs = list(self)
            coefs[0] += other
            return self.__class__(coefs, self.frequency)
        if self.frequency != other.frequency:
            raise NotImplementedError
        values = [0] * (1 + 2 * max(self.pmax, other.pmax))
        for i, val in enumerate(self):
            values[i] += val
        for i, val in enumerate(other):
            values[i] += val
        return self.__class__(values, self.frequency)

    def __sub__(self, other: Union[Scalar, Trignomial]) -> Trignomial:
        return self.__add__(-other)

    def __mul__(self, other: Union[Scalar, Trignomial]) -> Trignomial:
        if not isinstance(other, Trignomial):
            coefs = tuple(other * coef for coef in self)
            return self.__class__(coefs, self.frequency)
        if self.frequency != other.frequency:
            raise NotImplementedError
        values = [0] * (1 + 2 * (self.pmax + other.pmax))
        for i, vali in enumerate(self):
            p = (i + 1) // 2
            for j, valj in enumerate(other):
                q = (j + 1) // 2
                s, d = p + q, abs(p - q)
                temp = (vali * valj) / 2
                if (i % 2) ^ (j % 2):
                    if p != q:
                        sind = -1 if (i > j) ^ (i % 2) else 1
                        values[2 * d - 1] += temp * sind
                    values[2 * s - 1] += temp
                else:
                    coss = -1 if i % 2 else 1
                    values[2 * d] += temp
                    values[2 * s] += temp * coss
        return self.__class__(values, self.frequency)

    def __divmod__(
        self, other: Union[Scalar, Trignomial]
    ) -> Tuple[Trignomial, Trignomial]:
        if isinstance(other, Trignomial) and not other.pmax:
            return self.__divmod__(other[0])
        if not isinstance(other, Trignomial):
            if not other:
                raise ZeroDivisionError("division by zero")
            quot = self.__class__((ci / other for ci in self), self.frequency)
            rest = Trignomial([0 * sum(self)])
            return quot, rest
        if self.frequency != other.frequency:
            raise NotImplementedError
        if self.pmax < other.pmax:
            return Trignomial([0 * sum(self)]), self
        square = other[-1] ** 2 + other[-2] ** 2
        othecs = other[-1] / square, other[-2] / square
        if self.pmax == other.pmax:
            const = self[-1] * othecs[0] + self[-2] * othecs[1]
            quot = Trignomial([const], self.frequency)
            return quot, self - quot * other

        quot = Trignomial([0 * sum(self)])
        rest = self
        while rest.pmax > other.pmax:
            cos = othecs[0] * rest[-1] + othecs[1] * rest[-2]
            sin = othecs[0] * rest[-2] - othecs[1] * rest[-1]
            coefs = [0] * (2 * (rest.pmax - other.pmax) - 1)
            coefs += [2 * sin, 2 * cos]
            quot += Trignomial(coefs)
            rest = self - other * quot
        newquot, newrest = divmod(rest, other)
        quot += newquot
        rest = newrest
        return quot, rest

    def __floordiv__(self, other: Union[Scalar, Trignomial]) -> Trignomial:
        return self.__divmod__(other)[0]

    def __mod__(self, other: Union[Scalar, Trignomial]) -> Trignomial:
        return self.__divmod__(other)[1]

    def __truediv__(self, other: Scalar) -> Trignomial:
        div, res = self.__divmod__(other)
        if res != 0:
            raise ValueError(f"Cannot divide {self} by {other}")
        return div

    def __rsub__(self, other: Scalar) -> Trignomial:
        return (-self).__add__(other)

    def __rmul__(self, other: Scalar) -> Trignomial:
        return self.__mul__(other)

    def __radd__(self, other: Scalar) -> Trignomial:
        return self.__add__(other)

    def __pow__(self, exponent: int) -> Trignomial:
        exponent = int(exponent)
        if exponent < 0:
            raise ValueError
        if exponent == 0:
            return self.__class__([1 + 0 * sum(self)])
        needs = sorted(keys(exponent))
        cache = {1: self}
        for n in needs:
            cache[n] = cache[n // 2] * cache[n - n // 2]
        return cache[exponent]

    def eval(self, node: Parameter, derivate: int = 0):
        """
        Evaluates the trignomio at given node

        Example
        -------
        >>> trig = Trignomial([1, 2])
        >>> print(trig)
        1 + 2*sin(tau*x)
        >>> trig.eval(0)
        1
        >>> trig.eval(1/4)
        3.0
        >>> trig.eval(0, 0)
        1
        >>> trig.eval(1/4, 2)
        -78.956835  # 2*tau^2
        """
        if derivate != 0:
            return self.derivate(derivate).eval(node, 0)
        results = self[0]
        for pi in range(self.pmax):
            sin, cos = Trignomial.sincos(node)
            results += self[2 * pi + 1] * sin + self[2 * pi + 2] * cos
        return results

    def derivate(self, times: int = 1) -> Trignomial:
        times = int(times)
        if times < 0:
            raise ValueError
        if times == 0:
            return self.__class__(tuple(self), self.frequency)
        const = self.omega**times
        coefs = list(self)
        coefs[0] *= 0
        for i in range(self.pmax):
            term = (i + 1) ** times
            coefs[2 * i + 1] *= const * term
            coefs[2 * i + 2] *= const * term
        times %= 4
        if times // 2:
            coefs = [-coef for coef in coefs]
        if times % 2:
            for i in range(self.pmax):
                sin, cos = coefs[2 * i + 1], coefs[2 * i + 2]
                coefs[2 * i + 1] = -cos
                coefs[2 * i + 2] = sin
        return self.__class__(coefs, self.frequency)

    def integrate(self, times: int) -> Trignomial:
        times = int(times)
        if times < 0:
            raise ValueError
        if times == 0:
            return self.__class__(tuple(self), self.frequency)
        if self[0]:
            raise ValueError("Cannot integrate the function with constant")
        const = self.omega**times
        coefs = list(self)
        for i in range(self.pmax):
            term = (i + 1) ** times
            coefs[2 * i + 1] /= const * term
            coefs[2 * i + 2] /= const * term
        times %= 4
        if times // 2:
            coefs = [-coef for coef in coefs]
        if times % 2:
            for i in range(self.pmax):
                sin, cos = coefs[2 * i + 1], coefs[2 * i + 2]
                coefs[2 * i + 1] = cos
                coefs[2 * i + 2] = -sin
        return self.__class__(coefs, self.frequency)

    def defintegral(self, lower: Parameter, upper: Parameter) -> Scalar:
        const = self[0]
        self[0] *= 0
        inttrig = self.integrate(1)
        value = inttrig.eval(upper, 0) - inttrig.eval(lower, 0)
        value += const * (upper - lower)
        self[0] += const
        return value

    def shift(self, amount: Parameter) -> Trignomial:
        """
        Evaluates the trignomio at given node

        Example
        -------
        >>> old_trig = Trignomial([1, 2])
        >>> print(old_trig)
        1 + 2*sin(tau*x)
        >>> new_trig = old_trig.shift(1/4)
        >>> print(new_trig)
        1 - 2*cos(tau*x)
        """
        newcoefs = [0] * (1 + 2 * self.pmax)
        newcoefs[0] += self[0]
        for p in range(1, self.pmax + 1):
            sinpwa, cospwa = self.sincos(p * amount)
            cofs, cofc = self[2 * p - 1], self[2 * p]
            newcoefs[2 * p - 1] = cofs * cospwa + cofc * sinpwa
            newcoefs[2 * p] = -cofs * sinpwa + cofc * cospwa
        return self.__class__(newcoefs, self.frequency)

    def scale(self, value: Scalar) -> Trignomial:
        """
        Returns a function g(t) = f(a*t)
        Where a is the given parameter
        """
        return self.__class__(tuple(self), value * self.frequency)

    def roots(
        self, inflim: Optional[Parameter], suplim: Optional[Parameter]
    ) -> Iterable[Parameter]:
        raise NotImplementedError

    def __call__(self, nodes):
        return self.eval(nodes, 0)

    def __str__(self) -> str:
        if self.pmax == 0:
            return str(self[0])
        msgs = []
        flag = False
        for i, coef in enumerate(self):
            if coef == 0:
                continue
            if coef < 0:
                msg = "- "
            elif flag:
                msg = "+ "
            else:
                msg = ""
            flag = True
            p = (i + 1) // 2
            coef = abs(coef)
            if coef != 1 or i == 0:
                msg += str(coef)
            if i > 0:
                if coef != 1:
                    msg += " * "
                msg += "sin(" if i % 2 else "cos("
                if p * self.frequency != 1:
                    msg += f"{p*self.frequency}*"
                msg += "tau*t)"
            msgs.append(msg)
        return " ".join(msgs)

    def __repr__(self) -> str:
        return str(self)
