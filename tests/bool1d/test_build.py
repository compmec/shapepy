import pytest

from shapepy.bool1d import EmptyR1, IntervalR1, SingleValueR1, WholeR1


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/test_default.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_empty():
    empty1 = EmptyR1()
    empty2 = EmptyR1()
    assert id(empty1) == id(empty2)
    assert empty1 is empty2

    hash(empty1)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_whole():
    whole1 = WholeR1()
    whole2 = WholeR1()
    assert id(whole1) == id(whole2)
    assert whole1 is whole2

    hash(whole1)


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_single():
    SingleValueR1(-10)
    SingleValueR1(0)
    SingleValueR1(10)

    SingleValueR1(-10.0)
    SingleValueR1(0.0)
    SingleValueR1(10.0)

    with pytest.raises(ValueError):
        SingleValueR1(float("-inf"))
    with pytest.raises(ValueError):
        SingleValueR1(float("inf"))

    hash(SingleValueR1(10))


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_interval():
    IntervalR1(-10, 10)
    IntervalR1(float("-inf"), 10)
    IntervalR1(-10, float("inf"))
    with pytest.raises(ValueError):
        IntervalR1(float("-inf"), float("inf"))

    hash(IntervalR1(-10, 10))


@pytest.mark.order(2)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_disjoint():
    pass


@pytest.mark.order(2)
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
