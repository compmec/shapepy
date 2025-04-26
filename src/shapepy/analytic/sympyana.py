"""
Defines the SympyAnalytic1D class

This class uses the `sympy` module to evaluate the functions.
It's a mandatory dependency now, but I would like to set it
as an optional dependency in the future.

Fow now, calling polynomials gives a SympyAnalytic1D instance
"""

from numbers import Real
from typing import Optional

import sympy as sp

from .. import default
from ..bool1d import (
    DisjointR1,
    EmptyR1,
    IntervalR1,
    SingleValueR1,
    SubSetR1,
    WholeR1,
)
from ..error import NotExpectedError
from ..logger import debug
from .base import IAnalytic1D


class SympyAnalytic1D(IAnalytic1D):
    """
    Analytic Function 1D that uses sympy to evaluate

    Example
    -------
    >>> t = SympyAnalytic1D.var  # Get the variable
    >>> SympyAnalytic1D(1 + 3*t)  # Defines a linear polynomial
    """

    var = sp.symbols("t", real=True)

    def __init__(self, expression, domain: Optional[SubSetR1] = None):
        if isinstance(expression, IAnalytic1D):
            raise TypeError
        if domain is None:
            domain = WholeR1()
        elif not isinstance(domain, SubSetR1):
            raise TypeError
        expr = sp.sympify(expression)
        if len(expr.free_symbols) > 0 and (
            (self.var not in expr.free_symbols) or (len(expr.free_symbols) > 1)
        ):
            raise ValueError(f"Received wrong input: {expr}")
        self.__expr = expr
        self.__domain = domain

    @property
    def expression(self) -> sp.Expr:
        """
        Gives the sympy expression that is internal of the SympyAnalytic1D

        It's the one used to evaluate, derivate, change domains ,etc.

        :getter: Returns the internal sympy expression
        :type: sympy.Expr
        """
        return self.__expr

    @property
    def domain(self) -> SubSetR1:
        return self.__domain

    def eval(self, node: Real, derivate: int = 0) -> Real:
        expr, var = self.expression, self.var
        if derivate != 0:
            expr = sp.diff(expr, (var, derivate))
        result = expr.subs(var, node)
        return default.finite(result)

    @debug("shapepy.analytic.spanalytic")
    def derivate(self, times: int = 1) -> IAnalytic1D:
        expr, var = self.expression, self.var
        newexpr = sp.diff(expr, (var, times))
        return self.__class__(newexpr, self.domain)

    @debug("shapepy.analytic.spanalytic")
    def shift(self, amount: Real) -> IAnalytic1D:
        expr, var = self.expression, self.var
        expr = expr.subs(var, var - amount)
        domain = self.domain.shift(amount)
        return self.__class__(expr, domain)

    @debug("shapepy.analytic.spanalytic")
    def scale(self, amount: Real) -> IAnalytic1D:
        expr, var = self.expression, self.var
        expr = expr.subs(var, amount * var)
        domain = self.domain.scale(amount)
        return self.__class__(expr, domain)

    @debug("shapepy.analytic.spanalytic")
    def integrate(
        self,
        domain: Optional[SubSetR1] = None,
        tolerance: Optional[Real] = None,
    ) -> Real:
        domain = self.domain if domain is None else (self.domain & domain)
        intervals = []
        if isinstance(domain, WholeR1):
            intervals.append((default.NEGINF, default.POSINF))
        elif isinstance(domain, IntervalR1):
            sta, end = domain[0], domain[1]
            intervals.append((sta, end))
        elif isinstance(domain, DisjointR1):
            for interv in domain.intervals:
                sta, end = interv[0], interv[1]
                intervals.append((sta, end))
        if len(intervals) == 0:
            return default.finite(0)

        result = 0
        expr, var = self.expression, self.var
        for sta, end in intervals:
            if default.isinfinity(sta):
                sta = -sp.oo
            if default.isinfinity(end):
                end = +sp.oo
            integral = sp.Integral(expr, (var, sta, end))
            result += integral.principal_value()
        return default.real(result)

    @debug("shapepy.analytic.spanalytic")
    def where(
        self, value: Real, domain: Optional[SubSetR1] = None
    ) -> SubSetR1:
        value = default.finite(value)
        domain = self.domain if domain is None else (self.domain & domain)
        if self.expression == 0:
            return domain
        all_roots = EmptyR1()
        try:
            roots = sp.real_roots(self.expression - value)
        except sp.polys.polyerrors.PolynomialError as e:  # pragma: no cover
            raise e and NotExpectedError("Should work for all polynomials")

        for root in set(roots):
            if not isinstance(root, Real):
                root = default.finite(root.evalf())
            if root in domain:
                all_roots |= SingleValueR1(root)
        return all_roots

    @debug("shapepy.analytic.spanalytic")
    def image(self, domain: Optional[SubSetR1] = None) -> SubSetR1:
        domain = self.domain if domain is None else (self.domain & domain)
        if isinstance(domain, WholeR1):
            sta, end = default.NEGINF, default.POSINF
        elif isinstance(domain, IntervalR1):
            sta, end = domain[0], domain[1]
        else:
            raise NotImplementedError
        interval = sp.Interval(sta, end)
        minvalue = sp.calculus.util.minimum(
            self.expression, self.var, interval
        )
        maxvalue = sp.calculus.util.maximum(
            self.expression, self.var, interval
        )
        if minvalue == maxvalue:
            return SingleValueR1(minvalue)
        if minvalue == default.NEGINF and maxvalue == default.POSINF:
            return WholeR1()
        return IntervalR1(minvalue, maxvalue)

    def __str__(self):
        tau = sp.symbols("tau", real=True, positive=True, constant=True)
        expr = self.expression.subs(sp.pi, tau / 2)
        return str(expr)

    def __repr__(self):
        return f"SympyAnalytic1D({self}, {self.domain})"

    def __eq__(self, other):
        if not isinstance(other, IAnalytic1D):
            try:
                other = self.__class__(other)
            except ValueError:
                return NotImplemented
        elif not isinstance(other, SympyAnalytic1D):
            return NotImplemented
        diff = self.expression - other.expression
        diff = sp.simplify(sp.expand(diff))
        return (self.domain == other.domain) & (diff == 0)

    def __add__(self, other):
        if not isinstance(other, SympyAnalytic1D):
            other = self.__class__(other)
        newexpr = self.expression + other.expression
        domain = self.domain & other.domain
        return self.__class__(newexpr, domain)

    def __mul__(self, other):
        if not isinstance(other, SympyAnalytic1D):
            other = self.__class__(other)
        newexpr = self.expression * other.expression
        domain = self.domain & other.domain
        return self.__class__(newexpr, domain)

    def __truediv__(self, other):
        if not isinstance(other, IAnalytic1D):
            other = self.__class__(other)
        if other.expression == 0:
            raise ZeroDivisionError
        newexpr = self.expression / other.expression
        domain = self.domain & other.domain
        return self.__class__(newexpr, domain)
