"""
Defines the functions that computes the boolean operations
between the SubSetR2 instances
"""

from __future__ import annotations

from .base import SubSetR2


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError
