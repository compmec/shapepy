"""
Useful functions to test objects and transform them,
logging, errors, debugging, etc.
"""

from __future__ import annotations

from typing import Any


class Is:
    """
    Contains functions to test the objects,
    telling if an object is a number, or it's integer, etc
    """

    instance = isinstance

    @staticmethod
    def bool(obj: Any) -> bool:
        """
        Tells if the object is a boolean
        """
        return Is.instance(obj, bool)

    @staticmethod
    def iterable(obj: Any) -> bool:
        """
        Tells if the object is iterable
        """
        try:
            iter(obj)
        except TypeError:
            return False
        return True


# pylint: disable=too-few-public-methods
class To:
    """
    Contains static methods to transform objects to some type numbers
    """

    float = float
