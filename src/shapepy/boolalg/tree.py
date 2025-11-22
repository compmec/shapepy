"""
File that defines a tree structure to store a boolean expression

Basically any boolean expression can be represented as a tree.
For example, 'a+b*c' can be stored as OR[a, AND[b, c]]
Which, for the root, there are two nodes 'a' and 'd' connected: OR[a, d]
The expression for 'd' is another three as the root AND[b, c]
"""

from __future__ import annotations

from collections import Counter
from enum import Enum
from typing import Generic, Iterable, Iterator, TypeVar

from ..loggers import debug
from ..tools import NotExpectedError

T = TypeVar("T")


class Operators(Enum):
    """Defines some options to be stored by a boolean three

    It represents how a root of a tree must treat its children"""

    NOT = 1
    AND = 2
    OR = 3
    XOR = 4


def flatten(items: Iterable[T], operator: Operators) -> Iterator[T]:
    """Flattens a tree that as an equivalent operator

    Example
    -------
    >>> A = items2tree(["a", "b"], Operators.OR)
    >>> flatten([A, "c", "d"], Operators.OR)
    ["a", "b", "c", "d"]
    """
    for item in items:
        if isinstance(item, BoolTree) and operator == item.operator:
            yield from item
        else:
            yield item


@debug("shapepy.boolalg.tree")
def items2tree(items: Iterable[T], operator: Operators) -> BoolTree[T]:
    """Creates a boolean tree from given items

    Example
    -------
    >>> items2tree(["a", "b"], Operators.OR)
    OR["a","b"]
    >>> items2tree(["a"], Operators.NOT)
    NOT["a"]
    """
    if operator == Operators.NOT:
        items = tuple(items)
        if len(items) != 1:
            raise NotExpectedError(f"Items = {len(items)}: {items}")
        item = items[0]
        if isinstance(item, BoolTree):
            if item.operator == Operators.NOT:
                return tuple(item)[0]
        return BoolTree((item,), Operators.NOT)
    items = flatten(items, operator)
    if operator == Operators.XOR:
        items = tuple(items)
        dictids = dict(Counter(map(id, items)))
        items = tuple(s for s in items if dictids[id(s)] % 2)
    else:
        items = tuple({id(i): i for i in items}.values())
    if len(items) == 1:
        return items[0]
    return BoolTree(items, operator)


class BoolTree(Generic[T]):
    """Defines a tree structure that stores a boolean expression"""

    def __init__(self, items: Iterable[T], operator: Operators):
        if operator == Operators.NOT and len(items) != 1:
            raise ValueError("NOT must have only one element")
        if operator not in Operators:
            raise TypeError(f"{operator} must be in {Operators}")
        self.__operator = operator
        self.__items = tuple(items)

    @property
    def operator(self) -> Operators:
        """Gets the operator of the tree between the options

        * OR: union between the items
        * AND: intersection between the items
        * NOT: the complementar of the item
        * XOR: xor between the items
        """
        return self.__operator

    def __iter__(self) -> Iterator[T]:
        yield from self.__items

    def __len__(self) -> int:
        return len(self.__items)

    def __repr__(self) -> str:
        ope2str = {
            Operators.OR: "OR",
            Operators.XOR: "XOR",
            Operators.AND: "AND",
            Operators.NOT: "NOT",
        }
        return ope2str[self.operator] + "[" + ",".join(map(repr, self)) + "]"


def false_tree() -> BoolTree:
    """Gets a boolean tree that is equivalent to false boolean value"""
    return BoolTree([], Operators.OR)


def true_tree() -> BoolTree:
    """Gets a boolean tree that is equivalent to true boolean value"""
    return BoolTree([], Operators.AND)
