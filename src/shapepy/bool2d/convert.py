"""
Functions to convert from typical data types into SubSetR2
"""

from ..tools import Is
from .base import SubSetR2


def from_any(subset: SubSetR2) -> SubSetR2:
    """
    Converts an object into a SubSetR2
    """
    if not Is.instance(subset, SubSetR2):
        raise TypeError
    return subset
