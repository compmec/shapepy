"""
Tests related to Parameter
"""

import pytest

from shapepy.parameter import (
    DisjointParameters,
    EmptyParameter,
    ParamInterval,
    WholeParameter,
)


@pytest.mark.order(1)
@pytest.mark.dependency()
def test_begin():
    pass


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_constructor():
    empty = EmptyParameter()
    assert isinstance(empty, EmptyParameter)
    str(empty)
    repr(empty)

    whole = WholeParameter()
    assert isinstance(whole, WholeParameter)
    str(whole)
    repr(whole)

    with pytest.raises(ValueError):
        ParamInterval(3, -3)


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_constructor"])
def test_singleton():
    empty1 = EmptyParameter()
    empty2 = EmptyParameter()
    assert id(empty1) == id(empty2)

    whole1 = WholeParameter()
    whole2 = WholeParameter()
    assert id(whole1) == id(whole2)


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_constructor"])
def test_compare():
    empty = EmptyParameter()
    whole = WholeParameter()
    inters = ParamInterval(-1, 1)

    assert empty == empty
    assert empty != whole
    assert whole != empty
    assert whole == whole

    assert empty != 0
    assert empty != inters
    assert whole != 0
    assert whole != inters

    assert 0 != empty
    assert inters != empty
    assert 0 != whole
    assert inters != whole


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_singleton"])
def test_contains_singleton():
    empty = EmptyParameter()
    whole = WholeParameter()

    assert empty in empty
    assert empty in whole
    assert whole not in empty
    assert whole in whole


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_singleton"])
def test_or_singleton():
    empty = EmptyParameter()
    whole = WholeParameter()

    assert empty | empty is empty
    assert empty | whole is whole
    assert whole | empty is whole
    assert whole | whole is whole


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_singleton"])
def test_and_singleton():
    empty = EmptyParameter()
    whole = WholeParameter()
    assert empty & empty is empty
    assert empty & whole is empty
    assert whole & empty is empty
    assert whole & whole is whole


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_or_singleton", "test_and_singleton"])
def test_single_parameter():
    empty = EmptyParameter()
    whole = WholeParameter()
    for value in (-1, 0, 1):
        assert empty | value is value
        assert whole | value is whole
        assert empty & value is empty
        assert whole & value is value

        assert value | empty is value
        assert value | whole is whole
        assert value & empty is empty
        assert value & whole is value

        # assert empty in val
        assert value not in empty
        assert value in whole
        # assert whole not in val


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_or_singleton",
        "test_and_singleton",
        "test_single_parameter",
    ]
)
def test_intervals():
    empty = EmptyParameter()
    whole = WholeParameter()
    intera = ParamInterval(-3, 2)
    interb = ParamInterval(-2, 3)
    interc = ParamInterval(-1, 1)

    for inter in (intera, interb, interc):
        assert empty | inter is inter
        assert whole | inter is whole
        assert empty & inter is empty
        assert whole & inter is inter

        assert inter | empty is inter
        assert inter | whole is whole
        assert inter & empty is empty
        assert inter & whole is inter

        assert empty in inter
        assert inter not in empty
        assert inter in whole
        assert whole not in inter

    assert intera | interb == ParamInterval(-3, 3)
    assert intera & interb == ParamInterval(-2, 2)

    intera = ParamInterval(-3, -2)
    interb = ParamInterval(2, 3)
    assert intera & interb is empty
    union = intera | interb
    assert isinstance(union, DisjointParameters)
    assert len(union) == 2
    assert union[0] == intera
    assert union[1] == interb

    intera = ParamInterval(-3, 0)
    interb = ParamInterval(0, 3)
    assert intera | interb == ParamInterval(-3, 3)
    assert intera & interb == 0

    intera = ParamInterval(ParamInterval.botinf, 2)
    interb = ParamInterval(-2, ParamInterval.topinf)
    assert intera | interb is whole
    assert intera & interb == ParamInterval(-2, 2)


@pytest.mark.order(1)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_or_singleton",
        "test_and_singleton",
        "test_single_parameter",
    ]
)
def test_printing():
    empty = EmptyParameter()
    whole = WholeParameter()
    intera = ParamInterval(-3, -2)
    interb = ParamInterval(2, 3)

    assert str(empty) == r"{}"
    assert str(whole) == "(-inf, inf)"
    assert str(intera) == "[-3, -2]"
    assert str(interb) == "[2, 3]"

    union = intera | interb
    assert str(union) == "[-3, -2] U [2, 3]"
    union |= 0
    assert str(union) == r"[-3, -2] U {0} U [2, 3]"
    union |= 4
    assert str(union) == r"[-3, -2] U {0} U [2, 3] U {4}"
    union |= -1
    assert str(union) == r"[-3, -2] U {-1, 0} U [2, 3] U {4}"

    for val in (-3, -2.5, -2, -1, 0, 2, 2.5, 3, 4):
        assert union & val == val
    for val in (-1.5, 1, 6):
        assert union & val is empty


@pytest.mark.order(1)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "test_or_singleton",
        "test_and_singleton",
        "test_single_parameter",
        "test_intervals",
    ]
)
def test_inverse_operation():
    empty = EmptyParameter()
    whole = WholeParameter()
    params = tuple(range(-4, 5))
    params = params + (ParamInterval.botinf, ParamInterval.topinf)
    inters = []
    for parama in params:
        for paramb in params:
            if paramb <= parama:
                continue
            try:
                interval = ParamInterval(parama, paramb)
            except ValueError:
                continue
            inters.append(interval)
    objas = inters + [empty, whole]
    objbs = list(params) + inters + [empty, whole]
    for obja in objas:
        assert obja | obja == obja
        assert obja & obja == obja
        for objb in objbs:
            assert obja | objb == objb | obja
            assert obja & objb == objb & obja


@pytest.mark.order(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_constructor",
        "test_singleton",
        "test_or_singleton",
        "test_and_singleton",
        "test_single_parameter",
        "test_intervals",
        "test_inverse_operation",
        "test_printing",
    ]
)
def test_end():
    pass
