import math

import pytest

from shapepy.loggers import enable_logger
from shapepy.scalar.boolalg import (
    Implicants,
    evaluate_table,
    evaluate_tree,
    find_operator,
    simplify,
)
from shapepy.scalar.reals import Is, Math, To


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_find_operator():
    values = {
        "0": None,
        "1": None,
        "!0": "!",
        "!1": "!",
        "0+0": "+",
        "0+1": "+",
        "1+0": "+",
        "1+1": "+",
        "0*0": "*",
        "0*1": "*",
        "1*0": "*",
        "1*1": "*",
        "0^0": "^",
        "0^1": "^",
        "1^0": "^",
        "1^1": "^",
        "1*(1^0)": "*",
        "!0+0": "+",
        "!0*0": "*",
        "!0^0": "^",
        "!1+1": "+",
        "!1*1": "*",
    }
    for expr, result in values.items():
        assert find_operator(expr) is result


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_find_operator"])
def test_evaluate_basic():
    values = {
        "0": False,
        "1": True,
        "!0": True,
        "!1": False,
        "0+0": False,
        "0+1": True,
        "1+0": True,
        "1+1": True,
        "0*0": False,
        "0*1": False,
        "1*0": False,
        "1*1": True,
        "0^0": False,
        "0^1": True,
        "1^0": True,
        "1^1": False,
    }
    for expr, result in values.items():
        assert evaluate_tree(expr) is result


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_evaluate_basic"])
def test_evaluate_tree():
    values = {
        "0+(1*(1^0))": True,
    }
    for expr, result in values.items():
        assert evaluate_tree(expr) is result


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_evaluate_basic", "test_evaluate_tree"])
def test_table_single_var():
    assert tuple(evaluate_table("0")) == (False,)
    assert tuple(evaluate_table("1")) == (True,)
    assert tuple(evaluate_table("!0")) == (True,)
    assert tuple(evaluate_table("!1")) == (False,)
    values = {
        "a+a": (False, True),
        "!a+a": (True, True),
        "a+!a": (True, True),
        "!a+!a": (True, False),
        "a*a": (False, True),
        "!a*a": (False, False),
        "a*!a": (False, False),
        "!a*!a": (True, False),
        "a^a": (False, False),
        "a^!a": (True, True),
        "!a^a": (True, True),
        "!a^!a": (False, False),
    }
    assert tuple(evaluate_table("a")) == (False, True)
    assert tuple(evaluate_table("!a")) == (True, False)
    for expr, result in values.items():
        assert tuple(evaluate_table(expr)) == result


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_evaluate_basic",
        "test_evaluate_tree",
        "test_table_single_var",
    ]
)
def test_table_multi_var():
    values = {
        "a+b": (False, True, True, True),
        "a*b": (False, False, False, True),
        "a^b": (False, True, True, False),
        "!a+b": (True, True, False, True),
        "a+!b": (True, False, True, True),
        "a+!b": (True, False, True, True),
        "!(a+b)": (True, False, False, False),
    }
    for expr, result in values.items():
        assert tuple(evaluate_table(expr)) == result


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_evaluate_basic",
        "test_evaluate_tree",
        "test_table_single_var",
    ]
)
def test_merge_prime_implicants():
    table = evaluate_table("a+a")
    implicants = Implicants.find_prime_implicants(table)
    implicants = Implicants.merge_prime_implicants(implicants)
    assert set(implicants) == {"1"}

    table = evaluate_table("a+!a")
    implicants = Implicants.find_prime_implicants(table)
    implicants = Implicants.merge_prime_implicants(implicants)
    assert set(implicants) == {"-"}

    table = evaluate_table("!a+a")
    implicants = Implicants.find_prime_implicants(table)
    implicants = Implicants.merge_prime_implicants(implicants)
    assert set(implicants) == {"-"}

    table = evaluate_table("!a+!a")
    implicants = Implicants.find_prime_implicants(table)
    implicants = Implicants.merge_prime_implicants(implicants)
    assert set(implicants) == {"0"}

    table = evaluate_table("a*a")
    implicants = Implicants.find_prime_implicants(table)
    implicants = Implicants.merge_prime_implicants(implicants)
    assert set(implicants) == {"1"}

    table = evaluate_table("a*!a")
    implicants = Implicants.find_prime_implicants(table)
    implicants = Implicants.merge_prime_implicants(implicants)
    assert set(implicants) == set()

    table = evaluate_table("!a*a")
    implicants = Implicants.find_prime_implicants(table)
    implicants = Implicants.merge_prime_implicants(implicants)
    assert set(implicants) == set()

    table = evaluate_table("!a*!a")
    implicants = Implicants.find_prime_implicants(table)
    implicants = Implicants.merge_prime_implicants(implicants)
    assert set(implicants) == {"0"}

    table = evaluate_table("a+b")
    implicants = Implicants.find_prime_implicants(table)
    implicants = Implicants.merge_prime_implicants(implicants)
    assert set(implicants) == {"1-", "-1"}

    table = evaluate_table("a*b")
    implicants = Implicants.find_prime_implicants(table)
    implicants = Implicants.merge_prime_implicants(implicants)
    assert set(implicants) == {"11"}


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_evaluate_basic",
        "test_evaluate_tree",
        "test_table_single_var",
        "test_table_multi_var",
        "test_merge_prime_implicants",
    ]
)
def test_simplify_no_variable():
    # DIRECT
    assert simplify("0") == "0"
    assert simplify("1") == "1"
    assert simplify("(0)") == "0"
    assert simplify("(1)") == "1"
    assert simplify("((0))") == "0"
    assert simplify("((1))") == "1"

    # NOT
    assert simplify("!0") == "1"
    assert simplify("!1") == "0"
    assert simplify("!!0") == "0"
    assert simplify("!!1") == "1"
    assert simplify("!!!0") == "1"
    assert simplify("!!!1") == "0"

    # OR
    assert simplify("0") == "0"
    assert simplify("1") == "1"
    assert simplify("0+0") == "0"
    assert simplify("0+1") == "1"
    assert simplify("1+0") == "1"
    assert simplify("1+1") == "1"
    assert simplify("0+0+0") == "0"
    assert simplify("0+0+1") == "1"
    assert simplify("0+1+0") == "1"
    assert simplify("0+1+1") == "1"
    assert simplify("1+0+0") == "1"
    assert simplify("1+0+1") == "1"
    assert simplify("1+1+0") == "1"
    assert simplify("1+1+1") == "1"

    # AND
    assert simplify("0") == "0"
    assert simplify("1") == "1"
    assert simplify("0*0") == "0"
    assert simplify("0*1") == "0"
    assert simplify("1*0") == "0"
    assert simplify("1*1") == "1"
    assert simplify("0*0*0") == "0"
    assert simplify("0*0*1") == "0"
    assert simplify("0*1*0") == "0"
    assert simplify("0*1*1") == "0"
    assert simplify("1*0*0") == "0"
    assert simplify("1*0*1") == "0"
    assert simplify("1*1*0") == "0"
    assert simplify("1*1*1") == "1"

    # XOR
    assert simplify("0") == "0"
    assert simplify("1") == "1"
    assert simplify("0^0") == "0"
    assert simplify("0^1") == "1"
    assert simplify("1^0") == "1"
    assert simplify("1^1") == "0"
    assert simplify("0^0^0") == "0"
    assert simplify("0^0^1") == "1"
    assert simplify("0^1^0") == "1"
    assert simplify("0^1^1") == "0"
    assert simplify("1^0^0") == "1"
    assert simplify("1^0^1") == "0"
    assert simplify("1^1^0") == "0"
    assert simplify("1^1^1") == "1"


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_evaluate_basic",
        "test_evaluate_tree",
        "test_table_single_var",
        "test_table_multi_var",
        "test_merge_prime_implicants",
        "test_simplify_no_variable",
    ]
)
def test_simplify_single_var():
    # DIRECT
    assert simplify("a") == "a"
    assert simplify("(a)") == "a"
    assert simplify("((a))") == "a"

    # NOT
    assert simplify("!a") == "!a"
    assert simplify("!!a") == "a"
    assert simplify("!!!a") == "!a"
    assert simplify("!!!!a") == "a"

    # OR
    assert simplify("a") == "a"
    assert simplify("a+a") == "a"
    assert simplify("a+!a") == "1"
    assert simplify("!a+a") == "1"
    assert simplify("!a+!a") == "!a"
    assert simplify("a+a+a") == "a"
    assert simplify("a+a+!a") == "1"
    assert simplify("a+!a+a") == "1"
    assert simplify("a+!a+!a") == "1"
    assert simplify("!a+a+a") == "1"
    assert simplify("!a+a+!a") == "1"
    assert simplify("!a+!a+a") == "1"
    assert simplify("!a+!a+!a") == "!a"

    # AND
    assert simplify("a") == "a"
    assert simplify("!a") == "!a"
    assert simplify("a*a") == "a"
    assert simplify("a*!a") == "0"
    assert simplify("!a*a") == "0"
    assert simplify("!a*!a") == "!a"
    assert simplify("a*a*a") == "a"
    assert simplify("a*a*!a") == "0"
    assert simplify("a*!a*a") == "0"
    assert simplify("a*!a*!a") == "0"
    assert simplify("!a*a*a") == "0"
    assert simplify("!a*a*!a") == "0"
    assert simplify("!a*!a*a") == "0"
    assert simplify("!a*!a*!a") == "!a"

    # XOR
    assert simplify("a") == "a"
    assert simplify("!a") == "!a"
    assert simplify("a^a") == "0"
    assert simplify("a^!a") == "1"
    assert simplify("!a^a") == "1"
    assert simplify("!a^!a") == "0"
    assert simplify("a^a^a") == "a"
    assert simplify("a^a^!a") == "!a"
    assert simplify("a^!a^a") == "!a"
    assert simplify("a^!a^!a") == "a"
    assert simplify("!a^a^a") == "!a"
    assert simplify("!a^a^!a") == "a"
    assert simplify("!a^!a^a") == "a"
    assert simplify("!a^!a^!a") == "!a"


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_evaluate_basic",
        "test_evaluate_tree",
        "test_table_single_var",
        "test_table_multi_var",
        "test_merge_prime_implicants",
        "test_simplify_no_variable",
        "test_simplify_single_var",
    ]
)
def test_simplify_multi_var():
    # DIRECT
    assert simplify("a+b") == "a+b"
    assert simplify("(a+b)") == "a+b"
    assert simplify("(a)+b") == "a+b"
    assert simplify("((a))+b") == "a+b"
    assert simplify("((a))+(b)") == "a+b"
    assert simplify("((a)+a)+(b)") == "a+b"
    assert simplify("((a)+a)+(b+a)") == "a+b"

    assert simplify("a+b+c") == "a+b+c"
    assert simplify("a+b*c") == "a+(b*c)"


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_evaluate_basic",
        "test_evaluate_tree",
        "test_table_single_var",
        "test_table_multi_var",
        "test_merge_prime_implicants",
        "test_simplify_no_variable",
        "test_simplify_single_var",
        "test_simplify_multi_var",
    ]
)
def test_all():
    pass
