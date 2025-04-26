"""
Defines the class PiecewiseAnalytic1D
"""

from __future__ import annotations

from numbers import Real
from typing import Dict, Iterable, Optional, Tuple

from .. import default
from ..bool1d import EmptyR1, SubSetR1, WholeR1, infimum, supremum, unite
from ..logger import debug
from .base import IAnalytic1D


class PiecewiseAnalytic1D(IAnalytic1D):
    """
    A class representing a piecewise analytic function,
    allowing the concatenation of some analytic functions
    over different intervals of the domain
    """

    def __init__(
        self,
        analytics: Dict[SubSetR1, IAnalytic1D],
    ):
        if len(analytics) < 2:
            raise ValueError(f"Too few analytics: {len(analytics)} < 2")
        keys = tuple(analytics.keys())
        for i, key in enumerate(keys):
            for j in range(i + 1, len(keys)):
                if key & keys[j] != EmptyR1():
                    raise ValueError(
                        f"All the subdomains must be disjoints: {keys}"
                    )
        analytics = {
            key: value.section(key) for key, value in analytics.items()
        }
        self.__analytics = analytics
        self.__domain = unite(*tuple(analytics.keys()))
        knots = set(map(supremum, analytics.keys()))
        knots |= set(map(infimum, analytics.keys()))
        self.__knots = tuple(sorted(knots))

    @property
    def domain(self) -> SubSetR1:
        """
        Gives the domain of the analytic function
        """
        return self.__domain

    @property
    def analytics(self) -> Dict[SubSetR1, IAnalytic1D]:
        """
        Gives the functions that defines the piecewise
        """
        return self.__analytics

    @property
    def knots(self) -> Tuple[Real, ...]:
        """
        Gives the subdivision
        """
        return self.__knots

    def __iter__(self) -> Iterable[SubSetR1, IAnalytic1D]:
        yield from self.analytics.items()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PiecewiseAnalytic1D):
            return NotImplemented
        return self.knots == other.knots and self.analytics == other.analytics

    def eval(self, node: Real, derivate: int = 0) -> Real:
        for subset, analytic in self:
            if node in subset:
                return analytic.eval(node, derivate)
        raise ValueError(
            f"Given node {node} is not inside the domain {self.domain}"
        )

    @debug("shapepy.analytic.piecewise")
    def derivate(self, times=1):
        return PiecewiseAnalytic1D(
            {subset: analytic.derivate(times) for subset, analytic in self}
        )

    @debug("shapepy.analytic.piecewise")
    def shift(self, amount):
        amount = default.finite(amount)
        new_analytics = {}
        for subset, analytic in self:
            new_analytics[subset.shift(amount)] = analytic.shift(amount)
        return PiecewiseAnalytic1D(new_analytics)

    @debug("shapepy.analytic.piecewise")
    def scale(self, amount):
        amount = default.finite(amount)
        new_analytics = {}
        for subset, analytic in self:
            new_analytics[subset.scale(amount)] = analytic.shift(amount)
        return PiecewiseAnalytic1D(new_analytics)

    @debug("shapepy.analytic.piecewise")
    def integrate(
        self,
        domain: Optional[SubSetR1] = None,
        tolerance: Optional[Real] = None,
    ) -> Real:
        domain = self.domain if domain is None else (self.domain & domain)
        result = 0
        for subset, analytic in self:
            result += analytic.integrate(subset & domain, tolerance)
        return result

    @debug("shapepy.analytic.piecewise")
    def where(
        self, value: Real, domain: Optional[SubSetR1] = None
    ) -> SubSetR1:
        domain = self.domain if domain is None else (self.domain & domain)
        result = EmptyR1()
        for subset, analytic in self:
            result |= analytic.where(value, subset & domain)
        return result

    @debug("shapepy.analytic.piecewise")
    def image(self, domain: Optional[SubSetR1] = None) -> Real:
        domain = self.domain if domain is None else (self.domain & domain)
        result = EmptyR1()
        for subset, analytic in self:
            result |= analytic.image(subset & domain)
        return result

    def section(
        self, subdomain: Optional[SubSetR1] = None
    ) -> PiecewiseAnalytic1D:
        if subdomain is None:
            subdomain = WholeR1()
        new_analytics = {
            key & subdomain: value for key, value in self.analytics.items()
        }
        return self.__class__(new_analytics)

    def __str__(self):
        msgs = []
        for subset, analytic in self:
            msgs.append(str(subset) + ": " + str(analytic))
        return ", ".join(msgs)

    def __repr__(self):
        msgs = []
        for subset, analytic in self:
            msgs.append(repr(subset) + ": " + repr(analytic))
        return "PiecewiseAnalytic1D(" + ", ".join(msgs) + ")"

    @debug("shapepy.analytic.piecewise")
    def __add__(self, other: IAnalytic1D) -> IAnalytic1D:
        if not isinstance(other, PiecewiseAnalytic1D):
            return PiecewiseAnalytic1D(
                {subset: analytic + other for subset, analytic in self}
            )
        new_analytics = {}
        for self_subset, self_analytic in self:
            for other_subset, other_analytic in other:
                new_subset = self_subset & other_subset
                if new_subset == EmptyR1():
                    continue
                new_analytics[new_subset] = self_analytic + other_analytic
        return PiecewiseAnalytic1D(new_analytics)

    @debug("shapepy.analytic.piecewise")
    def __mul__(self, other: IAnalytic1D) -> IAnalytic1D:
        if not isinstance(other, PiecewiseAnalytic1D):
            return PiecewiseAnalytic1D(
                {subset: analytic * other for subset, analytic in self}
            )
        new_analytics = {}
        for self_subset, self_analytic in self:
            for other_subset, other_analytic in other:
                new_subset = self_subset & other_subset
                if new_subset == EmptyR1():
                    continue
                new_analytics[new_subset] = self_analytic * other_analytic
        return PiecewiseAnalytic1D(new_analytics)

    @debug("shapepy.analytic.piecewise")
    def __truediv__(self, other: Real) -> IAnalytic1D:
        other = default.finite(other)
        return PiecewiseAnalytic1D(
            {subset: analytic / other for subset, analytic in self}
        )
