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
from typing import Iterable, Optional, Tuple, Union

from ..core import IAnalytic, Parameter, Scalar
from .base import BaseAnalytic


class Trignomial(BaseAnalytic):
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
        """
        Computes the sinus of given angle.
        The angle mesure is unitary, meaning

            sin(x) = sin(1+x) for all x

        Parameters
        ----------
        unit_angle: Scalar
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
        unit_angle %= 1
        quad, subangle = divmod(4 * unit_angle, 1)
        if not subangle:
            if not quad % 2:
                return 0
            return 1 - 2 * (quad == 3)
        return Trignomial.SIN(unit_angle * Trignomial.TAU)

    @staticmethod
    def cos(unit_angle: Scalar) -> Scalar:
        """
        Computes the cossinus of given angle.
        The angle mesure is unitary, meaning

            cos(x) = cos(1+x) for all x

        Parameters
        ----------
        unit_angle: Scalar
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
        unit_angle %= 1
        quad, subangle = divmod(4 * unit_angle, 1)
        if not subangle:
            if quad % 2:
                return 0
            return 1 - 2 * (quad == 2)
        return Trignomial.COS(unit_angle * Trignomial.TAU)

    @staticmethod
    def sincos(unit_angle: Scalar) -> Tuple[Scalar, Scalar]:
        """
        Computes the sinus and cossinus of given angle at same time.
        The angle mesure is unitary, meaning

            sin(x) = cos(1+x) for all x
            cos(x) = cos(1+x) for all x

        Parameters
        ----------
        unit_angle: Scalar
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
        super().__init__(values)
        self.__freq = frequency

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
        return len(self) // 2

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
        6.283185307
        >>> trig = Trignomial([1, 0, 1], 3)  # 1 + cos(3*tau*x)
        >>> trig.omega
        18.8495559
        """
        return self.TAU * self.frequency

    def __neg__(self) -> Trignomial:
        return self.__class__(tuple(-coef for coef in self), self.frequency)

    def __add__(self, other: Union[Scalar, Trignomial]):
        if isinstance(other, IAnalytic):
            if not isinstance(other, Trignomial):
                raise TypeError(f"Cannot add {self} with {other}")
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

    def __mul__(self, other: Union[Scalar, Trignomial]) -> Trignomial:
        if isinstance(other, IAnalytic):
            if not isinstance(other, Trignomial):
                raise TypeError(f"Cannot multiply {self} by {other}")
        if not isinstance(other, Trignomial):
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
                        sind = -1 if (i > j) ^ (i % 2) else 1
                        values[2 * diff - 1] += temp * sind
                    values[2 * soma - 1] += temp
                else:
                    coss = -1 if i % 2 else 1
                    values[2 * diff] += temp
                    values[2 * soma] += temp * coss
        return self.__class__(values, self.frequency)

    def __divmod__(
        self, other: Union[Scalar, Trignomial]
    ) -> Tuple[Trignomial, Trignomial]:
        print(f"Dividing {self} by {other}")
        if isinstance(other, IAnalytic):
            if not isinstance(other, Trignomial):
                raise TypeError(f"Cannot divide {self} by {other}")
            if not other.pmax:
                return self.__divmod__(other[0])
        if other == 0:
            raise ZeroDivisionError("division by zero")
        if not isinstance(other, Trignomial):
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

    def eval(self, node: Parameter, derivate: int = 0):
        """
        Evaluates the trignomio  at given node

        Parameters
        ----------
        node: Parameter
            The value of t to compute p(t)
        derivate: int
            Number of times to derivate the polynomial

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
        for pval in range(1, self.pmax + 1):
            sin, cos = Trignomial.sincos(node)
            results += self[2 * pval - 1] * sin + self[2 * pval] * cos
        return results

    def derivate(self, times: int = 1) -> Trignomial:
        """
        Derivate the trignomio, giving a new one trignomio

        Parameters
        ----------
        times: int, default = 1
            How many times to derivate p(t)
        return: Trignomial
            The derivated trignomio

        :raises ValueError: If ``times`` is negative

        Example
        -------
        >>> trig = Trignomial([1, 2])
        >>> print(trig)
        1 + 2*sin(tau*x)
        >>> dtrig = trig.derivate()
        >>> print(dtrig)
        12.566370614 * cos(tau*x)  # 2*tau*cos(tau*x)
        """
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
        """
        Integrate the trignomio, giving a new one

        The constant term must me zero

        Parameters
        ----------
        times: int, default = 1
            Number of times to integrate the polynomial
        return: Trignomial
            The integrated trignomial

        :raises ValueError: If the constant term is not zero

        Example
        -------
        >>> trig = Trignomial([0, 2])
        >>> print(trig)
        2*sin(tau*x)
        >>> itrig = trig.integrate()
        >>> print(itrig)
        -0.31830988 * cos(tau*x)  # (-2/tau)*cos(tau*x)
        """
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
        """
        Evaluates the defined integral of the trignomial

        Parameters
        ----------
        lower: Parameter
            The lower bound of integration
        upper: Parameter
            The upper bound of integration
        return: Scalar
            The value of the defined integral

        Example
        -------
        >>> trig = Trignomial([1, 2])
        >>> print(trig)
        2*sin(tau*x)
        >>> trig.defintegral(0, 0.5)
        0.81830988  # 1/2 + 4/tau
        """
        const = self[0]
        self[0] *= 0
        inttrig = self.integrate(1)
        value = inttrig.eval(upper, 0) - inttrig.eval(lower, 0)
        value += const * (upper - lower)
        self[0] += const
        return value

    def shift(self, amount: Parameter) -> Trignomial:
        """
        Shifts the trignomio by given amount

        Computes the trignomial q(x) = p(x-d) by
        translating the trignomial by 'd' to the right.

        Parameters
        ----------
        amount: Parameter
            The quantity to shift the function

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
        for pval in range(1, self.pmax + 1):
            sinpwa, cospwa = self.sincos(pval * amount)
            cofs, cofc = self[2 * pval - 1], self[2 * pval]
            newcoefs[2 * pval - 1] = cofs * cospwa + cofc * sinpwa
            newcoefs[2 * pval] = -cofs * sinpwa + cofc * cospwa
        return self.__class__(newcoefs, self.frequency)

    def scale(self, amount: Scalar) -> Trignomial:
        """
        Computes the polynomial q(t) = p(s*t) by
        scaling the polynomial by 's'.

        p(x) = a0 + a1 * t + ... + ap * t^p
        q(x) = b0 + b1 * t + ... + bp * t^p
             = a0 + a1 * (s*t) + ... + ap * (s*t)^p

        Parameters
        ----------
        amount: Parameter
            The quantity to scale the t-axis

        Example
        -------
        >>> old_trig = Trignomial([1, 2])
        >>> print(old_trig)
        1 + 2*sin(tau*x)
        >>> new_trig = old_trig.scale(2)
        >>> print(new_trig)
        1 + 2*sin(2*tau*x)

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

        If no interval is given, then it computes in the unitary domain [0, 1)

        If t0 is a root, then (t0 + 1) is also a root

        Parameters
        ----------
        inflim: Optional[Parameter], default = None
            The lower bound of research
        suplim: Optional[Parameter], default = None
            The upper bound of research

        Example
        -------
        >>> poly = Trignomial([0, 1])
        >>> poly.roots()
        (0, )
        >>> poly.roots(0, 3)
        (0, 1, 2, 3)
        """
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
            pval = (i + 1) // 2
            coef = abs(coef)
            if coef != 1 or i == 0:
                msg += str(coef)
            if i > 0:
                if coef != 1:
                    msg += " * "
                msg += "sin(" if i % 2 else "cos("
                if pval * self.frequency != 1:
                    msg += f"{pval*self.frequency}*"
                msg += "tau*t)"
            msgs.append(msg)
        return " ".join(msgs)
