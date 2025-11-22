"""
File that contains functions to convert a string to a boolean tree,
or convert the boolean tree into a string

Example
-------
>>> msg = "a+b*c"
>>> tree = string2tree(msg)
>>> tree
OR["a", AND["b", "c"]]
>>> tree2string(tree)
a+b*c
"""

from typing import Iterator, List, Union

from ..loggers import debug
from ..tools import Is
from .tree import BoolTree, Operators, false_tree, items2tree, true_tree

TRUE = "1"
FALSE = "0"

OPE2STR = {
    Operators.OR: "+",
    Operators.XOR: "^",
    Operators.AND: "*",
    Operators.NOT: "!",
}
STR2OPE = {v: k for k, v in OPE2STR.items()}


@debug("shapepy.boolalg.converter")
def string2tree(expression: str) -> Union[str, BoolTree[str]]:
    """Converts a string into a boolean tree

    Example
    -------
    >>> msg = "a+b*c"
    >>> string2tree(msg)
    OR["a", AND["b", "c"]]
    """
    operator = find_operator(expression)
    while operator is None and expression[0] == "(" and expression[-1] == ")":
        expression = expression[1:-1]
        operator = find_operator(expression)
    if operator is None:
        if expression is TRUE:
            return true_tree()
        if expression is FALSE:
            return false_tree()
        return expression
    items = tuple(extract(expression, operator))
    items = tuple(map(string2tree, items))
    return items2tree(items, operator)


@debug("shapepy.boolalg.converter")
def tree2string(tree: Union[str, BoolTree[str]]) -> str:
    """Converts a boolean tree into a expression

    Example
    -------
    >>> msg = "a+b*c"
    >>> tree = string2tree(msg)
    OR["a", AND["b", "c"]]
    >>> tree2string(tree)
    a+b*c
    """
    if not Is.instance(tree, BoolTree):
        return tree
    if len(tree) == 0:
        return TRUE if tree.operator == Operators.AND else FALSE
    items: List[str] = []
    for item in tree:
        stritem = tree2string(item)
        if (
            Is.instance(item, BoolTree)
            and len(item) > 1
            and item.operator.value > tree.operator.value
        ):
            stritem = "(" + stritem + ")"
        items.append(stritem)
    if tree.operator == Operators.NOT:
        return OPE2STR[tree.operator] + items[0]
    return OPE2STR[tree.operator].join(items)


@debug("shapepy.boolalg.converter")
def extract(expression: str, operator: Operators) -> Iterator[str]:
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
    if operator == Operators.NOT:
        return [expression[1:]]
    char = OPE2STR[operator]
    result: List[str] = []
    indexi = 0
    while indexi < len(expression):
        parentesis = 1 if expression[indexi] == "(" else 0
        indexj = indexi + 1
        while indexj < len(expression):
            if expression[indexj] == "(":
                parentesis += 1
            elif expression[indexj] == ")":
                parentesis -= 1
            elif expression[indexj] == char and parentesis == 0:
                break
            indexj += 1
        result.append(expression[indexi:indexj])
        indexi = indexj + 1
    return result


@debug("shapepy.boolalg.converter")
def find_operator(expression: str) -> Union[None, Operators]:
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
    for operator in (op for op in STR2OPE if op in expression):
        parentesis = 0
        for char in expression:
            if char == "(":
                parentesis += 1
            elif char == ")":
                parentesis -= 1
            elif parentesis != 0:
                continue
            elif char == operator:
                return STR2OPE[operator]
    return None
