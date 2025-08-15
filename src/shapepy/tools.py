"""
Useful functions to test objects and transform them,
logging, errors, debugging, etc.
"""

from __future__ import annotations

import types
from functools import wraps
from typing import Any, Iterable, Tuple

import numpy as np


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

    @staticmethod
    def callable(obj: Any) -> bool:
        """
        Tells if the object is callable
        """
        return hasattr(obj, "__call__")


# pylint: disable=too-few-public-methods
class To:
    """
    Contains static methods to transform objects to some type numbers
    """

    float = float


# Creates a decorator to vectorize functions that receives floats
# Or an array of floats depending on the dimension
def vectorize(position: int = 0, dimension: int = 0):
    """
    Decorator to vectorize functions that gives the same type of container
    as received from input. Meaning: tuple -> tuple, list -> list, ...

    The dimension parameter is to decide the quantity of floats per call
    * dimension = 0 -> float
    * dimension = 1 -> [float]
    * dimension = 2 -> [float, float]
    ...
    """

    def decorator(func):
        conversion = {
            types.GeneratorType: tuple,  # No conversion
            range: tuple,  # No conversion
        }

        @wraps(func)
        def wrapper(*args, **kwargs):
            param = args[position]
            if dimension == 0:
                if Is.real(param):
                    float(param)
                    return func(*args, **kwargs)

                result = (
                    func(*args[:position], p, *args[position + 1 :], **kwargs)
                    for p in param
                )
                result = tuple(result)
                for key, tipo in conversion.items():
                    if isinstance(param, key):
                        if tipo is not None:
                            result = tipo(result)
                        return result
                if isinstance(param, np.ndarray):
                    result = np.array(result, dtype=param.dtype)
                else:
                    result = param.__class__(result)
                return result
            raise NotImplementedError

        return wrapper

    return decorator


def reverse(objs: Iterable[Any]) -> Iterable[Any]:
    """Reverts the list/tuple"""
    return tuple(objs)[::-1]


def pairs(objs: Iterable[Any]) -> Iterable[Tuple[Any, Any]]:
    """Gives pairs of the objects in sequence

    Example
    -------
    >>> A = [0, 1, 2, 3]
    >>> list(pairs(A))
    [(0, 1), (1, 2), (2, 3), (3, 0)]
    """
    objs = tuple(objs)
    if len(objs) <= 1:
        raise ValueError(f"objs = {objs}")
    if len(objs) > 1:
        yield from zip(objs, objs[1:])
        yield (objs[-1], objs[0])


class NotExpectedError(Exception):
    """Raised when arrives in a section that were not expected"""
