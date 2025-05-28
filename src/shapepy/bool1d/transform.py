"""
Defines the methods used to do the usual transformations,
like translating, scaling and rotating the SubSetR2 instances on the plane
"""

from numbers import Real

from .. import default
from ..error import NotExpectedError
from .base import EmptyR1, Future, SubSetR1, WholeR1
from .singles import DisjointR1, IntervalR1, SingleValueR1


def move(subset: SubSetR1, amount: Real) -> SubSetR1:
    """
    Translates the subset on the the real line by given amount

    Parameters
    ----------
    subset: SubSetR1
        The subset to be displaced
    amount: Real
        The quantity to be displaced

    Return
    ------
    SubSetR1
        The translated subset, of the same type
    """
    subset = Future.convert(subset)
    amount = default.finite(amount)
    if isinstance(subset, (EmptyR1, WholeR1)):
        return subset
    if isinstance(subset, SingleValueR1):
        return SingleValueR1(subset.internal + amount)
    if isinstance(subset, IntervalR1):
        newlef = subset[0] + amount
        newrig = subset[1] + amount
        return IntervalR1(
            newlef, newrig, subset.closed_left, subset.closed_right
        )
    if isinstance(subset, DisjointR1):
        amount = default.finite(amount)
        newiterable = (move(sub, amount) for sub in subset)
        return DisjointR1(newiterable)
    raise NotExpectedError(f"Missing typo? {type(subset)}")


def scale(subset: SubSetR1, amount: Real) -> SubSetR1:
    """
    Scales the subset on the real line by given amount.

    Parameters
    ----------
    subset: SubSetR1
        The subset to be scaled
    amount: Real
        The amount to be scaled

    Return
    ------
    SubSetR1
        The scaled subset, of the same type

    Example
    -------
    >>> subset = [-2, 3]
    >>> scale(subset, 3)
    [-6, 9]
    """
    subset = Future.convert(subset)
    amount = default.finite(amount)
    if amount == 0:
        raise ValueError
    if isinstance(subset, (EmptyR1, WholeR1)):
        return subset
    if isinstance(subset, SingleValueR1):
        return SingleValueR1(subset.internal * amount)
    if isinstance(subset, IntervalR1):
        newlef = subset[0] * amount
        newrig = subset[1] * amount
        clolef = subset.closed_left
        clorig = subset.closed_right
        if amount < 0:
            newlef, newrig = newrig, newlef
            clolef, clorig = clorig, clolef
        return IntervalR1(newlef, newrig, clolef, clorig)
    if isinstance(subset, DisjointR1):
        amount = default.finite(amount)
        newiterable = (scale(sub, amount) for sub in subset)
        return DisjointR1(newiterable)
    raise NotExpectedError(f"Missing typo? {type(subset)}")
