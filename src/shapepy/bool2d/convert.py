"""
Functions to convert from typical data types into SubSetR2
"""

from ..geometry.base import IGeometricCurve
from ..tools import Is, To
from .base import SubSetR2
from .curve import SingleCurve
from .point import SinglePoint


def from_any(subset: SubSetR2) -> SubSetR2:
    """
    Converts an object into a SubSetR2
    """
    if Is.instance(subset, SubSetR2):
        return subset
    if Is.instance(subset, IGeometricCurve):
        return SingleCurve(subset)
    return SinglePoint(To.point(subset))
