"""
Defines the auxiliar containers used when doing the standard
boolean operations, like the union, intersection and inversion
of the base types.

These containers may store the datas in a lazy format:
The intersection of square and a circle can be represented as
a recipe of intersection, or by a single curve if needed.
"""

from typing import Iterable

from .base import EmptyR2, SubSetR2, WholeR2


def expand(subset: SubSetR2) -> SubSetR2:
    """
    Expands the containers using De Morgan's laws.

    The form of the final object is like OR[AND[NOT[OBJ]]]

    If a non-container is given, returns the same instance

    Parameters
    ----------
    subset: SubSetR2
        The container to be expanded

    Return
    ------
    SubSetR2
        The expanded subset
    """
    if not isinstance(subset, (ContainerAnd, ContainerOr, ContainerNot)):
        return subset
    if isinstance(subset, ContainerNot):
        if isinstance(~subset, ContainerOr):
            return expand(ContainerAnd(~sub for sub in ~subset))
        if isinstance(~subset, ContainerAnd):
            return expand(ContainerOr(~sub for sub in ~subset))
        return subset
    return subset.__class__(map(expand, subset))


class ContainerNot(SubSetR2):
    """
    Defines the class that stores the complementary of a SubSetR2
    """

    def __init__(self, subset: SubSetR2):
        if not isinstance(subset, SubSetR2):
            raise TypeError(f"Must be SubSetR2 instance, not {type(subset)}")
        if isinstance(subset, (EmptyR2, WholeR2, ContainerNot)):
            raise TypeError(f"Invalid type: {type(subset)}")
        self.__internal = subset

    def __invert__(self):
        return self.__internal

    def __eq__(self, other):
        if isinstance(other, ContainerNot):
            return (~self) == (~other)
        return super().__eq__(other)

    def __contains__(self, other):
        if isinstance(other, ContainerNot):
            return (~self) in (~other)  # pylint: disable=superfluous-parens
        return super().__contains__(other)

    def __str__(self):
        return "NOT[" + str(~self) + "]"

    def __repr__(self):
        return "NOT[" + repr(~self) + "]"

    def __hash__(self):
        return -hash(~self)


class ContainerOr(SubSetR2):
    """
    Defines the class that stores the union of some SubSetR2
    """

    def __init__(self, subsets: Iterable[SubSetR2]):
        subsets = frozenset(subsets)
        if len(subsets) < 2:
            raise ValueError("Less than 2 elements")
        if not all(isinstance(sub, SubSetR2) for sub in subsets):
            raise TypeError("Only SubSetR2 instances allowed")
        if any(
            isinstance(sub, (ContainerOr, EmptyR2, WholeR2)) for sub in subsets
        ):
            raise TypeError
        self.__internals = subsets

    def __iter__(self):
        yield from self.__internals

    def __hash__(self):
        return hash(self.__internals)

    def __str__(self):
        return "OR[" + ", ".join(map(str, self)) + "]"

    def __repr__(self):
        return "OR[" + ", ".join(map(repr, self)) + "]"

    def __eq__(self, other):
        if isinstance(other, ContainerOr):
            return frozenset(self) == frozenset(other)
        return super().__eq__(other)


class ContainerAnd(SubSetR2):
    """
    Defines the class that stores the intersection of some SubSetR2
    """

    def __init__(self, subsets: Iterable[SubSetR2]):
        subsets = frozenset(subsets)
        if len(subsets) < 2:
            raise ValueError("Less than 2 elements")
        if not all(isinstance(sub, SubSetR2) for sub in subsets):
            raise TypeError("Only SubSetR2 instances allowed")
        if any(
            isinstance(sub, (ContainerAnd, EmptyR2, WholeR2))
            for sub in subsets
        ):
            raise TypeError
        self.__internals = subsets

    def __iter__(self):
        yield from self.__internals

    def __hash__(self):
        return hash(self.__internals)

    def __str__(self):
        return "AND[" + ", ".join(map(str, self)) + "]"

    def __repr__(self):
        return "AND[" + ", ".join(map(repr, self)) + "]"

    def __contains__(self, other):
        return all(sub.__contains__(other) for sub in self)

    def __eq__(self, other):
        if isinstance(other, ContainerAnd):
            return frozenset(self) == frozenset(other)
        return super().__eq__(other)
