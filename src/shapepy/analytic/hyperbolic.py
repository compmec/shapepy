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

from fractions import Fraction
from typing import Iterable, Optional, Tuple, Union

from ..core import Configuration, IAnalytic, Parameter, Scalar
from .base import BaseAnalytic


class Hypernomial(BaseAnalytic):
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
        super().__init__(values)
        self.__freq = frequency

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
        return len(self) // 2

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

    def __neg__(self) -> Hypernomial:
        return self.__class__(tuple(-coef for coef in self), self.frequency)

    def __add__(self, other: Union[Scalar, Hypernomial]):
        if isinstance(other, IAnalytic):
            if not isinstance(other, self.__class__):
                raise TypeError(f"Cannot add {self} with {other}")
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

    def __mul__(self, other: Union[Scalar, Hypernomial]) -> Hypernomial:
        if isinstance(other, IAnalytic):
            if not isinstance(other, self.__class__):
                raise TypeError(f"Cannot multiply {self} by {other}")
        if not isinstance(other, Hypernomial):
            coefs = tuple(other * coef for coef in self)
            return self.__class__(coefs, self.frequency)
        if self.frequency != other.frequency:
            raise NotImplementedError
        values = [0] * (1 + 2 * (self.pmax + other.pmax))
        for i, vali in enumerate(self):
            harmi = (i + 1) // 2
            for j, valj in enumerate(other):
                harmj = (j + 1) // 2
                soma = harmi + harmj
                diff = abs(harmi - harmj)
                temp = (vali * valj) / 2
                if (i % 2) ^ (j % 2):
                    if harmi != harmj:
                        sind = 1 if (i > j) ^ (i % 2) else 1
                        values[2 * diff - 1] += temp * sind
                    values[2 * soma - 1] += temp
                else:
                    coss = -1 if i % 2 else 1
                    values[2 * diff] += temp * coss
                    values[2 * soma] += temp
        return self.__class__(values, self.frequency)

    def __divmod__(
        self, other: Union[Scalar, Hypernomial]
    ) -> Tuple[Hypernomial, Hypernomial]:
        if isinstance(other, IAnalytic):
            if not isinstance(other, self.__class__):
                raise TypeError(f"Cannot divide {self} by {other}")
        if isinstance(other, Hypernomial) and not other.pmax:
            return self.__divmod__(other[0])
        if not isinstance(other, Hypernomial):
            if not other:
                raise ZeroDivisionError("division by zero")
            quot = self.__class__((ci / other for ci in self), self.frequency)
            rest = Hypernomial([0 * sum(self)])
            return quot, rest
        raise NotImplementedError

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
        for pval in range(1, self.pmax + 1):
            sinh = Configuration.SINH(self.frequency * node)
            cosh = Configuration.COSH(self.frequency * node)
            results += self[2 * pval - 1] * sinh + self[2 * pval] * cosh
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
        """
        Integrate the hypernomio, giving a new one

        The constant term must me zero

        Parameters
        ----------
        times: int, default = 1
            Number of times to integrate the hypernomio
        return: Hypernomial
            The integrated hypernomio

        :raises ValueError: If the constant term is not zero

        Example
        -------
        >>> hyper = Hypernomial([0, 2])
        >>> print(hyper)
        2 * sinh(x)
        >>> ihyper = hyper.integrate()
        >>> print(ihyper)
        2 * cosh(x)
        """
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

        Parameters
        ----------
        amount: Parameter
            The quantity to shift the function

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

    def scale(self, amount: Scalar) -> Hypernomial:
        """
        Computes the hypernomio q(t) = p(s*t) by
        scaling the hypernomio by 's'.

        Parameters
        ----------
        amount: Parameter
            The quantity to scale the t-axis

        Example
        -------
        >>> old_hyper = Hypernomial([1, 2])
        >>> print(old_hyper)
        1 + 2 * sinh(x)
        >>> new_hyper = old_hyper.scale(2)
        >>> print(new_hyper)
        1 + 2 * sinh(2*x)
        """
        return self.__class__(tuple(self), amount * self.frequency)

    def roots(
        self,
        inflim: Optional[Parameter] = None,
        suplim: Optional[Parameter] = None,
    ) -> Iterable[Parameter]:
        """
        Computes the roots of the trignomial that are
        inside the given interval

        If no interval is given, then it computes in the entire domain


        Parameters
        ----------
        inflim: Optional[Parameter], default = None
            The lower bound of research
        suplim: Optional[Parameter], default = None
            The upper bound of research

        Example
        -------
        >>> hyper = Trignomial([0, 1])
        >>> print(hyper)
        sinh(x)
        >>> hyper.roots()
        (0, )
        """
        raise NotImplementedError

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
            pval = (i + 1) // 2
            coef = abs(coef)
            if coef != 1 or i == 0:
                msg += str(coef)
            if i > 0:
                if coef != 1:
                    msg += " * "
                msg += "sinh(" if i % 2 else "cosh("
                if pval * self.frequency != 1:
                    msg += f"{pval*self.frequency}*"
                msg += "t)"
            msgs.append(msg)
        return " ".join(msgs)
