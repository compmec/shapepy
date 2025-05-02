"""
Defines the function 'simplify' that is used to simplify a boolean
expression of the planar SubSetR2 instances
"""

from .base import SubSetR2


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
    return subset
