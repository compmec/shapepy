"""Defines useful functions"""

from numbers import Real
from typing import Union

from ..loggers import debug
from ..scalar.reals import Math
from ..tools import Is, NotExpectedError
from .base import EmptyR1, Future, SubSetR1, WholeR1
from .singles import DisjointR1, IntervalR1, SingleR1


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
    >>> infimum("{-10}")  # SingleR1
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
        return Math.NEGINF
    if isinstance(subset, SingleR1):
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
    >>> minimum("{-10}")  # SingleR1
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
    if isinstance(subset, SingleR1):
        return subset.internal
    if isinstance(subset, IntervalR1):
        return (
            subset[0]
            if (Is.finite(subset[0]) and subset.closed_left)
            else None
        )
    if isinstance(subset, DisjointR1):
        infval = Math.POSINF
        global_minval = Math.POSINF
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
    >>> maximum("{-10}")  # SingleR1
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
    if isinstance(subset, SingleR1):
        return subset.internal
    if isinstance(subset, IntervalR1):
        return (
            subset[1]
            if (Is.finite(subset[1]) and subset.closed_right)
            else None
        )
    if isinstance(subset, DisjointR1):
        supval = Math.NEGINF
        global_maxval = Math.NEGINF
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
    >>> supremum("{-10}")  # SingleR1
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
        return Math.POSINF
    if isinstance(subset, SingleR1):
        return subset.internal
    if isinstance(subset, IntervalR1):
        return subset[1]
    if isinstance(subset, DisjointR1):
        return max(map(supremum, subset))
    raise NotExpectedError(f"Received {type(subset)}: {subset}")


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
    subset = Future.convert(subset)
    if Is.instance(subset, IntervalR1):
        return subset[1] - subset[0]
    if Is.instance(subset, DisjointR1):
        return sum(map(subset_length, subset.intervals))
    return 0


def is_bounded(subset: SubSetR1) -> Real:
    """
    Tells if the given subset is limited, meaning it does not contain INF
    """
    subset = Future.convert(subset)
    return not Is.instance(subset, WholeR1) and (
        not (
            Is.instance(subset, IntervalR1)
            and not (Math.NEGINF < subset[0] and subset[1] < Math.POSINF)
        )
        and not (
            Is.instance(subset, DisjointR1)
            and not all(map(is_bounded, subset))
        )
    )


def is_continuous(subset: SubSetR1) -> Real:
    """
    Tells if the given subset is continuous, there's no gaps
    """
    return not Is.instance(Future.convert(subset), DisjointR1)
