import pytest

from shapepy.bool1d import (
    DisjointR1,
    EmptyR1,
    IntervalR1,
    SingleValueR1,
    WholeR1,
    bigger,
    lower,
)


@pytest.mark.order(14)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/bool1d/test_build.py::test_all",
        "tests/bool1d/test_convert.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(14)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_empty():
    empty = EmptyR1()
    assert str(empty) == r"{}"
    assert repr(empty) == r"EmptyR1"


@pytest.mark.order(14)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_whole():
    whole = WholeR1()
    assert str(whole) == r"(-inf, inf)"
    assert repr(whole) == r"WholeR1"


@pytest.mark.order(14)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_single():
    value = SingleValueR1(-10)
    assert str(value) == r"{-10}"
    assert repr(value) == r"SingleValueR1(-10)"

    value = SingleValueR1(0)
    assert str(value) == r"{0}"
    assert repr(value) == r"SingleValueR1(0)"

    value = SingleValueR1(10)
    assert str(value) == r"{10}"
    assert repr(value) == r"SingleValueR1(10)"


@pytest.mark.order(14)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_interval():
    interval = IntervalR1(-10, 10, True, True)
    assert str(interval) == r"[-10, 10]"

    interval = IntervalR1(-10, 10, True, False)
    assert str(interval) == r"[-10, 10)"

    interval = IntervalR1(-10, 10, False, True)
    assert str(interval) == r"(-10, 10]"

    interval = IntervalR1(-10, 10, False, False)
    assert str(interval) == r"(-10, 10)"

    interval = lower(10, True)
    assert str(interval) == r"(-inf, 10]"

    interval = lower(10, False)
    assert str(interval) == r"(-inf, 10)"

    interval = bigger(-10, True)
    assert str(interval) == r"[-10, inf)"

    interval = bigger(-10, False)
    assert str(interval) == r"(-10, inf)"


@pytest.mark.order(14)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_disjoint():
    interv0 = lower(-50)
    interv1 = bigger(50)
    disjoint = DisjointR1([interv0, interv1])
    assert str(disjoint) == "(-inf, -50] U [50, inf)"
    repr(disjoint)

    interv2 = IntervalR1(-20, 20)
    singles = list(map(SingleValueR1, [-30, -25, 25, 30, 40]))
    disjoint = DisjointR1([interv0, interv1, interv2] + singles)
    blocks = [
        "(-inf, -50]",
        "{-30, -25}",
        "[-20, 20]",
        "{25, 30, 40}",
        "[50, inf)",
    ]
    assert str(disjoint) == " U ".join(blocks)
    repr(disjoint)

    disjoint = DisjointR1([interv0, interv2] + singles)
    blocks = ["(-inf, -50]", "{-30, -25}", "[-20, 20]", "{25, 30, 40}"]
    assert str(disjoint) == " U ".join(blocks)
    repr(disjoint)

    disjoint = DisjointR1(singles)
    assert str(disjoint) == "{-30, -25, 25, 30, 40}"
    repr(disjoint)


@pytest.mark.order(14)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_single",
        "test_interval",
        "test_disjoint",
    ]
)
def test_all():
    pass
