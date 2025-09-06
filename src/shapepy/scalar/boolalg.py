"""Contains the algorithm to simplify boolean expressions"""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, Iterator, List, Set, Tuple, Union

from ..loggers import debug
from ..tools import Is, NotExpectedError

AND = "*"
OR = "+"
NOT = "!"
XOR = "^"
TRUE = "1"
FALSE = "0"
NOTCARE = "-"
OPERATORS = (OR, XOR, AND, NOT)


def funcand(values: Iterable[bool], /) -> bool:
    """Function that computes the AND of many booleans"""
    return all(map(bool, values))


def funcor(values: Iterable[bool], /) -> bool:
    """Function that computes the OR of many booleans"""
    return any(map(bool, values))


def funcxor(values: Iterable[bool], /) -> bool:
    """Function that computes the XOR of many booleans"""
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
    expression = simplify_no_variable(expression)
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
        return unite_strs(and_exprs)
    return expression


# pylint: disable=too-many-return-statements,too-many-branches
@debug("shapepy.scalar.boolalg")
def simplify_no_variable(expression: str) -> str:
    """Simplifies the given boolean expression ignoring the values
    that the variables can assume"""
    if not Is.instance(expression, str):
        raise TypeError
    if len(expression) == 0:
        raise ValueError
    operator = find_operator(expression)
    while operator is None and expression[0] == "(" and expression[-1] == ")":
        expression = expression[1:-1]
        operator = find_operator(expression)
    if operator is None:
        try:
            return TRUE if evaluate_tree(expression) else FALSE
        except ValueError:
            return expression

    if operator == NOT:
        if expression[0] != NOT:
            raise NotExpectedError(f"Expression: {expression}")
        try:
            return (
                TRUE if not evaluate_tree(extract(expression, NOT)) else FALSE
            )
        except ValueError:
            return invert_str(simplify_no_variable(extract(expression, NOT)))
    subexprs = extract(expression, operator)
    if operator == XOR:
        subexprs = (s for s, i in dict(Counter(subexprs)).items() if i % 2)
    subexprs = set(map(simplify_no_variable, set(subexprs)))
    if operator == XOR:
        subexprs = set(s for s in subexprs if s != FALSE)
    elif operator == AND:
        subexprs = set(s for s in subexprs if s != TRUE)
    elif operator == OR:
        subexprs = set(s for s in subexprs if s != FALSE)
    if len(subexprs) == 0:
        return TRUE if operator == AND else FALSE
    if len(subexprs) == 1:
        return tuple(subexprs)[0]
    subexprs = sorted(subexprs, key=compare_expression)
    subexprs = (s if len(s) < 2 else ("(" + s + ")") for s in subexprs)
    return operator.join(subexprs)


@debug("shapepy.scalar.boolalg")
def find_operator(expression: str) -> Union[None, str]:
    """From the given expression, finds the operator to divide the expression

    Example
    -------
    >>> find_operator("a+b*c")
    +
    >>> find_operator("!a^b")
    ^
    """
    if not Is.instance(expression, str):
        raise ValueError(f"Invalid argument {expression}")
    if len(expression) == 0:
        raise ValueError(f"Invalid expression '{expression}'")
    for operator in (op for op in OPERATORS if op in expression):
        parentesis = 0
        for char in expression:
            if char == "(":
                parentesis += 1
            elif char == ")":
                parentesis -= 1
            elif parentesis != 0:
                continue
            elif char == operator:
                return char
    return None


@debug("shapepy.scalar.boolalg")
def find_variables(expression: str) -> str:
    """Searches the expression to finding the variables"""
    if not Is.instance(expression, str):
        raise TypeError(f"Invalid typo: {type(expression)}")
    return "".join(sorted(set(re.findall(r"([a-z])", expression))))


@debug("shapepy.scalar.boolalg")
def evaluate_table(expression: str) -> Iterable[bool]:
    """Evaluates all the combination of boolean variables"""
    if not Is.instance(expression, str):
        raise TypeError(f"Invalid typo: {type(expression)}")

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
    if len(find_variables(expression)) != 0:
        raise ValueError(f"Cannot evaluate expression {expression}")
    operator = find_operator(expression)
    while operator is None and expression[0] == "(" and expression[-1] == ")":
        expression = expression[1:-1]
        operator = find_operator(expression)
    if len(expression) == 1:
        if expression not in {FALSE, TRUE}:
            raise NotExpectedError(f"Invalid {expression}")
        return expression == TRUE
    if operator not in OPERATORS:
        raise NotExpectedError(str(expression))
    if operator == NOT:
        if expression[0] != NOT:
            raise NotExpectedError(str(expression))
        return not evaluate_tree(expression[1:])
    if operator not in {AND, OR, XOR}:
        raise ValueError
    subexprs = extract(expression, operator)
    results = map(evaluate_tree, subexprs)
    return METHODS[operator](results)


def compare_expression(expression: str) -> Tuple[int, str]:
    """Function used to sort expressions"""
    return (len(expression), expression)


def invert_str(expression: str) -> str:
    """Inverts an expression

    Example
    -------
    >>> invert_str('a')
    !a
    >>> invert_str('a*b')
    !(a*b)
    """
    if len(expression) > 1:
        expression = "(" + expression + ")"
    return NOT + expression


def unite_strs(expressions: Iterable[str]) -> str:
    """Gives the union of given expressions.

    Example
    -------
    >>> unite_strs({'a'})
    a
    >>> unite_strs({'a','b'})
    a+b
    >>> unite_strs({'a*b','c'})
    c+(a*b)
    >>> unite_strs({'c+(a*b)'})
    c+(a*b)
    """
    expressions = tuple(expressions)
    if len(expressions) == 1:
        return expressions[0]
    exprs = (e if len(e) < 2 else ("(" + e + ")") for e in expressions)
    return OR.join(sorted(exprs, key=compare_expression))


def intersect_strs(expressions: Iterable[str]) -> str:
    """Gives the intersection of given expressions.

    Example
    -------
    >>> intersect_strs({'a'})
    a
    >>> intersect_strs({'a','b'})
    a*b
    >>> intersect_strs({'a*b','c'})
    c*(a*b)
    >>> intersect_strs({'c+(a*b)'})
    c+(a*b)
    """
    expressions = tuple(expressions)
    if len(expressions) == 1:
        return expressions[0]
    exprs = (e if len(e) < 2 else ("(" + e + ")") for e in expressions)
    return AND.join(sorted(exprs, key=compare_expression))


def extract(expression: str, operator: str) -> Union[str, Iterator[str]]:
    """Extracts from the expression the required"""
    if operator == NOT:
        return expression[1:]
    return divide_by(expression, operator)


@debug("shapepy.scalar.boolalg")
def divide_by(expression: str, divisor: str) -> Iterator[str]:
    """Divides the standard expression by divisor"""
    if not Is.instance(expression, str) or len(expression) == 0:
        raise NotExpectedError(str(expression))
    subsets: List[str] = []
    indexi = 0
    while indexi < len(expression):
        parentesis = 1 if expression[indexi] == "(" else 0
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
        subsets.append(subset)
        indexi = indexj + 1
    return tuple(subsets)


class Implicants:
    """Class to store static methods used to simplify implicants"""

    @staticmethod
    @debug("shapepy.scalar.boolalg")
    def binary2number(binary: str) -> int:
        """Converts a binary representation to a number"""
        number = 0
        for char in binary:
            number *= 2
            number += 1 if (char == TRUE) else 0
        return number

    @staticmethod
    @debug("shapepy.scalar.boolalg")
    def number2binary(number: int, nbits: int) -> str:
        """Converts a number into a binary representation"""
        chars = []
        while number > 0:
            char = TRUE if number % 2 else FALSE
            chars.insert(0, char)
            number //= 2
        return FALSE * (nbits - len(chars)) + "".join(chars)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def can_merge(mini: str, minj: str) -> bool:
        """Tells if it's possible to merge two implicants"""
        assert Is.instance(mini, str)
        assert Is.instance(minj, str)
        assert len(mini) == len(minj)
        for chari, charj in zip(mini, minj):
            if (chari == NOTCARE) ^ (charj == NOTCARE):
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
            new_char = NOTCARE if chari != charj else chari
            result.append(new_char)
        return "".join(result)

    @staticmethod
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
        assert len(implicant) > 0
        parts = []
        for i, v in zip(implicant, variables):
            if i == FALSE:
                parts.append(invert_str(v))
            elif i == TRUE:
                parts.append(v)
        return intersect_strs(parts) if len(parts) > 0 else TRUE
