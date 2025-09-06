"""Contains the algorithm to simplify boolean expressions"""

from __future__ import annotations

import re
from typing import Iterable, Iterator, List, Set, Tuple

from ..loggers import debug, get_logger
from ..tools import Is, NotExpectedError

AND = "*"
OR = "+"
NOT = "!"
XOR = "^"
TRUE = "1"
FALSE = "0"
NOTCARE = "-"
OPERATORS = {AND, OR, NOT, XOR}


def funcand(values: Iterable[bool], /) -> bool:
    return all(values)


def funcor(values: Iterable[bool], /) -> bool:
    return any(values)


def funcxor(values: Iterable[bool], /) -> bool:
    values = iter(values)
    result = next(values)
    for value in values:
        result ^= value
    return result


METHODS = {
    AND: funcand,
    OR: funcor,
    XOR: funcxor,
}


@debug("shapepy.scalar.boolalg")
def simplify(expression: str) -> str:
    """Simplifies given boolean expression"""
    if not Is.instance(expression, str):
        raise TypeError
    variables = find_variables(expression)
    if 0 < len(variables) < 5:
        table = evaluate_table(expression)
        implicants = Implicants.find_prime_implicants(table)
        implicants = Implicants.merge_prime_implicants(implicants)
        variables = "".join(sorted(variables))
        if len(implicants) == 0:
            return FALSE
        and_exprs = (
            Implicants.implicant2expression(imp, variables)
            for imp in implicants
        )
        if len(implicants) == 1:
            return next(and_exprs)
        return OR + OR.join("(" + expr + ")" for expr in and_exprs)
    return expression


@debug("shapepy.scalar.boolalg")
def find_variables(expression: str) -> str:
    """Searches the expression to finding the variables"""
    assert Is.instance(expression, str)
    return "".join(sorted(set(re.findall(r"([a-z])", expression))))


@debug("shapepy.scalar.boolalg")
def evaluate_table(expression: str) -> Iterable[bool]:
    """Evaluates all the combination of boolean variables"""
    assert Is.instance(expression, str)

    indexvar = 0
    variables = find_variables(expression)

    def recursive(expression: str) -> Iterable[int]:
        """Recursive function to subs the variables into expression"""
        nonlocal indexvar
        if indexvar == len(variables):
            yield evaluate_tree(expression)
        else:
            var = variables[indexvar]
            indexvar += 1
            yield from recursive(expression.replace(var, FALSE))
            yield from recursive(expression.replace(var, TRUE))
            indexvar -= 1

    return tuple(recursive(expression))


@debug("shapepy.scalar.boolalg")
def evaluate_tree(expression: str) -> bool:
    """Evaluates a single boolean expression"""
    # logger = get_logger("shapepy.scalar.boolalg")
    if expression[0] == NOT:
        return not evaluate_tree(expression[1:])
    if len(expression) == 1:
        if expression not in {FALSE, TRUE}:
            raise NotExpectedError(f"Invalid {expression}")
        return expression == TRUE
    if expression[0] not in OPERATORS:
        if expression[0] != "(":
            raise NotExpectedError(f"Invalid {expression}")
        return evaluate_tree(expression[1:-1])
    operator = expression[0]
    if operator not in {AND, OR, XOR}:
        raise ValueError
    subexprs = divide_by(expression[1:], operator)
    results = map(evaluate_tree, subexprs)
    return METHODS[operator](results)


@debug("shapepy.scalar.boolalg")
def divide_by(expression: str, divisor: str) -> Iterator[str]:
    """Divides the standard expression by divisor"""
    parentesis = 1 if expression[0] == "(" else 0
    indexi = 0
    while indexi < len(expression):
        indexj = indexi + 1
        while indexj < len(expression):
            if expression[indexj] == "(":
                parentesis += 1
            elif expression[indexj] == ")":
                parentesis -= 1
            elif expression[indexj] == divisor and parentesis == 0:
                break
            indexj += 1
        subset = expression[indexi:indexj]
        yield subset
        indexi = indexj + 1


class Implicants:
    """Class to store static methods used to simplify implicants"""

    @debug("shapepy.scalar.boolalg")
    def binary2number(binary: str) -> int:
        """Converts a binary representation to a number"""
        number = 0
        for char in binary:
            number *= 2
            number += 1 if (char == TRUE) else 0
        return number

    @debug("shapepy.scalar.boolalg")
    def number2binary(number: int, nbits: int) -> str:
        """Converts a number into a binary representation"""
        chars = []
        while number > 0:
            char = TRUE if number % 2 else FALSE
            chars.insert(0, char)
            number //= 2
        return FALSE * (nbits - len(chars)) + "".join(chars)

    @debug("shapepy.scalar.boolalg")
    def find_prime_implicants(results: Iterable[bool]) -> Tuple[str]:
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
        if nbits == 0:
            raise ValueError
        implicants: List[str] = []
        for i, result in enumerate(results):
            if result:
                implicant = Implicants.number2binary(i, nbits)
                implicants.append(implicant)
        return tuple(implicants)

    @debug("shapepy.scalar.boolalg")
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

    @debug("shapepy.scalar.boolalg")
    def can_merge(mini: str, minj: str) -> bool:
        """Tells if it's possible to merge two implicants"""
        assert Is.instance(mini, str)
        assert Is.instance(minj, str)
        assert len(mini) == len(minj)
        for chari, charj in zip(mini, minj):
            if (chari == "-") ^ (charj == "-"):
                return False
        numi = Implicants.binary2number(mini)
        numj = Implicants.binary2number(minj)
        res = numi ^ numj
        return res != 0 and (res & res - 1) == 0

    @debug("shapepy.scalar.boolalg")
    def merge_two(mini: str, minj: str) -> bool:
        """Merge two implicants"""
        result = []
        for chari, charj in zip(mini, minj):
            new_char = "-" if chari != charj else chari
            result.append(new_char)
        return "".join(result)

    @debug("shapepy.scalar.boolalg")
    def implicant2expression(implicant: str, variables: str) -> str:
        """Tranforms an implicant to an AND expression

        Example
        -------
        >>> implicant = "a
        """
        assert Is.instance(implicant, str)
        assert Is.instance(variables, str)
        assert len(implicant) == len(variables)
        parts = []
        for i, v in zip(implicant, variables):
            if i == FALSE:
                parts.append(NOT + v)
            elif i == TRUE:
                parts.append(v)
        return AND + AND.join(parts)
