"""Defines containers, or also named Lazy Evaluators"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Iterable, Iterator, Union

from ..boolalg.simplify import simplify_tree
from ..boolalg.tree import (
    BoolTree,
    Operators,
    false_tree,
    items2tree,
    true_tree,
)
from ..loggers import debug
from ..tools import Is, NotExpectedError
from .base import EmptyShape, SubSetR2, WholeShape
from .density import intersect_densities, unite_densities


def subset2tree(subset: SubSetR2) -> Union[SubSetR2, BoolTree]:
    """Converts a subset into a tree equivalent"""
    if Is.instance(subset, EmptyShape):
        return false_tree()
    if Is.instance(subset, WholeShape):
        return true_tree()
    if Is.instance(subset, LazyNot):
        return items2tree((subset2tree(-subset),), Operators.NOT)
    if Is.instance(subset, LazyAnd):
        return items2tree(map(subset2tree, subset), Operators.AND)
    if Is.instance(subset, LazyOr):
        return items2tree(map(subset2tree, subset), Operators.OR)
    return subset


def tree2subset(tree: Union[SubSetR2, BoolTree]) -> SubSetR2:
    """Converts a tree into the subset equivalent"""
    if not Is.instance(tree, BoolTree):
        return tree
    if len(tree) == 0:
        return WholeShape() if tree.operator == Operators.AND else EmptyShape()
    if tree.operator == Operators.NOT:
        return LazyNot(tree2subset(tuple(tree)[0]))
    if tree.operator == Operators.AND:
        return LazyAnd(map(tree2subset, tree))
    if tree.operator == Operators.OR:
        return LazyOr(map(tree2subset, tree))
    raise NotExpectedError(f"Operator {tree.operator}")


@debug("shapepy.bool2d.lazy")
def operate(subsets: Iterable[SubSetR2], operator: Operators) -> SubSetR2:
    """Computes the operation of the items, such as union, intersection"""
    tree = items2tree(map(subset2tree, subsets), operator)
    return tree2subset(simplify_tree(tree))


class RecipeLazy:
    """Contains static methods that gives lazy recipes"""

    @staticmethod
    @debug("shapepy.bool2d.lazy")
    def invert(subset: SubSetR2) -> SubSetR2:
        """Gives the complementar of the given subset"""
        return operate((subset,), Operators.NOT)

    @staticmethod
    @debug("shapepy.bool2d.lazy")
    def intersect(subsets: Iterable[SubSetR2]) -> SubSetR2:
        """Gives the recipe for the intersection of given subsets"""
        return operate(subsets, Operators.AND)

    @staticmethod
    @debug("shapepy.bool2d.contain")
    def unite(subsets: Iterable[SubSetR2]) -> SubSetR2:
        """Gives the recipe for the union of given subsets"""
        return operate(subsets, Operators.OR)

    @staticmethod
    @debug("shapepy.bool2d.contain")
    def xor(subsets: Iterable[SubSetR2]) -> SubSetR2:
        """Gives the exclusive or of the given subsets"""
        return operate(subsets, Operators.XOR)


class LazyNot(SubSetR2):
    """A Lazy evaluator that stores the complementar of given subset"""

    def __init__(self, subset: SubSetR2):
        if not Is.instance(subset, SubSetR2):
            raise TypeError(f"Invalid typo: {type(subset)}: {subset}")
        if Is.instance(subset, LazyNot):
            raise TypeError("Subset cannot be LazyNot")
        self.__internal = subset

    @debug("shapepy.bool2d.lazy")
    def __hash__(self):
        return -hash(self.__internal)

    def __str__(self):
        return f"NOT[{str(self.__internal)}]"

    def __repr__(self):
        return f"NOT[{repr(self.__internal)}]"

    def __invert__(self):
        return self.__internal

    def __neg__(self):
        return self.__internal

    def __copy__(self):
        return LazyNot(self.__internal)

    def __deepcopy__(self, memo):
        return LazyNot(deepcopy(self.__internal))

    def __eq__(self, other):
        return (
            Is.instance(other, LazyNot)
            and hash(self) == hash(other)
            and (~self == ~other)
        )

    def move(self, vector):
        return LazyNot(self.__internal.move(vector))

    def scale(self, amount):
        return LazyNot(self.__internal.scale(amount))

    def rotate(self, angle):
        return LazyNot(self.__internal.rotate(angle))

    @lru_cache(maxsize=1)
    @debug("shapepy.bool2d.base")
    def density(self, center):
        return ~(self.__internal.density(center))


class LazyOr(SubSetR2):
    """A Lazy evaluator that stores the union of given subsets"""

    def __init__(self, subsets: Iterable[SubSetR2]):
        subsets = (s for s in subsets if not Is.instance(s, EmptyShape))
        subsets = frozenset(subsets)
        if any(Is.instance(s, LazyOr) for s in subsets):
            raise TypeError
        if any(Is.instance(s, WholeShape) for s in subsets):
            subsets = frozenset()
        self.__subsets = subsets

    def __iter__(self) -> Iterator[SubSetR2]:
        yield from self.__subsets

    def __str__(self):
        return f"OR[{', '.join(map(str, self))}]"

    def __repr__(self):
        return f"OR[{', '.join(map(repr, self))}]"

    @debug("shapepy.bool2d.lazy")
    def __hash__(self):
        return hash(tuple(map(hash, self.__subsets)))

    def __copy__(self):
        return LazyOr(self.__subsets)

    def __deepcopy__(self, memo):
        return LazyOr(map(deepcopy, self))

    def __eq__(self, other):
        return (
            Is.instance(other, LazyOr)
            and hash(self) == hash(other)
            and frozenset(self) == frozenset(other)
        )

    def move(self, vector):
        return LazyOr(sub.move(vector) for sub in self)

    def scale(self, amount):
        return LazyOr(sub.scale(amount) for sub in self)

    def rotate(self, angle):
        return LazyOr(sub.rotate(angle) for sub in self)

    @lru_cache(maxsize=1)
    @debug("shapepy.bool2d.lazy")
    def density(self, center):
        return unite_densities(sub.density(center) for sub in self)


class LazyAnd(SubSetR2):
    """A Lazy evaluator that stores the union of given subsets"""

    def __init__(self, subsets: Iterable[SubSetR2]):
        subsets = (s for s in subsets if not Is.instance(s, EmptyShape))
        subsets = frozenset(subsets)
        if any(Is.instance(s, LazyAnd) for s in subsets):
            raise TypeError
        if any(Is.instance(s, WholeShape) for s in subsets):
            subsets = frozenset()
        self.__subsets = subsets

    def __iter__(self) -> Iterator[SubSetR2]:
        yield from self.__subsets

    def __str__(self):
        return f"AND[{', '.join(map(str, self))}]"

    def __repr__(self):
        return f"AND[{', '.join(map(repr, self))}]"

    @debug("shapepy.bool2d.lazy")
    def __hash__(self):
        return -hash(tuple(-hash(sub) for sub in self))

    def __copy__(self):
        return LazyAnd(self.__subsets)

    def __deepcopy__(self, memo):
        return LazyAnd(map(deepcopy, self))

    def __eq__(self, other):
        return (
            Is.instance(other, LazyAnd)
            and hash(self) == hash(other)
            and frozenset(self) == frozenset(other)
        )

    def move(self, vector):
        return LazyAnd(sub.move(vector) for sub in self)

    def scale(self, amount):
        return LazyAnd(sub.scale(amount) for sub in self)

    def rotate(self, angle):
        return LazyAnd(sub.rotate(angle) for sub in self)

    @lru_cache(maxsize=1)
    @debug("shapepy.bool2d.lazy")
    def density(self, center):
        return intersect_densities(sub.density(center) for sub in self)
