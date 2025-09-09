"""Defines containers, or also named Lazy Evaluators"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Iterable, Iterator, Type

from ..loggers import debug
from ..tools import Is
from .base import EmptyShape, SubSetR2, WholeShape
from .density import intersect_densities, unite_densities


class RecipeLazy:
    """Contains static methods that gives lazy recipes"""

    @staticmethod
    def flatten(subsets: Iterable[SubSetR2], typo: Type) -> Iterator[SubSetR2]:
        """Flattens the subsets"""
        for subset in subsets:
            if Is.instance(subset, typo):
                yield from subset
            else:
                yield subset

    @staticmethod
    @debug("shapepy.bool2d.lazy")
    def invert(subset: SubSetR2) -> SubSetR2:
        """Gives the complementar of the given subset"""
        if Is.instance(subset, (EmptyShape, WholeShape, LazyNot)):
            return -subset
        return LazyNot(subset)

    @staticmethod
    @debug("shapepy.bool2d.lazy")
    def intersect(subsets: Iterable[SubSetR2]) -> SubSetR2:
        """Gives the recipe for the intersection of given subsets"""
        subsets = RecipeLazy.flatten(subsets, LazyAnd)
        subsets = frozenset(
            s for s in subsets if not Is.instance(s, WholeShape)
        )
        if len(subsets) == 0:
            return WholeShape()
        if any(Is.instance(s, EmptyShape) for s in subsets):
            return EmptyShape()
        if len(subsets) == 1:
            return tuple(subsets)[0]
        return LazyAnd(subsets)

    @staticmethod
    @debug("shapepy.bool2d.contain")
    def unite(subsets: Iterable[SubSetR2]) -> SubSetR2:
        """Gives the recipe for the union of given subsets"""
        subsets = RecipeLazy.flatten(subsets, LazyOr)
        subsets = frozenset(
            s for s in subsets if not Is.instance(s, EmptyShape)
        )
        if len(subsets) == 0:
            return EmptyShape()
        if any(Is.instance(s, WholeShape) for s in subsets):
            return WholeShape()
        if len(subsets) == 1:
            return tuple(subsets)[0]
        return LazyOr(subsets)

    @staticmethod
    @debug("shapepy.bool2d.contain")
    def xor(subsets: Iterable[SubSetR2]) -> SubSetR2:
        """Gives the exclusive or of the given subsets"""
        subsets = tuple(subsets)
        dictids = dict(Counter(map(id, subsets)))
        subsets = tuple(s for s in subsets if dictids[id(s)] % 2)
        length = len(subsets)
        if length == 0:
            return EmptyShape()
        if length == 1:
            return subsets[0]
        mid = length // 2
        aset = RecipeLazy.xor(subsets[:mid])
        bset = RecipeLazy.xor(subsets[mid:])
        left = RecipeLazy.intersect((aset, RecipeLazy.invert(bset)))
        righ = RecipeLazy.intersect((RecipeLazy.invert(aset), bset))
        return RecipeLazy.unite((left, righ))


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
        self.__internal.move(vector)
        return self

    def scale(self, amount):
        self.__internal.scale(amount)
        return self

    def rotate(self, angle):
        self.__internal.rotate(angle)
        return self

    def density(self, center):
        return ~self.__internal.density(center)


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
        return f"OR[{", ".join(map(str, self))}]"

    def __repr__(self):
        return f"OR[{", ".join(map(repr, self))}]"

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

    def density(self, center):
        densities = (sub.density(center) for sub in self)
        return unite_densities(tuple(densities))


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
        return f"AND[{", ".join(map(str, self))}]"

    def __repr__(self):
        return f"AND[{", ".join(map(repr, self))}]"

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

    def density(self, center):
        densities = (sub.density(center) for sub in self)
        return intersect_densities(tuple(densities))


def is_lazy(subset: SubSetR2) -> bool:
    """Tells if the given subset is a Lazy evaluated instance"""
    return Is.instance(subset, (LazyAnd, LazyNot, LazyOr))
