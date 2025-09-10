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
NULL = ""
TRUE = "1"
FALSE = "0"
NOTCARE = "-"
OPERATORS = (OR, XOR, AND, NOT)


@debug("shapepy.scalar.boolalg")
def simplify(expression: str) -> str:
    """Simplifies given boolean expression"""
    if not Is.instance(expression, str):
        raise TypeError
    expression = simplify_no_variable(expression)
    variables = find_variables(expression)
    if 0 < len(variables) < 5:
        table = Implicants.evaluate_table(expression)
        implicants = Implicants.find_prime_implicants(table)
        implicants = Implicants.merge_prime_implicants(implicants)
        variables = "".join(sorted(variables))
        if len(implicants) == 0:
            return FALSE
        and_exprs = (
            Implicants.implicant2expression(imp, variables)
            for imp in implicants
        )
        return Formatter.mult_strs(and_exprs, OR)
    return expression


def find_variables(expression: str) -> str:
    """Searches the expression to finding the variables

    Example
    -------
    >>> find_variables("a")
    'a'
    >>> find_variables("a*b+b")
    'ab'
    >>> find_variables("a*b+c^(!a+b)")
    'abc'
    """
    if not Is.instance(expression, str):
        raise TypeError(f"Invalid typo: {type(expression)}")
    return "".join(sorted(set(re.findall(r"([a-z])", expression))))


def remove_parentesis(expression: str) -> str:
    """Removes the parentesis for given expression

    Example
    -------
    >>> remove_parentesis("a")
    a
    >>> remove_parentesis("(a)")
    a
    >>> remove_parentesis("((a))")
    a
    """
    operator = find_operator(expression)
    while operator is NULL and expression[0] == "(" and expression[-1] == ")":
        expression = expression[1:-1]
        operator = find_operator(expression)
    return expression


def simplify_no_variable(expression: str) -> str:
    """Simplifies the given boolean expression ignoring the values
    that the variables can assume"""
    if not Is.instance(expression, str):
        raise TypeError
    if len(expression) == 0:
        raise ValueError
    expression = remove_parentesis(expression)
    operator = find_operator(expression)
    if operator is NULL:
        if not Implicants.can_evaluate(expression):
            return expression
        return TRUE if Implicants.evaluate(expression) else FALSE
    if operator is NOT:
        subexpression = extract(expression, NOT)
        if not Implicants.can_evaluate(expression):
            return Formatter.invert_str(simplify_no_variable(subexpression))
        return FALSE if Implicants.evaluate(subexpression) else TRUE
    return multiple_no_variable(expression, operator)


def multiple_no_variable(expression: str, operator: str) -> str:
    """Simplifies the given boolean expression
    when the operator is AND, OR or XOR"""
    subexps = extract(expression, operator)
    if operator is XOR:
        subexps = (s for s, i in dict(Counter(subexps)).items() if i % 2)
    subexps = set(map(simplify_no_variable, set(subexps)))
    if operator is XOR:
        subexps = set(s for s in subexps if s != FALSE)
    elif operator is AND:
        subexps = set(s for s in subexps if s != TRUE)
    elif operator is OR:
        subexps = set(s for s in subexps if s != FALSE)
    if len(subexps) == 0:
        return TRUE if operator is AND else FALSE
    return Formatter.mult_strs(subexps, operator)


def extract(expression: str, operator: str) -> Union[str, Iterator[str]]:
    """Extracts from the expression the required subset

    Example
    -------
    >>> extract("!a+b", "+")
    ('!a', 'b')
    >>> extract("!a+b", "*")
    ('!a+b', )
    >>> extract("!a", "+")
    ('!a', )
    >>> extract("!a", "!")
    'a'
    """
    if operator == NOT:
        return expression[1:]
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
            elif expression[indexj] == operator and parentesis == 0:
                break
            indexj += 1
        subset = expression[indexi:indexj]
        subsets.append(subset)
        indexi = indexj + 1
    return tuple(subsets)


def find_operator(expression: str) -> str:
    """Finds the operator to divide the given expression

    If no operator exists, returns an empty string

    Example
    -------
    >>> find_operator("a+b*c")
    +
    >>> find_operator("!a^b")
    ^
    >>> find_operator("!a")
    !
    >>> find_operator("a")
    ''
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
    return NULL


class Formatter:
    """Contains static method for extract"""

    @staticmethod
    def compare_expression(expression: str) -> Tuple[int, str]:
        """Function used to sort expressions"""
        return (len(expression), expression)

    @staticmethod
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

    @staticmethod
    def mult_strs(expressions: Iterable[str], operator: str) -> str:
        """Gives the intersection of given expressions.

        Example
        -------
        >>> mult_strs({'a'}, '+')
        a
        >>> mult_strs({'a','b'}, '+')
        a+b
        >>> mult_strs({'a*b','c'}, '+')
        c+(a*b)
        >>> mult_strs({'c+(a*b)'}, '+')
        c+(a*b)
        >>> mult_strs({'a'}, '*')
        a
        >>> mult_strs({'a','b'}, '*')
        a*b
        >>> mult_strs({'a*b','c'}, '*')
        c*(a*b)
        >>> mult_strs({'c+(a*b)'}, '*')
        c+(a*b)
        """
        expressions = tuple(expressions)
        if len(expressions) == 1:
            return expressions[0]
        exprs = (e if len(e) < 3 else ("(" + e + ")") for e in expressions)
        return operator.join(sorted(exprs, key=Formatter.compare_expression))


class Implicants:
    """Class to store static methods used to simplify implicants"""

    @staticmethod
    def funcand(values: Iterable[bool], /) -> bool:
        """Function that computes the AND of many booleans"""
        return all(map(bool, values))

    @staticmethod
    def funcor(values: Iterable[bool], /) -> bool:
        """Function that computes the OR of many booleans"""
        return any(map(bool, values))

    @staticmethod
    def funcxor(values: Iterable[bool], /) -> bool:
        """Function that computes the XOR of many booleans"""
        values = iter(values)
        result = next(values)
        for value in values:
            result ^= value
        return result

    @staticmethod
    @debug("shapepy.scalar.boolalg")
    def can_evaluate(expression: str) -> bool:
        """Tells if it's possible evaluate a boolean expression"""
        return find_variables(expression) == ""

    @staticmethod
    @debug("shapepy.scalar.boolalg")
    def evaluate(expression: str) -> bool:
        """Evaluates a single boolean expression"""
        if not Implicants.can_evaluate(expression):
            raise ValueError(f"Cannot evaluate expression {expression}")
        expression = remove_parentesis(expression)
        if len(expression) == 1:
            if expression not in {FALSE, TRUE}:
                raise NotExpectedError(f"Invalid {expression}")
            return expression == TRUE
        operator = find_operator(expression)
        if operator not in OPERATORS:
            raise NotExpectedError(str(expression))
        if operator == NOT:
            subexpression = extract(expression, NOT)
            return not Implicants.evaluate(subexpression)
        if operator not in {AND, OR, XOR}:
            raise ValueError
        subexprs = extract(expression, operator)
        results = map(Implicants.evaluate, subexprs)
        if operator == AND:
            return Implicants.funcand(results)
        if operator == OR:
            return Implicants.funcor(results)
        if operator == XOR:
            return Implicants.funcxor(results)
        raise NotExpectedError(f"{operator} Exp {expression}")

    @staticmethod
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
                yield Implicants.evaluate(expression)
            else:
                var = variables[indexvar]
                indexvar += 1
                yield from recursive(expression.replace(var, FALSE))
                yield from recursive(expression.replace(var, TRUE))
                indexvar -= 1

        return tuple(recursive(expression))

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
                parts.append(Formatter.invert_str(v))
            elif i == TRUE:
                parts.append(v)
        return Formatter.mult_strs(parts, AND) if len(parts) > 0 else TRUE
