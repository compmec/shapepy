"""
This file contains a class Hypernomial that allows evaluating and
making operations with hypernomials, like adding, multiplying, etc

A hypernomial is similar to a trignomials, but uses hyperbolic functions :
    * sinh(t) instead of sin(t)
    * cosh(t) instead of cos(t)

Example
-------
>>> hyper = Hypernomial([1, 2, 3])
>>> print(hyper)
1 + 2 * sinh(x) + 3 * cosh(x)
>>> hyper = Hypernomial([1, 2, 3, 4])
>>> print(hyper)
1 + 2 * sinh(x) + 3 * cosh(x) + 4 * sinh(2*x)
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Iterable, Optional, Tuple, Union

from ..core import IAnalytic
from .utils import keys_pow

Parameter = Union[int, float]
Scalar = Union[int, float]


class Hypernomial(IAnalytic):
    """
    Defines a hyberbolic version of a trignomials

    We define a hyperbolic version:
    H(x) = a0 + a1 * sinh(w*x) + a2 * cosh(w*x) + ...
           + a_{2p-1} * sinh(p*w*x) + a_{2p} * cosh(p*w*x)

    Example
    -------
    >>> hyper = Hypernomial([1, 0, 1])
    >>> print(hyper)
    1 + cosh(x)
    >>> hyper.eval(0)
    2.0
    >>> hyper.eval(1)
    2.54308063482
    >>> hyper = Hypernomial([1, 2, 0, -3])
    >>> print(hyper)
    1 + 2 * sinh(x) - 3*sinh(2*x)

    """

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
        if not isinstance(other, Hypernomial):
            return False
        if self.pmax != other.pmax or self.frequency != other.frequency:
            return False
        atol = 1e-9
        return all(abs(ci - cj) < atol for ci, cj in zip(self, other))

    @property
    def pmax(self) -> int:
        """
        Returns the maximum harmonic value of the hypernomio

        Example
        -------
        >>> hyper = Hypernomial([1, 0, 1])  # 1 + cosh(x)
        >>> hyper.pmax
        1
        >>> hyper = Hypernomial([1, 0, 1, 2])  # 1 + cosh(x) + sinh(2*x)
        >>> hyper.pmax
        2
        """
        return len(self.__values) // 2

    @property
    def frequency(self) -> Scalar:
        """
        Returns the frequency of the hypernomio

        Example
        -------
        >>> hyper = Hypernomial([1, 0, 1])  # 1 + cosh(x)
        >>> hyper.frequency
        1
        >>> hyper = Hypernomial([1, 0, 1], 3)  # 1 + cosh(3*x)
        >>> hyper.frequency
        3
        """
        return self.__freq

    def __iter__(self):
        yield from self.__values

    def __getitem__(self, index):
        return self.__values[index]

    def __setitem__(self, key, newvalue):
        self.__values[key] = newvalue

    def __neg__(self) -> Hypernomial:
        return self.__class__(tuple(-coef for coef in self), self.frequency)

    def __add__(self, other: Union[Scalar, Hypernomial]):
        if not isinstance(other, Hypernomial):
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

    def __sub__(self, other: Union[Scalar, Hypernomial]) -> Hypernomial:
        return self.__add__(-other)

    def __mul__(self, other: Union[Scalar, Hypernomial]) -> Hypernomial:
        if not isinstance(other, Hypernomial):
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
                        sind = 1 if (i > j) ^ (i % 2) else 1
                        values[2 * d - 1] += temp * sind
                    values[2 * s - 1] += temp
                else:
                    coss = -1 if i % 2 else 1
                    values[2 * d] += temp * coss
                    values[2 * s] += temp
        return self.__class__(values, self.frequency)

    def __divmod__(
        self, other: Union[Scalar, Hypernomial]
    ) -> Tuple[Hypernomial, Hypernomial]:
        if isinstance(other, Hypernomial) and not other.pmax:
            return self.__divmod__(other[0])
        if not isinstance(other, Hypernomial):
            if not other:
                raise ZeroDivisionError("division by zero")
            quot = self.__class__((ci / other for ci in self), self.frequency)
            rest = Hypernomial([0 * sum(self)])
            return quot, rest
        raise NotImplementedError

    def __floordiv__(self, other: Union[Scalar, Hypernomial]) -> Hypernomial:
        return self.__divmod__(other)[0]

    def __mod__(self, other: Union[Scalar, Hypernomial]) -> Hypernomial:
        return self.__divmod__(other)[1]

    def __truediv__(self, other: Scalar) -> Hypernomial:
        div, res = self.__divmod__(other)
        if res != 0:
            raise ValueError(f"Cannot divide {self} by {other}")
        return div

    def __rsub__(self, other: Scalar) -> Hypernomial:
        return (-self).__add__(other)

    def __rmul__(self, other: Scalar) -> Hypernomial:
        return self.__mul__(other)

    def __radd__(self, other: Scalar) -> Hypernomial:
        return self.__add__(other)

    def __pow__(self, exponent: int) -> Hypernomial:
        exponent = int(exponent)
        if exponent < 0:
            raise ValueError
        if exponent == 0:
            return self.__class__([1 + 0 * sum(self)])
        needs = sorted(keys_pow(exponent))
        cache = {1: self}
        for n in needs:
            cache[n] = cache[n // 2] * cache[n - n // 2]
        return cache[exponent]

    def eval(self, node: Parameter, derivate: int = 0):
        """
        Evaluates the hypernomio at given node

        Example
        -------
        >>> hyper = Hypernomial([1, 2])
        >>> print(hyper)
        1 + 2*sinh(x)
        >>> hyper.eval(0)
        1
        >>> hyper.eval(0, 0)
        1
        >>> hyper.eval(1, 0)
        3.3504023872876029
        """
        if derivate != 0:
            return self.derivate(derivate).eval(node, 0)
        results = self[0]
        for pi in range(self.pmax):
            sinh = math.sinh(self.frequency * node)
            cosh = math.cosh(self.frequency * node)
            results += self[2 * pi + 1] * sinh + self[2 * pi + 2] * cosh
        return results

    def derivate(self, times: int = 1) -> Hypernomial:
        times = int(times)
        if times < 0:
            raise ValueError
        if times == 0:
            return self.__class__(tuple(self), self.frequency)
        const = self.frequency**times
        coefs = list(self)
        coefs[0] *= 0
        for i in range(self.pmax):
            term = (i + 1) ** times
            coefs[2 * i + 1] *= const * term
            coefs[2 * i + 2] *= const * term
        times %= 4
        if times % 2:
            for i in range(self.pmax):
                sinh = coefs[2 * i + 1]
                cosh = coefs[2 * i + 2]
                coefs[2 * i + 1] = cosh
                coefs[2 * i + 2] = sinh
        return self.__class__(coefs, self.frequency)

    def integrate(self, times: int) -> Hypernomial:
        times = int(times)
        if times < 0:
            raise ValueError
        if times == 0:
            return self.__class__(tuple(self), self.frequency)
        if self[0]:
            raise ValueError("Cannot integrate the function with constant")
        const = self.frequency**times
        coefs = list(self)
        for i in range(self.pmax):
            term = (i + 1) ** times
            coefs[2 * i + 1] /= const * term
            coefs[2 * i + 2] /= const * term
        times %= 4
        if times % 2:
            for i in range(self.pmax):
                sinh, cosh = coefs[2 * i + 1], coefs[2 * i + 2]
                coefs[2 * i + 1] = cosh
                coefs[2 * i + 2] = sinh
        return self.__class__(coefs, self.frequency)

    def defintegral(self, lower: Parameter, upper: Parameter) -> Scalar:
        const = self[0]
        self[0] *= 0
        inthyper = self.integrate(1)
        value = inthyper.eval(upper, 0) - inthyper.eval(lower, 0)
        value += const * (upper - lower)
        self[0] += const
        return value

    def shift(self, amount: Parameter) -> Hypernomial:
        """
        Evaluates the hypernomio at given node

        Example
        -------
        >>> old_hyper = Hypernomial([1, 2])
        >>> print(old_hyper)
        1 + 2*sinh(x)
        >>> new_hyper = old_hyper.shift(1/4)
        >>> print(new_hyper)
        1 - 2*cosh(x)
        """
        raise NotImplementedError

    def scale(self, value: Scalar) -> Hypernomial:
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
                msg += "sinh(" if i % 2 else "cosh("
                if p * self.frequency != 1:
                    msg += f"{p*self.frequency}*"
                msg += "t)"
            msgs.append(msg)
        return " ".join(msgs)

    def __repr__(self) -> str:
        return str(self)
