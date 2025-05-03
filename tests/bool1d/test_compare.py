import pytest

from shapepy import default
from shapepy.bool1d import EmptyR1, IntervalR1, SingleValueR1, WholeR1


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

    assert empty == empty
    assert empty == {}
    assert empty == r"{}"


@pytest.mark.order(14)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_whole():
    whole = WholeR1()
    NEGINF = default.NEGINF
    POSINF = default.POSINF

    assert whole == whole
    assert whole == (float("-inf"), float("inf"))
    assert whole == (float("-inf"), POSINF)
    assert whole == (NEGINF, float("inf"))
    assert whole == (NEGINF, POSINF)
    assert whole == [float("-inf"), float("inf")]
    assert whole == [float("-inf"), POSINF]
    assert whole == [NEGINF, float("inf")]
    assert whole == [NEGINF, POSINF]
    assert whole == r"(-inf, inf)"


@pytest.mark.order(14)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_empty", "test_whole"])
def test_singletons():
    empty = EmptyR1()
    whole = WholeR1()

    assert empty == empty
    assert empty != whole
    assert whole != empty
    assert whole == whole

    assert not empty != empty
    assert not empty == whole
    assert not whole == empty
    assert not whole != whole


@pytest.mark.order(14)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_singletons"])
def test_singles():
    empty = EmptyR1()
    whole = WholeR1()

    for value in (-10, 0, 10):
        single = SingleValueR1(value)
        assert single == single
        assert single == value
        assert single == {value}
        assert single == "{" + str(value) + "}"

        assert single != empty
        assert empty != single
        assert single != whole
        assert whole != single

        assert not single == empty
        assert not empty == single
        assert not single == whole
        assert not whole == single


@pytest.mark.order(14)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_singletons", "test_singles"])
def test_intervals():
    empty = EmptyR1()
    whole = WholeR1()

    NEGINF = default.NEGINF
    POSINF = default.POSINF
    aval, bval = -10, 10

    n2a = IntervalR1(NEGINF, aval)
    n2b = IntervalR1(NEGINF, bval)
    a2b = IntervalR1(aval, bval)
    a2p = IntervalR1(aval, POSINF)
    b2p = IntervalR1(bval, POSINF)

    intervals = (n2a, n2b, a2b, a2p, b2p)
    for i, intvi in enumerate(intervals):
        for j, intvj in enumerate(intervals):
            if i == j:
                assert intvi == intvj
            else:
                assert intvi != intvj

    for interv in intervals:
        assert empty != interv
        assert whole != interv
        assert interv != empty
        assert interv != whole

        assert not empty == interv
        assert not whole == interv
        assert not interv == empty
        assert not interv == whole

    closed_pairs = [
        (-50, 50),
        (-50, -20),
        (20, 50),
        (NEGINF, -20),
        (NEGINF, 0),
        (NEGINF, 20),
        (-20, POSINF),
        (0, POSINF),
        (20, POSINF),
    ]
    for sta, end in closed_pairs:
        interv = IntervalR1(sta, end, True, True)
        assert interv == [sta, end]
        assert [sta, end] == interv

    open_pairs = [
        (-50, 50),
        (-50, -20),
        (20, 50),
        (NEGINF, -20),
        (NEGINF, 0),
        (NEGINF, 20),
        (-20, POSINF),
        (0, POSINF),
        (20, POSINF),
    ]
    for sta, end in open_pairs:
        interv = IntervalR1(sta, end, False, False)
        assert interv == (sta, end)
        assert (sta, end) == interv


@pytest.mark.order(14)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_singletons",
        "test_singles",
        "test_intervals",
    ]
)
def test_all():
    pass
