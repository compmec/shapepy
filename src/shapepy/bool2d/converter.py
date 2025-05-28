"""
Define somes functions that converts some basic objects to SubSetR2 instances

The easier example is from string:
* "{}" represents a empty set, so returns the EmptyR2 instance
* "{(-1, 1)}" represents a point, returns PointR2 instance
"""

import re
from typing import Any, Dict, Iterable, Set, Tuple

from .. import geometry
from ..geometry.point import str2point
from .base import EmptyR2, Future, SubSetR2
from .singles import PointR2


def from_any(obj: Any) -> SubSetR2:
    """
    Converts an arbitrary object into a SubSetR2 instance.
    If it's already a SubSetR2 instance, returns the object

    Example
    -------
    >>> from_any("{}")
    {}
    >>> from_any("(-inf, +inf)")
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
    if isinstance(obj, tuple):
        return from_tuple(obj)
    raise NotImplementedError(f"Unsupported type {type(obj)}: {obj}")


def from_str(text: str) -> SubSetR2:
    """
    Converts a string to a SubSetR2 instance
    """
    if not isinstance(text, str):
        raise TypeError
    text = text.strip()
    if text == r"{}":
        return EmptyR2()
    # Check if exists OR[...], AND[...] or NOT[...]
    pattern = r"([ANDORT]+)\[(.+)\]"
    solution = re.findall(pattern, text)
    if solution:
        if len(solution) != 1:
            raise ValueError(f"Invalid conversion from: '{text}'")
        key, middle = solution[0]
        if key == "NOT":
            return Future.invert(from_str(middle))
        internals = map(from_str, smart_divide(middle))
        if key == "AND":
            return Future.intersect(*internals)
        if key == "OR":
            return Future.unite(*internals)
        raise ValueError(f"Invalid key {key}")
    if "[" in text or "]" in text:
        raise ValueError(f"Invalid string '{text}'")
    if text[0] == "{" and text[-1] == "}":
        internals = map(from_str, smart_divide(text[1:-1]))
        return Future.unite(*internals)
    if text[0] == "(" and text[-1] == ")":
        point = str2point(text)
        return PointR2(point)
    raise ValueError(f"Invalid string '{text}'")


def from_set(obj: Set) -> SubSetR2:
    """
    Converts a string to a SubSetR2 instance
    """
    return Future.unite(*map(from_any, obj))


def from_dict(obj: Dict) -> SubSetR2:
    """
    Converts a string to a SubSetR2 instance
    """
    if len(obj.keys()) == 0:
        return EmptyR2()
    raise ValueError(str(obj))


def from_tuple(obj: Tuple) -> SubSetR2:
    """
    Converts a tuple to a SubSetR2 instance
    """
    if len(obj) != 2:
        raise ValueError("Only tuples of length 2 are permited")
    point = geometry.cartesian(obj[0], obj[1])
    return PointR2(point)


def smart_divide(text: str) -> Iterable[str]:
    """
    Divides a string using the divisor ',' and
    based on the quantity of the chars '[]'

    Example
    -------
    >>> text = "NOT[{(-10, 10)}], NOT[{(10, -10)}]"
    >>> tuple(smart_divide(text))
    ("NOT[{(-10, 10)}]", "NOT[{(10, -10)}]")
    """
    pairs = ("[]", "()", r"{}")
    retorno = ""
    for subtext in text.split(","):
        if retorno != "":
            retorno += ","
        retorno += subtext
        for left, righ in pairs:
            if retorno.count(left) != retorno.count(righ):
                break
        else:
            yield retorno.strip()
            retorno = ""
    if retorno != "":
        yield retorno.strip()
