import pytest

from shapepy import default
from shapepy.bool1d import (
    DisjointR1,
    EmptyR1,
    IntervalR1,
    SingleValueR1,
    WholeR1,
    bigger,
    from_any,
    lower,
)


@pytest.mark.order(15)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/bool1d/test_build.py::test_all",
        "tests/bool1d/test_convert.py::test_all",
        "tests/bool1d/test_compare.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(15)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_singleton_in_singleton():
    empty = EmptyR1()
    whole = WholeR1()

    assert empty in empty
    assert empty in whole

    assert whole not in empty
    assert whole in whole


@pytest.mark.order(15)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_singleton_contains_object():
    empty = EmptyR1()
    whole = WholeR1()

    values = (-100, -50, -20, -10, 0, 10, 20, 50, 100)
    singls = tuple(map(SingleValueR1, values))
    for value in values:
        assert value not in empty
        assert value in whole
    for single in singls:
        assert empty in single
        assert whole not in single
        assert single not in empty
        assert single in whole

    NEGINF = default.NEGINF
    POSINF = default.POSINF
    aval, bval = -10, 10

    n2a = IntervalR1(NEGINF, aval)
    n2b = IntervalR1(NEGINF, bval)
    a2b = IntervalR1(aval, bval)
    a2p = IntervalR1(aval, POSINF)
    b2p = IntervalR1(bval, POSINF)
    intervals = (n2a, n2b, a2b, a2p, b2p)
    for interval in intervals:
        assert empty in interval
        assert whole not in interval
        assert interval not in empty
        assert interval in whole


@pytest.mark.order(15)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_interval_contains_interval():

    NEGINF = default.NEGINF
    POSINF = default.POSINF
    aval, bval = -10, 10

    n2a = IntervalR1(NEGINF, aval)
    n2b = IntervalR1(NEGINF, bval)
    a2b = IntervalR1(aval, bval)
    a2p = IntervalR1(aval, POSINF)
    b2p = IntervalR1(bval, POSINF)

    assert n2a in n2a
    assert n2a in n2b
    assert n2a not in a2b
    assert n2a not in a2p
    assert n2a not in b2p

    assert n2b not in n2a
    assert n2b in n2b
    assert n2b not in a2b
    assert n2b not in a2p
    assert n2b not in b2p

    assert a2b not in n2a
    assert a2b in n2b
    assert a2b in a2b
    assert a2b in a2p
    assert a2b not in b2p

    assert a2p not in n2a
    assert a2p not in n2b
    assert a2p not in a2b
    assert a2p in a2p
    assert a2p not in b2p

    assert b2p not in n2a
    assert b2p not in n2b
    assert b2p not in a2b
    assert b2p in a2p
    assert b2p in b2p

    assert IntervalR1(-50, -20) not in IntervalR1(0, 20)
    assert IntervalR1(10, 50) not in IntervalR1(0, 20)
    assert IntervalR1(-10, 10) in IntervalR1(-20, 20)
    assert IntervalR1(-10, 10, True, True) not in IntervalR1(
        -20, 10, True, False
    )
    assert IntervalR1(-10, 10, True, True) not in IntervalR1(
        -10, 20, False, True
    )


@pytest.mark.order(15)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_disjoint_contains_object():
    blocks = [
        "(-inf, -20)",
        "[-10, -5]",
        "[0, 5)",
        "(10, 15]",
        "(20, 25)",
        "{30, 31, 33}",
    ]
    string = " U ".join(blocks)
    disjoint = from_any(string)
    assert isinstance(disjoint, DisjointR1)

    inside = {-25, -10, -7, -5, 0, 2, 12, 15, 22, 30, 31, 33}
    outside = {-20, -15, -2, 5, 7, 10, 17, 20, 25, 28, 32}
    for value in inside:
        assert value in disjoint
    for value in outside:
        assert value not in disjoint

    assert disjoint == string
    assert disjoint != {30, 31}
    assert disjoint != [-10, -5]
    assert disjoint != {30}
    assert disjoint != EmptyR1()
    assert disjoint != WholeR1()

    assert {30, 31} in disjoint
    assert [-10, -5] in disjoint
    assert {30} in disjoint
    assert EmptyR1() in disjoint
    assert WholeR1() not in disjoint


@pytest.mark.order(15)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_infinity():
    empty = EmptyR1()
    assert default.NEGINF not in empty
    assert default.POSINF not in empty

    whole = WholeR1()
    assert default.NEGINF in whole
    assert default.POSINF in whole

    for value in (-10, -1, 0, 1, 10):
        assert default.NEGINF not in SingleValueR1(value)
        assert default.POSINF not in SingleValueR1(value)

    interval = lower(0)
    assert default.NEGINF in interval
    assert default.POSINF not in interval

    interval = bigger(0)
    assert default.NEGINF not in interval
    assert default.POSINF in interval

    interval = IntervalR1(-10, 10)
    assert default.NEGINF not in interval
    assert default.POSINF not in interval

    blocks = [
        "(-inf, -20)",
        "[-10, -5]",
        "[0, 5)",
        "(10, 15]",
        "(20, 25)",
        "{30, 31, 33}",
    ]
    string = " U ".join(blocks)
    disjoint = from_any(string)
    assert isinstance(disjoint, DisjointR1)

    assert default.NEGINF in disjoint
    assert default.POSINF not in disjoint


@pytest.mark.order(15)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_singleton_in_singleton",
        "test_singleton_contains_object",
        "test_interval_contains_interval",
        "test_disjoint_contains_object",
        "test_infinity",
    ]
)
def test_all():
    pass
