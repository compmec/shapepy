"""Wraps the rbool library and add some useful functions for this package"""

from typing import Any, Callable, Iterator, Type

import rbool

from .loggers import debug
from .scalar.reals import Real
from .tools import Is

EmptyR1: Type = rbool.Empty
IntervalR1: Type = rbool.Interval
SingleR1: Type = rbool.SingleValue
SubSetR1: Type = rbool.SubSetR1
DisjointR1: Type = rbool.Disjoint
WholeR1: Type = rbool.Whole
extract_knots: Callable[[Any], Iterator[Any]] = rbool.extract_knots
from_any: Callable[[Any], object] = rbool.from_any
shift = rbool.move
scale = rbool.scale
unite = rbool.unite
infimum = rbool.infimum
supremum = rbool.supremum


def create_single(knot: Real) -> SingleR1:
    """Creates a Subset on real-line that contains only one value"""
    if not Is.finite(knot):
        raise ValueError(f"Invalid {knot}")
    return SingleR1(knot)


def create_interval(knota: Real, knotb: Real) -> IntervalR1:
    """Creates a closed interval [a, b] in the real line"""
    if not Is.real(knota) or not Is.real(knotb):
        raise TypeError(f"Invalid typos: {type(knota)}, {type(knotb)}")
    if knotb <= knota:
        raise ValueError(f"{knotb} <= {knota}")
    return IntervalR1(knota, knotb)


@debug("shapepy.rbool")
def subset_length(subset: SubSetR1) -> Real:
    """Computes the length of the subset

    Example
    -------
    >>> subset_length([0, 1])
    1
    >>> subset_length([-3, 2])
    5
    >>> subset_length({})
    0
    """
    subset = from_any(subset)
    if Is.instance(subset, IntervalR1):
        return subset[1] - subset[0]
    if Is.instance(subset, DisjointR1):
        return sum(map(subset_length, subset.intervals))
    return 0
