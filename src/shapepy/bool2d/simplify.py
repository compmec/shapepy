"""
Defines the function 'simplify' that is used to simplify a boolean
expression of the planar SubSetR2 instances
"""

from .base import SubSetR2
from .container import ContainerAnd, ContainerNot, ContainerOr, expand


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
    return subset.__class__(map(simplify, subset))
