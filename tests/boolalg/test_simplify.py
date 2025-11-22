import pytest

from shapepy.boolalg.converter import find_operator, string2tree, tree2string
from shapepy.boolalg.simplify import simplify_tree
from shapepy.boolalg.tree import Operators


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_find_operator():
    values = {
        "0": None,
        "1": None,
        "!0": Operators.NOT,
        "!1": Operators.NOT,
        "0+0": Operators.OR,
        "0+1": Operators.OR,
        "1+0": Operators.OR,
        "1+1": Operators.OR,
        "0*0": Operators.AND,
        "0*1": Operators.AND,
        "1*0": Operators.AND,
        "1*1": Operators.AND,
        "0^0": Operators.XOR,
        "0^1": Operators.XOR,
        "1^0": Operators.XOR,
        "1^1": Operators.XOR,
        "1*(1^0)": Operators.AND,
        "!0+0": Operators.OR,
        "!0*0": Operators.AND,
        "!0^0": Operators.XOR,
        "!1+1": Operators.OR,
        "!1*1": Operators.AND,
    }
    for expr, result in values.items():
        assert find_operator(expr) is result


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_find_operator",
    ]
)
def test_simplify_no_variable():
    table = {
        # DIRECT
        "0": "0",
        "1": "1",
        "(0)": "0",
        "(1)": "1",
        "((0))": "0",
        "((1))": "1",
        # NOT
        "!0": "1",
        "!1": "0",
        "!!0": "0",
        "!!1": "1",
        "!!!0": "1",
        "!!!1": "0",
        # OR
        "0": "0",
        "1": "1",
        "0+0": "0",
        "0+1": "1",
        "1+0": "1",
        "1+1": "1",
        "0+0+0": "0",
        "0+0+1": "1",
        "0+1+0": "1",
        "0+1+1": "1",
        "1+0+0": "1",
        "1+0+1": "1",
        "1+1+0": "1",
        "1+1+1": "1",
        # AND
        "0": "0",
        "1": "1",
        "0*0": "0",
        "0*1": "0",
        "1*0": "0",
        "1*1": "1",
        "0*0*0": "0",
        "0*0*1": "0",
        "0*1*0": "0",
        "0*1*1": "0",
        "1*0*0": "0",
        "1*0*1": "0",
        "1*1*0": "0",
        "1*1*1": "1",
        # XOR
        "0": "0",
        "1": "1",
        "0^0": "0",
        "0^1": "1",
        "1^0": "1",
        "1^1": "0",
        "0^0^0": "0",
        "0^0^1": "1",
        "0^1^0": "1",
        "0^1^1": "0",
        "1^0^0": "1",
        "1^0^1": "0",
        "1^1^0": "0",
        "1^1^1": "1",
    }

    for original, good in table.items():
        tree = string2tree(original)
        tree = simplify_tree(tree)
        test = tree2string(tree)
        assert test == good


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_find_operator",
        "test_simplify_no_variable",
    ]
)
def test_simplify_single_var():
    table = {
        # DIRECT
        "a": "a",
        "(a)": "a",
        "((a))": "a",
        # NOT
        "!a": "!a",
        "!!a": "a",
        "!!!a": "!a",
        "!!!!a": "a",
        # OR
        "a": "a",
        "a+a": "a",
        "a+!a": "1",
        "!a+a": "1",
        "!a+!a": "!a",
        "a+a+a": "a",
        "a+a+!a": "1",
        "a+!a+a": "1",
        "a+!a+!a": "1",
        "!a+a+a": "1",
        "!a+a+!a": "1",
        "!a+!a+a": "1",
        "!a+!a+!a": "!a",
        # AND
        "a": "a",
        "!a": "!a",
        "a*a": "a",
        "a*!a": "0",
        "!a*a": "0",
        "!a*!a": "!a",
        "a*a*a": "a",
        "a*a*!a": "0",
        "a*!a*a": "0",
        "a*!a*!a": "0",
        "!a*a*a": "0",
        "!a*a*!a": "0",
        "!a*!a*a": "0",
        "!a*!a*!a": "!a",
        # XOR
        "a": "a",
        "!a": "!a",
        "a^a": "0",
        "a^!a": "1",
        "!a^a": "1",
        "!a^!a": "0",
        "a^a^a": "a",
        "a^a^!a": "!a",
        "a^!a^a": "!a",
        "a^!a^!a": "a",
        "!a^a^a": "!a",
        "!a^a^!a": "a",
        "!a^!a^a": "a",
        "!a^!a^!a": "!a",
    }

    for original, good in table.items():
        tree = string2tree(original)
        tree = simplify_tree(tree)
        test = tree2string(tree)
        assert test == good


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_find_operator",
        "test_simplify_no_variable",
        "test_simplify_single_var",
    ]
)
def test_simplify_multi_var():

    table = {
        # DIRECT
        "a+b": "a+b",
        "(a+b)": "a+b",
        "(a)+b": "a+b",
        "((a))+b": "a+b",
        "((a))+(b)": "a+b",
        "((a)+a)+(b)": "a+b",
        "((a)+a)+(b+a)": "a+b",
        "a+b+c": "a+b+c",
        "a+b*c": "a+(b*c)",
    }
    for original, good in table.items():
        tree = string2tree(original)
        test = simplify_tree(tree)
        test = tree2string(test)
        assert test == good

    original = "a+b+c+d+e+f*a"
    tree = string2tree(original)
    tree = simplify_tree(tree, 4)
    test = tree2string(tree)
    assert test == "a+b+c+d+e+(f*a)"
    tree = simplify_tree(tree, 8)
    test = tree2string(tree)
    assert test == "a+b+c+d+e"


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_find_operator",
        "test_simplify_no_variable",
        "test_simplify_single_var",
        "test_simplify_multi_var",
    ]
)
def test_all():
    pass
