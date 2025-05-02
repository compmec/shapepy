"""
Define somes functions that converts some basic objects to SubSetR2 instances

The easier example is from string:
* "{}" represents a empty set, so returns the EmptyR2 instance
* "{(-1, 1)}" represents a point, returns SinglePointR2 instance
"""

from typing import Any

from .base import SubSetR2


def from_any(obj: Any) -> SubSetR2:
    """
    Converts an arbitrary object into a SubSetR2 instance.
    If it's already a SubSetR2 instance, returns the object

    Example
    -------
    >>> ConverterR1.from_any("{}")
    {}
    >>> ConverterR1.from_any("(-inf, +inf)")
    (-inf, +inf)
    """
    return obj
