"""Defines containers, or also named Lazy Evaluators"""

from __future__ import annotations

from copy import copy
from typing import Any, Iterable, Type, Union

from ..loggers import debug
from ..tools import Is
from .base import EmptyShape, SubSetR2, WholeShape


class LazyNot(SubSetR2):
    """A Lazy evaluator that stores the complementar of given subset"""

    def __init__(self, subset: SubSetR2):
        if not Is.instance(subset, SubSetR2):
            raise TypeError
        if Is.instance(subset, (EmptyShape, WholeShape, LazyNot)):
            raise TypeError
        self.__internal = subset

    def __copy__(self) -> LazyOr:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> LazyOr:
        return LazyNot(copy(self.__internal))

    def __invert__(self) -> SubSetR2:
        return self.__internal

    def __and__(
        self, other: Union[SubSetR2, LazyNot, LazyAnd, LazyOr]
    ) -> SubSetR2:
        return recipe_and((self, other))

    def __or__(
        self, other: Union[SubSetR2, LazyNot, LazyAnd, LazyOr]
    ) -> SubSetR2:
        return recipe_or((self, other))

    def __str__(self):
        return f"NOT[{str(self.__internal)}]"

    def __repr__(self):
        return f"NOT[{repr(self.__internal)}]"

    def __hash__(self):
        return -hash(self.__internal)

    def move(self, vector):
        self.__internal.move(vector)
        return self

    def scale(self, amount):
        self.__internal.scale(amount)
        return self

    def rotate(self, angle):
        self.__internal.rotate(angle)
        return self


class LazyAnd(SubSetR2):
    """A Lazy evaluator that stores the intersection of given subsets"""

    def __init__(self, subsets: Iterable[SubSetR2]):
        subsets = frozenset(subsets)
        if not all(Is.instance(sub, SubSetR2) for sub in subsets):
            raise TypeError
        if any(
            Is.instance(sub, (EmptyShape, WholeShape, LazyAnd))
            for sub in subsets
        ):
            raise TypeError
        self.__subsets = subsets

    def __copy__(self) -> LazyOr:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> LazyOr:
        return LazyAnd(map(copy, self))

    def __iter__(self) -> Iterable[SubSetR2]:
        yield from self.__subsets

    def __len__(self) -> int:
        return len(self.__subsets)

    def __invert__(self) -> SubSetR2:
        return recipe_not(self)

    def __and__(
        self, other: Union[SubSetR2, LazyNot, LazyAnd, LazyOr]
    ) -> SubSetR2:
        return recipe_and((self, other))

    def __or__(
        self, other: Union[SubSetR2, LazyNot, LazyAnd, LazyOr]
    ) -> SubSetR2:
        return recipe_or((self, other))

    def __str__(self):
        return f"AND[{str(self.__subsets)}]"

    def __repr__(self):
        return f"AND[{repr(self.__subsets)}]"

    def __hash__(self):
        return hash(tuple(map(hash, self)))

    def move(self, vector):
        for subset in self:
            subset.move(vector)
        return self

    def scale(self, amount):
        for subset in self:
            subset.scale(amount)
        return self

    def rotate(self, angle):
        for subset in self:
            subset.rotate(angle)
        return self


class LazyOr(SubSetR2):
    """A Lazy evaluator that stores the union of given subsets"""

    def __init__(self, subsets: Iterable[SubSetR2]):
        subsets = frozenset(subsets)
        if not all(Is.instance(sub, SubSetR2) for sub in subsets):
            raise TypeError
        if any(
            Is.instance(sub, (EmptyShape, WholeShape, LazyOr))
            for sub in subsets
        ):
            raise TypeError
        self.__subsets = subsets

    def __copy__(self) -> LazyOr:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> LazyOr:
        return LazyOr(map(copy, self))

    def __iter__(self) -> Iterable[SubSetR2]:
        yield from self.__subsets

    def __len__(self) -> int:
        return len(self.__subsets)

    def __invert__(self) -> SubSetR2:
        return recipe_not(self)

    def __and__(
        self, other: Union[SubSetR2, LazyNot, LazyAnd, LazyOr]
    ) -> SubSetR2:
        return recipe_and((self, other))

    def __or__(
        self, other: Union[SubSetR2, LazyNot, LazyAnd, LazyOr]
    ) -> SubSetR2:
        return recipe_or((self, other))

    def __str__(self):
        return f"OR[{str(self.__subsets)}]"

    def __repr__(self):
        return f"OR[{repr(self.__subsets)}]"

    def __hash__(self):
        return hash(tuple(map(hash, self)))

    def move(self, vector):
        for subset in self:
            subset.move(vector)
        return self

    def scale(self, amount):
        for subset in self:
            subset.scale(amount)
        return self

    def rotate(self, angle):
        for subset in self:
            subset.rotate(angle)
        return self


def flatten_container(
    objects: Iterable[Any], classe: Type[Union[LazyOr, LazyAnd]]
) -> Iterable[Any]:
    """Transforms a list of lists into a single list"""
    for subobj in objects:
        if Is.instance(subobj, classe):
            yield from flatten_container(subobj, classe)
        else:
            yield subobj


@debug("shapepy.bool2d.contain")
def recipe_not(subset: SubSetR2) -> SubSetR2:
    """Gives the complementar of the given subset"""
    if Is.instance(subset, (EmptyShape, WholeShape, LazyNot)):
        return -subset
    return LazyNot(subset)


@debug("shapepy.bool2d.contain")
def recipe_and(subsets: Iterable[SubSetR2]) -> SubSetR2:
    """Gives the complementar of the given subset"""
    subsets = tuple(subsets)
    subsets = flatten_container(subsets, LazyAnd)
    subsets = frozenset(s for s in subsets if not Is.instance(s, WholeShape))
    if len(subsets) == 0:
        return WholeShape()
    if any(Is.instance(s, EmptyShape) for s in subsets):
        return EmptyShape()
    return LazyAnd(subsets) if len(subsets) > 1 else tuple(subsets)[0]


@debug("shapepy.bool2d.contain")
def recipe_or(subsets: Iterable[SubSetR2]) -> SubSetR2:
    """Gives the complementar of the given subset"""
    subsets = tuple(subsets)
    subsets = flatten_container(subsets, LazyOr)
    subsets = frozenset(s for s in subsets if not Is.instance(s, EmptyShape))
    if len(subsets) == 0:
        return EmptyShape()
    if any(Is.instance(s, WholeShape) for s in subsets):
        return WholeShape()
    return LazyOr(subsets) if len(subsets) > 1 else tuple(subsets)[0]


@debug("shapepy.bool2d.contain")
def expand_morgans(subset: SubSetR2) -> SubSetR2:
    """Expands the given subset by using De Morgan's laws

    This function is used to simplifies the `Lazy` class.
    For example, for any subset:

    Example
    -------
    >>> other = LazyOr((subset, LazyNot(subset)))
    >>> expand_morgans(other)
    WholeShape
    >>> other = LazyAnd((subset, LazyNot(subset)))
    >>> expand_morgans(other)
    EmptyShape
    """
    if not Is.instance(subset, (LazyAnd, LazyNot, LazyOr)):
        return subset
    if Is.instance(subset, LazyNot):
        if not Is.instance(~subset, (LazyAnd, LazyOr)):
            return subset
    return subset
