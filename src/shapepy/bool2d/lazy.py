"""Defines containers, or also named Lazy Evaluators"""

from __future__ import annotations

from copy import copy
from typing import Iterable, Iterator

from ..loggers import debug
from ..tools import Is
from .base import EmptyShape, SubSetR2, WholeShape
from .density import intersect_densities


class RecipeLazy:
    """Contains static methods that gives lazy recipes"""

    @staticmethod
    @debug("shapepy.bool2d.lazy")
    def invert(subset: SubSetR2) -> SubSetR2:
        """Gives the complementar of the given subset"""
        if Is.instance(subset, (EmptyShape, WholeShape)):
            return -subset
        return RecipeLazy.nand({subset})

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
        return RecipeLazy.invert(RecipeLazy.nand(subsets))

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
        return RecipeLazy.nand((RecipeLazy.nand({sub}) for sub in subsets))

    @staticmethod
    @debug("shapepy.bool2d.contain")
    def nand(subsets: Iterable[SubSetR2]) -> SubSetR2:
        """Gives the exclusive and of the given subsets
        NAND[A, B, C] = NOT[AND[A, B, C]]
        """
        subsets = frozenset(subsets)
        return LazyNand(subsets)

    @staticmethod
    @debug("shapepy.bool2d.contain")
    def xor(subsets: Iterable[SubSetR2]) -> SubSetR2:
        """Gives the exclusive or of the given subsets
        NAND[A, B, C] = NOT[AND[A, B, C]]
        """
        subsets = frozenset(subsets)
        if len(subsets) > 2:
            raise NotImplementedError
        aset, bset = tuple(subsets)
        cset = RecipeLazy.nand({aset, bset})
        dset = RecipeLazy.nand({aset, cset})
        eset = RecipeLazy.nand({bset, cset})
        return RecipeLazy.nand({dset, eset})


class LazyNand(SubSetR2):
    """A Lazy evaluator that stores the complementar of given subset"""

    def __init__(self, subsets: Iterable[SubSetR2]):
        subsets = frozenset(subsets)
        if any(Is.instance(sub, (EmptyShape, WholeShape)) for sub in subsets):
            raise TypeError("Invalid typos")
        self.__subsets = subsets

    def __copy__(self) -> LazyNand:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> LazyNand:
        return LazyNand(map(copy, self))

    def __iter__(self) -> Iterator[SubSetR2]:
        yield from self.__subsets

    def __len__(self) -> int:
        return len(self.__subsets)

    def __str__(self):
        return f"NAND[{str(set(self.__subsets))}]"

    def __repr__(self):
        return f"NOT[{repr(set(self.__subsets))}]"

    def __hash__(self):
        return hash(tuple(self.__subsets))

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
        return ~intersect_densities(densities)


def is_lazy(subset: SubSetR2) -> bool:
    """Tells if the given subset is a Lazy evaluated instance"""
    return Is.instance(subset, LazyNand)


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
    return subset
