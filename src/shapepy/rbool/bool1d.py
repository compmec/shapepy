"""
This file contains functions to perform boolean operation on 1D subsets
"""

from numbers import Real
from typing import Callable, Iterable, List, Set, Union

from ..tools import Is
from .base import EmptyR1, Future, SubSetR1, WholeR1
from .singles import DisjointR1, IntervalR1, SingleR1, bigger, lower


def extract_knots(obj: SubSetR1) -> Iterable[Real]:
    """
    Extract all the knots from the SubSetR1.

    If it's a SingleR1, gives the internal value
    If it's a IntervalR1, gives the extremities
    If it's a DisjointR1, use recursion
    """
    if isinstance(obj, SingleR1):
        yield obj.internal
    if isinstance(obj, IntervalR1):
        if Is.finite(obj[0]):
            yield obj[0]
        if Is.finite(obj[1]):
            yield obj[1]
    if isinstance(obj, DisjointR1):
        for sub in obj:
            yield from extract_knots(sub)


def general_doer(
    subsets: Iterable[SubSetR1], function: Callable[[Real], bool]
) -> SubSetR1:
    """
    Receives a group of SubSetR1 and makes the union, the intersection,
    or the inversion depending on the given function.

    This is an internal function and should not be used careless
    """
    subsets = tuple(map(Future.convert, subsets))
    if not all(isinstance(subset, SubSetR1) for subset in subsets):
        raise TypeError
    set_all_knots: Set[Real] = set()
    for subset in subsets:
        set_all_knots |= set(extract_knots(subset))
    all_knots: List[Real] = sorted(set_all_knots)
    eval_knots: List[Real] = [0] * (2 * len(all_knots) + 1)
    eval_knots[0] = all_knots[0] - 1
    eval_knots[-1] = all_knots[-1] + 1
    for i, knot in enumerate(all_knots):
        eval_knots[2 * i + 1] = knot
    for i, (knota, knotb) in enumerate(zip(all_knots, all_knots[1:])):
        eval_knots[2 * i + 2] = (knota + knotb) / 2
    return general_subset(all_knots, map(function, eval_knots))


def general_subset(knots: Iterable[Real], insides: Iterable[bool]) -> SubSetR1:
    """
    Transforms the knots real values and the vector of insides into a SubSetR1

    Basically it gets all the knots from a group of subsets:
    * internal value of SingleR1
    * start and end of an IntervalR1
    * knots of the internals for case DisjointR1
    and then mark the middle points from the

    Then, this function walks from left to right, deciding which SingleR1
    or IntervalR1 should be gotten to make the return SubSetR1.

    This is an internal function and should not be used careless
    """
    insides = tuple(insides)
    knots = tuple(knots)
    if len(insides) != 2 * len(knots) + 1:
        raise ValueError(f"Invalid: knots = {knots}, insides = {insides}")
    if all(insides):
        return WholeR1()
    if not any(insides):
        return EmptyR1()

    items: List[Union[SingleR1, IntervalR1]] = []
    start: Union[None, Real] = None
    close: bool = False
    for i, knot in enumerate(knots):
        left = insides[2 * i]
        midd = insides[2 * i + 1]
        righ = insides[2 * i + 2]
        if left == midd == righ:
            continue
        if not left and not righ:
            items.append(SingleR1(knot))
            continue
        if left:  # Finish interval
            if start is None:
                newinterv = lower(knot, midd)
            else:
                newinterv = IntervalR1(start, knot, close, midd)
            items.append(newinterv)
            start = None
        if righ:
            start = knot
            close = midd
    if start is not None:
        newinterv = bigger(start, close)
        items.append(newinterv)

    if len(items) == 1:
        return items[0]

    return DisjointR1(items)


def unite(*subsets: SubSetR1) -> SubSetR1:
    """
    Unites a group of subsets

    Parameters
    ----------
    subsets : Iterable[SubSetR1]
        The subsets of R1 to be united

    Return
    ------
    SubSetR1
        The result of the union of the given subsets

    Example
    -------
    >>> unite({10}, [-10, 5])
    [-10, 5] U {10}
    >>> unite((-10, 5), 5)
    (-10, 5]
    >>> unite(("-inf", 10), (-10, "inf"))
    (-inf, +inf)
    """

    def or_func(x):
        return any(x in sub for sub in subsets)

    return general_doer(subsets, or_func)


def intersect(*subsets: SubSetR1) -> SubSetR1:
    """
    Intersects a group of subsets

    Parameters
    ----------
    subsets : Iterable[SubSetR1]
        The subsets of R1 to be intersected

    Return
    ------
    SubSetR1
        The result of the union of the given subsets

    Example
    -------
    >>> intersect({-10}, [-10, 5])
    {-10}
    >>> intersect((-10, 5), [3, 10])
    [3, 5)
    >>> intersect((-10, 0), (0, 10))
    {}
    """

    def and_func(x):
        return all(x in sub for sub in subsets)

    return general_doer(subsets, and_func)


def invert(subset: SubSetR1) -> SubSetR1:
    """
    Computes the complementar / inversion of the given subset

    Parameters
    ----------
    subset : SubSetR1
        The subset of R1 to be inverted

    Return
    ------
    SubSetR1
        The inverted subset

    Example
    -------
    >>> invert({-10})
    (-inf, -10) U (-10, +inf)
    >>> invert((-10, 10))
    (-inf, -10] U [10, +inf)
    >>> invert(("-inf", 0))
    [0, +inf)
    """

    def inv_func(x):
        return x not in subset

    return general_doer((subset,), inv_func)


def contains(subseta: SubSetR1, subsetb: SubSetR1) -> bool:
    """
    Tells if B in A

    Parameters
    ----------
    subseta : SubSetR1
        The A subset
    subsetb : SubSetR1
        The B subset

    Return
    ------
    bool
        The result

    """
    return Future.convert(subsetb) in Future.convert(subseta)
