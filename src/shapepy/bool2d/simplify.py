"""
Defines the function 'simplify' that is used to simplify a boolean
expression of the planar SubSetR2 instances
"""

from typing import Iterable

from .base import EmptyR2, SubSetR2
from .bool2d import intersect
from .container import ContainerAnd, ContainerNot, ContainerOr, expand
from .singles import PointR2


def simplify(subset: SubSetR2) -> SubSetR2:
    """
    Simplifies the SubSetR2 containers.

    This function doesn't create a copy.

    Parameters
    ----------
    subset: SubSetR2
        The subset to be simplified

    Return
    ------
    SubSetR2
        The simplified subset
    """
    subset = expand(subset)
    if isinstance(subset, ContainerNot):
        return subset
    if not isinstance(subset, (ContainerAnd, ContainerOr)):
        return subset
    isunion = isinstance(subset, ContainerOr)
    if isunion:
        subset = expand(~subset)
    subset = intersect(*map(simplify, subset))
    if isinstance(subset, ContainerAnd):
        subset = simplify_intersection(subset)
    return expand(~subset) if isunion else expand(subset)


def simplify_intersection(subsets: Iterable[SubSetR2]) -> SubSetR2:
    """
    Simplify the intersection of the given subsets
    """
    subsets = frozenset(subsets)
    for sub in subsets:
        if isinstance(sub, PointR2):
            for subj in subsets:
                if sub not in subj:
                    return EmptyR2()
            return sub
    return intersect(*subsets)
