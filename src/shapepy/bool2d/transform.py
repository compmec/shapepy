"""
Defines the methods used to do the usual transformations,
like translating, scaling and rotating the SubSetR2 instances on the plane
"""

from numbers import Real
from typing import Tuple, Union

from ..angle import Angle
from .base import SubSetR2


def move(subset: SubSetR2, vector: Tuple[Real, Real]) -> SubSetR2:
    """
    Translates the subset on the plane, by given vector

    Parameters
    ----------
    subset: SubSetR2
        The subset to be displaced
    vector: Tuple[Real, Real]
        The coordinates (x, y) of the vector

    Return
    ------
    SubSetR2
        The translated subset, of the same type

    Example
    -------
    >>> subset = primitive.square()
    >>> move(subset, (3, 4))
    """
    raise NotImplementedError


def scale(
    subset: SubSetR2, amount: Union[Real, Tuple[Real, Real]]
) -> SubSetR2:
    """
    Scales the subset on the plane by given amount.

    * If a Real number is given, scales evenly on 'x' and 'y'
    * If a pair of Real is given, scales 'x' and 'y' by different amounts

    Parameters
    ----------
    subset: SubSetR2
        The subset to be scaled
    amount: Union[Real, Tuple[Real, Real]]
        The coordinates (x, y) of the vector

    Return
    ------
    SubSetR2
        The scaled subset, of the same type

    Example
    -------
    >>> subset = primitive.square()
    >>> scale(subset, 3)  # Area is 9 times bigger
    >>> scale(subset, (5, 2))  # Scale x by 5 times, y by 2 times
    """
    raise NotImplementedError


def rotate(subset: SubSetR2, angle: Angle) -> SubSetR2:
    """
    Rotates the subset on the clockwise direction arount the origin

    Parameters
    ----------
    subset: SubSetR2
        The subset to be rotated around the origin
    angle: Angle
        The angle to rotate

    Return
    ------
    SubSetR2
        The rotated subset, of the same type

    Example
    -------
    >>> subset = primitive.square()
    >>> angle = Angle.degrees(90)
    >>> rotate(subset, angle)
    """
    raise NotImplementedError
