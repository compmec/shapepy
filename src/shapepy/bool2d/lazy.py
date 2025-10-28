"""Defines containers, or also named Lazy Evaluators"""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Iterator

from ..loggers import debug
from ..tools import Is
from .base import EmptyShape, Future, SubSetR2, WholeShape
from .density import intersect_densities


class RecipeLazy:
    """Contains static methods that gives lazy recipes"""

    @staticmethod
    @debug("shapepy.bool2d.lazy")
    def invert(subset: SubSetR2) -> SubSetR2:
        """Gives the complementar of the given subset"""
        if Is.instance(subset, (EmptyShape, WholeShape)):
            return -subset
        return LazyNand({subset})

    @staticmethod
    @debug("shapepy.bool2d.lazy")
    def intersect(subsets: Iterable[SubSetR2]) -> SubSetR2:
        """Gives the recipe for the intersection of given subsets"""
        subsets = frozenset(
            s for s in subsets if not Is.instance(s, WholeShape)
        )
        if len(subsets) == 0:
            return WholeShape()
        if any(Is.instance(s, EmptyShape) for s in subsets):
            return EmptyShape()
        if len(subsets) == 1:
            return tuple(subsets)[0]
        return LazyNand({LazyNand(subsets)})

    @staticmethod
    @debug("shapepy.bool2d.contain")
    def unite(subsets: Iterable[SubSetR2]) -> SubSetR2:
        """Gives the recipe for the union of given subsets"""
        subsets = frozenset(
            s for s in subsets if not Is.instance(s, EmptyShape)
        )
        if len(subsets) == 0:
            return EmptyShape()
        if any(Is.instance(s, WholeShape) for s in subsets):
            return WholeShape()
        if len(subsets) == 1:
            return tuple(subsets)[0]
        return LazyNand(map(LazyNand, subsets))

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


class LazyNand(SubSetR2):
    """A Lazy evaluator that stores the Nand of given subsets"""

    def __init__(self, subsets: Iterable[SubSetR2]):
        subsets = map(Future.convert, subsets)
        subsets = frozenset(s for s in subsets if s is not WholeShape())
        if any(Is.instance(s, EmptyShape) for s in subsets):
            subsets = frozenset()
        self.__subsets = subsets

    def __len__(self) -> int:
        return len(self.__subsets)

    def __iter__(self) -> Iterator[SubSetR2]:
        yield from self.__subsets

    def __str__(self):
        return f"NAND[{', '.join(map(str, self))}]"

    def __repr__(self):
        return f"NAND[{', '.join(map(repr, self))}]"

    @debug("shapepy.bool2d.lazy")
    def __hash__(self):
        return hash(tuple(map(hash, self.__subsets)))

    def __copy__(self):
        return LazyNand(self.__subsets)

    def __eq__(self, other):
        return (
            Is.instance(other, LazyNand)
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
        return ~intersect_densities(sub.density(center) for sub in self)
