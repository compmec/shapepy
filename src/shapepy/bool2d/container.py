"""
Defines the auxiliar containers used when doing the standard
boolean operations, like the union, intersection and inversion
of the base types.

These containers may store the datas in a lazy format:
The intersection of square and a circle can be represented as
a recipe of intersection, or by a single curve if needed.
"""

from .base import SubSetR2


def expand(subset: SubSetR2) -> SubSetR2:
    """
    Expands the containers using De Morgan's laws.

    The form of the final object is like OR[AND[NOT[OBJ]]]

    If a non-container is given, returns the same instance

    Parameters
    ----------
    subset: SubSetR2
        The container to be expanded

    Return
    ------
    SubSetR2
        The expanded subset
    """
    return subset
