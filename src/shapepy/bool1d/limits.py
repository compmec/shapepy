"""
Contains some functions to compute the limits of the given subsets
"""

from numbers import Real
from typing import Union

from .. import default
from ..error import NotExpectedError
from .base import EmptyR1, Future, SubSetR1, WholeR1
from .singles import DisjointR1, IntervalR1, SingleValueR1


def infimum(subset: SubSetR1) -> Union[Real, None]:
    """
    Computes the infimum of the SubSetR1

    Parameters
    ----------
    subset: SubSetR1
        The subset to get the infimum

    Return
    ------
    Real | None
        The infimum value, or None if receives EmptyR1

    Example
    -------
    >>> infimum("{}")  # EmptyR1
    None
    >>> infimum("(-inf, +inf)")  # WholeR1
    -inf
    >>> infimum("{-10}")  # SingleValueR1
    -10
    >>> infimum("[-10, 10]")  # IntervalR1
    -10
    >>> infimum("(-10, 10)")  # IntervalR1
    -10
    >>> infimum("{0, 10, 20}")  # DisjointR1
    0
    """
    subset = Future.convert(subset)
    if isinstance(subset, EmptyR1):
        return None
    if isinstance(subset, WholeR1):
        return default.NEGINF
    if isinstance(subset, SingleValueR1):
        return subset.internal
    if isinstance(subset, IntervalR1):
        return subset[0]
    if isinstance(subset, DisjointR1):
        return min(map(infimum, subset))
    raise NotExpectedError(f"Received {type(subset)}: {subset}")


def minimum(subset: SubSetR1) -> Union[Real, None]:
    """
    Computes the minimum of the SubSetR1

    Parameters
    ----------
    subset: SubSetR1
        The subset to get the minimum

    Return
    ------
    Real | None
        The minimum value or None

    Example
    -------
    >>> minimum("{}")  # EmptyR1
    None
    >>> minimum("(-inf, +inf)")  # WholeR1
    None
    >>> minimum("{-10}")  # SingleValueR1
    -10
    >>> minimum("[-10, 10]")  # IntervalR1
    -10
    >>> minimum("(-10, 10)")  # IntervalR1
    None
    >>> minimum("{0, 10, 20}")  # DisjointR1
    0
    """
    subset = Future.convert(subset)
    if isinstance(subset, (EmptyR1, WholeR1)):
        return None
    if isinstance(subset, SingleValueR1):
        return subset.internal
    if isinstance(subset, IntervalR1):
        return (
            subset[0]
            if (default.isfinite(subset[0]) and subset.closed_left)
            else None
        )
    if isinstance(subset, DisjointR1):
        infval = default.POSINF
        global_minval = default.POSINF
        for sub in subset:
            infval = min(infval, infimum(sub))
            minval = minimum(sub)
            if minval is not None:
                global_minval = min(global_minval, minval)
        return infval if (global_minval == infval) else None
    raise NotExpectedError(f"Received {type(subset)}: {subset}")


def maximum(subset: SubSetR1) -> Union[Real, None]:
    """
    Computes the maximum of the SubSetR1

    Parameters
    ----------
    subset: SubSetR1
        The subset to get the maximum

    Return
    ------
    Real | None
        The maximum value of the subset

    Example
    -------
    >>> maximum("{}")  # EmptyR1
    None
    >>> maximum("(-inf, +inf)")  # WholeR1
    None
    >>> maximum("{-10}")  # SingleValueR1
    -10
    >>> maximum("[-10, 10]")  # IntervalR1
    10
    >>> maximum("(-10, 10)")  # IntervalR1
    None
    >>> maximum("{0, 10, 20}")  # DisjointR1
    20
    """
    subset = Future.convert(subset)
    if isinstance(subset, (EmptyR1, WholeR1)):
        return None
    if isinstance(subset, SingleValueR1):
        return subset.internal
    if isinstance(subset, IntervalR1):
        return (
            subset[1]
            if (default.isfinite(subset[1]) and subset.closed_right)
            else None
        )
    if isinstance(subset, DisjointR1):
        supval = default.NEGINF
        global_maxval = default.NEGINF
        for sub in subset:
            supval = max(supval, supremum(sub))
            maxval = maximum(sub)
            if maxval is not None:
                global_maxval = max(global_maxval, maxval)
        return maxval if (global_maxval == supval) else None
    raise NotExpectedError(f"Received {type(subset)}: {subset}")


def supremum(subset: SubSetR1) -> Union[Real, None]:
    """
    Computes the supremum of the SubSetR1

    Parameters
    ----------
    subset: SubSetR1
        The subset to get the supremum

    Return
    ------
    Real | None
        The supremum value, or None if receives EmptyR1

    Example
    -------
    >>> supremum("{}")  # EmptyR1
    None
    >>> supremum("(-inf, +inf)")  # WholeR1
    +inf
    >>> supremum("{-10}")  # SingleValueR1
    -10
    >>> supremum("[-10, 10]")  # IntervalR1
    10
    >>> supremum("(-10, 10)")  # IntervalR1
    10
    >>> supremum("{0, 10, 20}")  # DisjointR1
    20
    """
    subset = Future.convert(subset)
    if isinstance(subset, EmptyR1):
        return None
    if isinstance(subset, WholeR1):
        return default.POSINF
    if isinstance(subset, SingleValueR1):
        return subset.internal
    if isinstance(subset, IntervalR1):
        return subset[1]
    if isinstance(subset, DisjointR1):
        return max(map(supremum, subset))
    raise NotExpectedError(f"Received {type(subset)}: {subset}")
