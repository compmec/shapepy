"""
Tests related to 'Empty' and 'Whole' which describes a empty set
and the whole domain
"""

from copy import copy

import pytest

from shapepy.core import Empty, Whole


@pytest.mark.order(1)
@pytest.mark.dependency()
def test_begin():
    pass


@pytest.mark.order(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_constructor():
    empty = Empty()
    assert isinstance(empty, Empty)

    whole = Whole()
    assert isinstance(whole, Whole)


@pytest.mark.order(1)
@pytest.mark.dependency(depends=["test_constructor"])
def test_singleton():
    empty1 = Empty()
    empty2 = Empty()
    assert id(empty1) == id(empty2)

    whole1 = Whole()
    whole2 = Whole()
    assert id(whole1) == id(whole2)


@pytest.mark.order(1)
@pytest.mark.dependency(depends=["test_singleton"])
def test_inverse():
    empty = Empty()
    whole = Whole()
    assert ~empty is whole
    assert ~whole is empty


@pytest.mark.order(1)
@pytest.mark.dependency(depends=["test_singleton"])
def test_or():
    empty = Empty()
    whole = Whole()
    assert empty | empty is empty
    assert empty | whole is whole
    assert whole | empty is whole
    assert whole | whole is whole

    assert empty + empty is empty
    assert empty + whole is whole
    assert whole + empty is whole
    assert whole + whole is whole


@pytest.mark.order(1)
@pytest.mark.dependency(depends=["test_singleton"])
def test_and():
    empty = Empty()
    whole = Whole()
    assert empty & empty is empty
    assert empty & whole is empty
    assert whole & empty is empty
    assert whole & whole is whole

    assert empty * empty is empty
    assert empty * whole is empty
    assert whole * empty is empty
    assert whole * whole is whole


@pytest.mark.order(1)
@pytest.mark.dependency(depends=["test_inverse", "test_or", "test_and"])
def test_xor():
    empty = Empty()
    whole = Whole()
    assert empty ^ empty is empty
    assert empty ^ whole is whole
    assert whole ^ empty is whole
    assert whole ^ whole is empty


@pytest.mark.order(1)
@pytest.mark.dependency(depends=["test_inverse", "test_or", "test_and"])
def test_sub():
    empty = Empty()
    whole = Whole()
    assert empty - empty is empty
    assert empty - whole is empty
    assert whole - empty is whole
    assert whole - whole is empty


@pytest.mark.order(1)
@pytest.mark.dependency(depends=["test_singleton"])
def test_copy():
    empty = Empty()
    whole = Whole()
    assert copy(empty) is empty
    assert copy(whole) is whole


@pytest.mark.order(1)
@pytest.mark.dependency(depends=["test_constructor"])
def test_string():
    empty = Empty()
    whole = Whole()
    assert str(empty) == "Empty"
    assert str(whole) == "Whole"
    assert repr(empty) == "Empty"
    assert repr(whole) == "Whole"


@pytest.mark.order(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_constructor",
        "test_singleton",
        "test_inverse",
        "test_or",
        "test_and",
        "test_xor",
        "test_sub",
        "test_copy",
        "test_string",
    ]
)
def test_end():
    pass
