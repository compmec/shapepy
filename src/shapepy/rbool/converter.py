"""
Module that contains functions to convert some basic types into Bool1D types

The easier example is from string:
* "{}" represents a empty set, so returns the EmptyR1 instance
* "(-inf, +inf)" represents the entire real line, returns WholeR1 instance
"""

from numbers import Real
from typing import Any, Dict, List, Set, Tuple

from ..scalar.reals import Math
from ..tools import NotExpectedError, To
from .base import EmptyR1, Future, SubSetR1, WholeR1
from .singles import IntervalR1, SingleR1, bigger, lower


# pylint: disable=too-many-return-statements
def from_any(obj: Any) -> SubSetR1:
    """
    Converts an arbitrary object into a SubSetR1 instance.
    If it's already a SubSetR1 instance, returns the object

    Example
    -------
    >>> Future.convert("{}")
    {}
    >>> Future.convert("(-inf, +inf)")
    (-inf, +inf)
    """
    if isinstance(obj, SubSetR1):
        return obj
    if isinstance(obj, Real):
        number = To.finite(obj)
        return SingleR1(number)
    if isinstance(obj, str):
        return from_str(obj)
    if isinstance(obj, dict):
        return from_dict(obj)
    if isinstance(obj, set):
        return from_set(obj)
    if isinstance(obj, tuple):
        return from_tuple(obj)
    if isinstance(obj, list):
        return from_list(obj)
    raise NotExpectedError(f"Received object {type(obj)} = {obj}")


def from_str(string: str) -> SubSetR1:
    """
    Converts a string into a SubSetR1 instance.

    Example
    -------
    >>> from_str("{}")  # EmptyR1
    {}
    >>> from_str("(-inf, +inf)")  # WholeR1
    (-inf, +inf)
    >>> from_str("{10}")  # SingleR1
    {10}
    >>> from_str("[-10, 0] U {5, 10}")  # DisjointR1
    [-10, 0] U {5, 10}
    """
    string = string.strip()
    if "U" in string:
        return Future.unite(*map(from_str, string.split("U")))
    if string[0] == "{" and string[-1] == "}":
        result = EmptyR1()
        for substr in string[1:-1].split(","):
            if not substr:  # EmptyR1 string
                continue
            finite = To.finite(substr)
            result |= SingleR1(finite)
        return result
    if string[0] in "([" and string[-1] in ")]":
        stastr, endstr = string[1:-1].split(",")
        start = To.real(stastr)
        end = To.real(endstr)
        if start == Math.NEGINF and end == Math.POSINF:
            return WholeR1()
        left = string[0] == "["
        right = string[-1] == "]"
        return IntervalR1(start, end, left, right)
    raise ValueError(f"Cannot parse '{string}' into a SubSetR1 instance")


def from_dict(dic: Dict) -> SubSetR1:
    """
    Converts a dictonary into a SubSetR1 instance

    Only accepts an empty dict, since it's the standard type of {}:

    Example
    -------
    >>> variable = {}
    >>> type(variable)
    <class 'dict'>
    >>> subset = from_dict(variable)
    >>> subset
    {}
    >>> type(subset)
    <class 'EmptyR1'>
    """
    if not isinstance(dic, dict):
        raise TypeError
    result = EmptyR1()
    if len(dic) != 0:
        raise NotExpectedError
    return result


def from_set(items: Set[object]) -> SubSetR1:
    """
    Converts a set into a SubSetR1 instance

    Example
    -------
    >>> variable = {-10, 5}
    >>> type(variable)
    <class 'set'>
    >>> subset = from_set(variable)
    >>> subset
    {-10, 5}
    >>> type(subset)
    <class 'DisjointR1'>
    """
    if not isinstance(items, set):
        raise TypeError
    result = EmptyR1()
    for item in items:
        result |= To.finite(item)
    return result


def from_tuple(pair: Tuple[object]) -> SubSetR1:
    """
    Converts a tuple of two values into a SubSetR1 instance

    It's the standard open interval, or the WholeR1

    Example
    -------
    >>> variable = (-10, 10)
    >>> type(variable)
    <class 'tuple'>
    >>> subset = from_tuple(variable)
    >>> subset
    (-10, 10)
    >>> type(subset)
    <class 'IntervalR1'>
    >>> variable = ("-inf", "inf")
    >>> subset = from_tuple(variable)
    >>> type(subset)
    <class 'WholeR1'>
    """
    if not isinstance(pair, tuple):
        raise TypeError
    if len(pair) != 2:
        raise ValueError
    sta = To.real(pair[0])
    end = To.real(pair[1])
    if sta == Math.NEGINF and end == Math.POSINF:
        return WholeR1()
    if sta == Math.NEGINF:
        return lower(end, False)
    if end == Math.POSINF:
        return bigger(sta, False)
    return IntervalR1(sta, end, False, False)


def from_list(pair: List[object]) -> SubSetR1:
    """
    Converts a list of two values into a SubSetR1 instance

    It's the standard closed interval, or the WholeR1

    Example
    -------
    >>> variable = [-10, 10]
    >>> type(variable)
    <class 'list'>
    >>> subset = from_list(variable)
    >>> subset
    [-10, 10]
    >>> type(subset)
    <class 'IntervalR1'>
    >>> variable = ["-inf", "inf"]
    >>> subset = from_list(variable)
    >>> subset
    (-inf, +inf)
    >>> type(subset)
    <class 'WholeR1'>
    """
    if not isinstance(pair, list):
        raise TypeError
    if len(pair) != 2:
        raise ValueError
    sta = To.real(pair[0])
    end = To.real(pair[1])
    if sta == Math.NEGINF and end == Math.POSINF:
        return WholeR1()
    if sta == Math.NEGINF:
        return lower(end, True)
    if end == Math.POSINF:
        return bigger(sta, True)
    return IntervalR1(sta, end, True, True)
