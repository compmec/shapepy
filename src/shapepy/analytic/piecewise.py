"""
Defines the class PiecewiseAnalytic1D
"""

from __future__ import annotations

from numbers import Real
from typing import Dict, Iterable, Optional, Tuple

from .. import default
from ..bool1d import EmptyR1, IntervalR1, SubSetR1, WholeR1, unite
from ..loggers import debug
from .base import IAnalytic1D


class PiecewiseAnalytic1D(IAnalytic1D):
    """
    A class representing a piecewise analytic function,
    allowing the concatenation of some analytic functions
    over different intervals of the domain
    """

    @classmethod
    def from_dict(cls, parameters: Dict[SubSetR1, IAnalytic1D]):
        """
        Initialize a PiecewiseAnalytic1D by a dictionary
        """
        intervals = tuple(parameters.keys())
        functions = tuple(parameters[interval] for interval in intervals)
        return cls(intervals, functions)

    def __init__(
        self, intervals: Iterable[IntervalR1], analytics: Iterable[IAnalytic1D]
    ):
        intervals = tuple(intervals)
        analytics = tuple(analytics)
        if len(analytics) < 2 or len(intervals) != len(analytics):
            raise ValueError(
                f"Invalid lengths! {len(intervals)}, {len(analytics)}"
            )
        for interval in intervals:
            if not isinstance(interval, IntervalR1):
                raise TypeError(
                    f"Must be an IntervalR1, received {type(interval)}"
                )
        middles = tuple(
            middle_knot(interval[0], interval[1]) for interval in intervals
        )
        intervals = tuple(
            interval for _, interval in sorted(zip(middles, intervals))
        )
        analytics = tuple(
            analytic for _, analytic in sorted(zip(middles, analytics))
        )
        for i in range(len(intervals) - 1):
            if (intervals[i] & intervals[i + 1]) != EmptyR1():
                raise ValueError("The intervals must be disjoint")

        self.__intervals = intervals
        self.__analytics = analytics

        knots = set(interval[0] for interval in intervals)
        knots |= set(interval[1] for interval in intervals)
        self.__knots = tuple(sorted(knots))
        self.__domain = unite(*intervals)

    @property
    def domain(self) -> SubSetR1:
        """
        Gives the domain of the analytic function
        """
        return self.__domain

    @property
    def intervals(self) -> Tuple[SubSetR1, ...]:
        """
        Gives the functions that defines the piecewise
        """
        return self.__intervals

    @property
    def analytics(self) -> Tuple[IAnalytic1D, ...]:
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
        yield from zip(self.intervals, self.analytics)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PiecewiseAnalytic1D):
            return NotImplemented
        return self.knots == other.knots and self.analytics == other.analytics

    def span(self, node: Real) -> int:
        """
        Finds the index such the given node is on interval

        Parameters
        ----------
        node: Real
            The node

        Return
        ------
        int
            The index
        """
        for i, subset in enumerate(self.__intervals):
            if node in subset:
                return i
        raise ValueError(
            f"Given node {node} is not inside the domain {self.domain}"
        )

    def eval(self, node: Real, derivate: int = 0) -> Real:
        analytic = self.analytics[self.span(node)]
        return analytic.eval(node, derivate)

    @debug("shapepy.analytic.piecewise")
    def derivate(self, times=1):
        new_analytics = (ana.derivate(times) for ana in self.analytics)
        return PiecewiseAnalytic1D(self.intervals, new_analytics)

    @debug("shapepy.analytic.piecewise")
    def shift(self, amount):
        amount = default.finite(amount)
        new_intervals = (inter.shift(amount) for inter in self.intervals)
        new_analytics = (analy.shift(amount) for analy in self.analytics)
        return PiecewiseAnalytic1D(new_intervals, new_analytics)

    @debug("shapepy.analytic.piecewise")
    def scale(self, amount):
        amount = default.finite(amount)
        new_intervals = (inter.scale(amount) for inter in self.intervals)
        new_analytics = (analy.scale(amount) for analy in self.analytics)
        return PiecewiseAnalytic1D(new_intervals, new_analytics)

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
        new_intervals = (inter & subdomain for inter in self.intervals)
        new_analytics = (analy.section(subdomain) for analy in self.analytics)
        return PiecewiseAnalytic1D(new_intervals, new_analytics)

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
            new_analytics = (analy + other for analy in self.analytics)
            return PiecewiseAnalytic1D(self.intervals, new_analytics)
        knots = sorted(set(self.knots) | set(other.knots))
        middles = tuple(
            middle_knot(ta, tb) for ta, tb in zip(knots, knots[1:])
        )

        new_intervals = []
        new_analytics = []
        for knot in middles:
            sespan = self.span(knot)
            otspan = other.span(knot)
            new_interval = self.intervals[sespan] & other.intervals[otspan]
            new_analytic = self.analytics[sespan] + other.analytics[otspan]
            new_intervals.append(new_interval)
            new_analytics.append(new_analytic)
        return PiecewiseAnalytic1D(new_intervals, new_analytics)

    @debug("shapepy.analytic.piecewise")
    def __mul__(self, other: IAnalytic1D) -> IAnalytic1D:
        if not isinstance(other, PiecewiseAnalytic1D):
            new_analytics = (analy * other for analy in self.analytics)
            return PiecewiseAnalytic1D(self.intervals, new_analytics)
        knots = sorted(set(self.knots) | set(other.knots))
        middles = tuple(
            middle_knot(ta, tb) for ta, tb in zip(knots, knots[1:])
        )

        new_intervals = []
        new_analytics = []
        for knot in middles:
            sespan = self.span(knot)
            otspan = other.span(knot)
            new_interval = self.intervals[sespan] & other.intervals[otspan]
            new_analytic = self.analytics[sespan] * other.analytics[otspan]
            new_intervals.append(new_interval)
            new_analytics.append(new_analytic)
        return PiecewiseAnalytic1D(new_intervals, new_analytics)

    @debug("shapepy.analytic.piecewise")
    def __truediv__(self, other: Real) -> IAnalytic1D:
        other = default.finite(other)
        new_analytics = (analy / other for analy in self.analytics)
        return PiecewiseAnalytic1D(self.intervals, new_analytics)


def middle_knot(left: Real, right: Real) -> Real:
    """
    Computes the middle point of the interval [left, right]

    If one of them is infinity, we only shift by 1 unit:

    Example
    -------
    >>> middle_knot(-1, 1)
    0
    >>> middle_knot(0, 2)
    1
    >>> middle_knot(-inf, 10)
    9
    >>> middle_knot(10, +inf)
    11
    """
    if default.isinfinity(left):
        return right - 1
    if default.isinfinity(right):
        return left + 1
    return (left + right) / 2
