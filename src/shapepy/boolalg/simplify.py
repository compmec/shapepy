"""Contains the algorithm to simplify boolean expressions"""

from __future__ import annotations

from typing import Iterable, Iterator, Set, Tuple, TypeVar, Union

from ..loggers import debug
from ..tools import Is, NotExpectedError
from .tree import BoolTree, Operators, false_tree, true_tree

T = TypeVar("T")


def find_variables(tree: BoolTree[T]) -> Iterator[T]:
    """Searchs recursivelly in the tree for all the variables inside it

    A variable is any object refered by the tree that is not also a tree

    Example
    -------
    >>> tree = OR[XOR[A, B], AND[NOT[C], OR[D, E]]]
    >>> find_variables(tree)
    [A, B, C, D, E]
    """
    if not Is.instance(tree, BoolTree):
        yield tree
        return
    items = {}
    for item in tree:
        for var in find_variables(item):
            if id(var) not in items:
                items[id(var)] = var
    yield from items.values()


@debug("shapepy.boolalg.simplify")
def simplify_tree(
    tree: Union[T, BoolTree[T]], maxvars: int = 16
) -> BoolTree[T]:
    """Simplifies given boolean expression"""
    if not Is.instance(tree, BoolTree):
        return tree
    variables = tuple(find_variables(tree))
    if maxvars and len(variables) > maxvars:
        return tree
    idsvars = tuple(map(id, variables))
    table = Implicants.evaluate_table(tree, idsvars)
    if len(variables) == 0:
        result = bool(tuple(table)[0])
        return true_tree() if result else false_tree()
    implicants = Implicants.find_prime_implicants(table)
    implicants = Implicants.merge_prime_implicants(implicants)
    implicants = Implicants.sort_implicants(implicants)
    return Implicants.implicants2tree(implicants, variables)


class Implicants:
    """Class to store static methods used to simplify implicants"""

    TRUE = "1"
    FALSE = "0"
    NOTCARE = "-"

    @staticmethod
    @debug("shapepy.boolalg.simplify")
    def evaluate(tree: BoolTree, idsvars: Tuple[int], binary: int) -> bool:
        """Evaluates a single boolean expression"""
        if not Is.instance(tree, BoolTree):
            index = len(idsvars) - idsvars.index(id(tree)) - 1
            return bool(binary & (2**index))
        values = (Implicants.evaluate(i, idsvars, binary) for i in tree)
        if tree.operator == Operators.NOT:
            return not tuple(values)[0]
        if tree.operator == Operators.OR:
            return any(values)
        if tree.operator == Operators.AND:
            return all(values)
        if tree.operator == Operators.XOR:
            return sum(values) % 2
        raise NotExpectedError(f"Invalid operator: {tree.operator}")

    @staticmethod
    @debug("shapepy.boolalg.simplify")
    def evaluate_table(
        tree: BoolTree, idsvars: Iterable[int]
    ) -> Iterator[bool]:
        """Evaluates all the combination of boolean variables"""
        if not Is.instance(tree, BoolTree):
            raise TypeError(f"Invalid typo: {type(tree)}")
        results = []
        for counter in range(2 ** len(idsvars)):
            results.append(Implicants.evaluate(tree, idsvars, counter))
        return tuple(map(bool, results))

    @staticmethod
    def binary2number(binary: str) -> int:
        """Converts a binary representation to a number

        Example
        -------
        >>> binary2number("0000")
        0
        >>> binary2number("0001")
        1
        >>> binary2number("0010")
        2
        >>> binary2number("1111")
        15
        """
        number = 0
        for char in binary:
            number *= 2
            number += 1 if (char == Implicants.TRUE) else 0
        return number

    @staticmethod
    def number2binary(number: int, nbits: int) -> str:
        """Converts a number into a binary representation

        Example
        -------
        >>> number2binary(0, 4)
        0000
        >>> number2binary(1, 4)
        0001
        >>> number2binary(2, 4)
        0010
        >>> number2binary(15, 4)
        1111
        """
        chars = []
        while number > 0:
            char = Implicants.TRUE if number % 2 else Implicants.FALSE
            chars.insert(0, char)
            number //= 2
        return Implicants.FALSE * (nbits - len(chars)) + "".join(chars)

    @staticmethod
    def find_prime_implicants(results: Iterable[bool]) -> Iterator[str]:
        """Finds the prime implicants

        A minterm is of the form '1001', '1010', etc
        """
        results = tuple(results)
        nbits = 0
        length = len(results)
        while length > 2**nbits:
            nbits += 1
        if length != 2**nbits:
            raise ValueError(f"Invalid results: {results}")
        implicants = []
        for i, result in enumerate(results):
            if result:
                implicants.append(Implicants.number2binary(i, nbits))
        return tuple(implicants)

    @staticmethod
    @debug("shapepy.boolalg.simplify")
    def merge_prime_implicants(minterms: Iterable[str]) -> Set[str]:
        """Merge the prime implicants

        A minterm is of the form '1001', '1010', etc
        """
        minterms = tuple(minterms)
        while True:
            new_minterms = set()
            length = len(minterms)
            merges = [False] * length
            for i, mini in enumerate(minterms):
                for j in range(i + 1, length):
                    minj = minterms[j]
                    if Implicants.can_merge(mini, minj):
                        merges[i] = True
                        merges[j] = True
                        merged = Implicants.merge_two(mini, minj)
                        if merged not in minterms:
                            new_minterms.add(merged)
            if len(new_minterms) == 0:
                break
            minterms = (m for i, m in enumerate(minterms) if not merges[i])
            minterms = tuple(set(minterms) | set(new_minterms))

        return minterms

    @staticmethod
    def can_merge(mini: str, minj: str) -> bool:
        """Tells if it's possible to merge two implicants"""
        assert Is.instance(mini, str)
        assert Is.instance(minj, str)
        assert len(mini) == len(minj)
        for chari, charj in zip(mini, minj):
            if (chari == Implicants.NOTCARE) ^ (charj == Implicants.NOTCARE):
                return False
        numi = Implicants.binary2number(mini)
        numj = Implicants.binary2number(minj)
        res = numi ^ numj
        return res != 0 and (res & res - 1) == 0

    @staticmethod
    def merge_two(mini: str, minj: str) -> bool:
        """Merge two implicants"""
        result = []
        for chari, charj in zip(mini, minj):
            new_char = Implicants.NOTCARE if chari != charj else chari
            result.append(new_char)
        return "".join(result)

    @staticmethod
    @debug("shapepy.boolalg.simplify")
    def sort_implicants(implicants: Iterable[str]) -> Iterable[str]:
        """Sorts the implicants by the simplest first"""
        implicants = tuple(implicants)
        weights = tuple(
            sum(c == Implicants.NOTCARE for c in imp) for imp in implicants
        )
        return tuple(
            i for _, i in sorted(zip(weights, implicants), reverse=True)
        )

    @staticmethod
    def implicants2tree(
        implicants: Iterable[str], variables: Tuple[T]
    ) -> BoolTree[T]:
        """
        Tranforms the implicants into a tree
        """
        invvars = tuple(BoolTree((v,), Operators.NOT) for v in variables)
        ands = []
        for implicant in implicants:
            parts = []
            for i, imp in enumerate(implicant):
                if imp == Implicants.FALSE:
                    parts.append(invvars[i])
                elif imp == Implicants.TRUE:
                    parts.append(variables[i])
            if len(parts) == 1:
                ands.append(parts[0])
            else:
                ands.append(BoolTree(parts, Operators.AND))
        return ands[0] if len(ands) == 1 else BoolTree(ands, Operators.OR)
