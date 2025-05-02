"""
Define somes functions that converts some basic objects to SubSetR2 instances

The easier example is from string:
* "{}" represents a empty set, so returns the EmptyR2 instance
* "{(-1, 1)}" represents a point, returns SinglePointR2 instance
"""

from typing import Any, Dict, Set

from .base import EmptyR2, SubSetR2


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
    if isinstance(obj, SubSetR2):
        return obj
    if isinstance(obj, str):
        return from_str(obj)
    if isinstance(obj, set):
        return from_set(obj)
    if isinstance(obj, dict):
        return from_dict(obj)
    raise NotImplementedError(f"Unsupported type {type(obj)}")


def from_str(obj: str) -> SubSetR2:
    """
    Converts a string to a SubSetR2 instance
    """
    if obj == r"{}":
        return EmptyR2()
    raise NotImplementedError(str(obj))


def from_set(obj: Set) -> SubSetR2:
    """
    Converts a string to a SubSetR2 instance
    """
    if len(obj) == 0:
        return EmptyR2()
    raise NotImplementedError(str(obj))


def from_dict(obj: Dict) -> SubSetR2:
    """
    Converts a string to a SubSetR2 instance
    """
    if len(obj.keys()) == 0:
        return EmptyR2()
    raise NotImplementedError(str(obj))
