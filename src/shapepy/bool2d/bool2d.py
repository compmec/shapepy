"""
Defines the functions that computes the boolean operations
between the SubSetR2 instances
"""

from __future__ import annotations

from .base import EmptyR2, SubSetR2, WholeR2
from .container import ContainerAnd, ContainerNot, ContainerOr
from .converter import from_any
from .singles import SinglePointR2


def unite(*subsets: SubSetR2) -> SubSetR2:
    """
    Computes the union of given subsets

    Parameters
    ----------
    subsets: SubSetR2
        The subsets to be united

    Return
    ------
    SubSetR2
        The united subset
    """
    subsets = map(from_any, subsets)
    subsets = frozenset(sub for sub in subsets if not isinstance(sub, EmptyR2))
    if len(subsets) == 0:
        return EmptyR2()
    if len(subsets) == 1:
        return tuple(subsets)[0]
    if any(isinstance(subset, WholeR2) for subset in subsets):
        return WholeR2()
    return ContainerOr(subsets)


def intersect(*subsets: SubSetR2) -> SubSetR2:
    """
    Computes the intersection of given subsets

    Parameters
    ----------
    subsets: SubSetR2
        The subsets to be intersected

    Return
    ------
    SubSetR2
        The intersection subset
    """
    subsets = map(from_any, subsets)
    subsets = frozenset(sub for sub in subsets if not isinstance(sub, WholeR2))
    if len(subsets) == 0:
        return WholeR2()
    if len(subsets) == 1:
        return tuple(subsets)[0]
    if any(isinstance(subset, EmptyR2) for subset in subsets):
        return EmptyR2()
    return ContainerAnd(subsets)


def invert(subset: SubSetR2) -> SubSetR2:
    """
    Inverts the given subset

    Parameters
    ----------
    subset: SubSetR2
        The subset to be interveted

    Return
    ------
    SubSetR2
        The inverted subset
    """
    if isinstance(subset, (EmptyR2, WholeR2, ContainerNot)):
        return ~subset
    return ContainerNot(subset)


def contains(subseta: SubSetR2, subsetb: SubSetR2) -> bool:
    """
    Checks if the subset B is contained by the subset A

    Parameters
    ----------
    subseta: SubSetR2
        The subset A to check if (B in A)
    subsetb: SubSetR2
        The subset B to check if (B in A)

    Return
    ------
    bool
        The result of (B in A)

    Example
    -------
    >>> contains(EmptyR2(), WholeR2())
    False
    >>> contains(WholeR2(), EmptyR2())
    True
    """
    subseta = from_any(subseta)
    subsetb = from_any(subsetb)
    if isinstance(subseta, (EmptyR2, WholeR2, ContainerAnd, SinglePointR2)):
        return subsetb in subseta
    if isinstance(subsetb, ContainerOr):
        return all(contains(subseta, sub) for sub in subsetb)
    if isinstance(subseta, ContainerNot):
        if isinstance(subsetb, ContainerNot):
            return contains(~subsetb, ~subseta)
        if isinstance(~subseta, SinglePointR2):
            return not contains(subsetb, ~subseta)
    raise NotImplementedError(f"Types {type(subseta)} and {type(subsetb)}")
