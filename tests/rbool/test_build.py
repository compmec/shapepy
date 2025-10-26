import pytest

from shapepy.rbool import EmptyR1, IntervalR1, SingleR1, WholeR1


@pytest.mark.order(12)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_begin():
    pass


@pytest.mark.order(12)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_empty():
    empty1 = EmptyR1()
    empty2 = EmptyR1()
    assert id(empty1) == id(empty2)
    assert empty1 is empty2

    hash(empty1)


@pytest.mark.order(12)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_whole():
    whole1 = WholeR1()
    whole2 = WholeR1()
    assert id(whole1) == id(whole2)
    assert whole1 is whole2

    hash(whole1)


@pytest.mark.order(12)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_single():
    SingleR1(-10)
    SingleR1(0)
    SingleR1(10)

    SingleR1(-10.0)
    SingleR1(0.0)
    SingleR1(10.0)

    with pytest.raises(ValueError):
        SingleR1(float("-inf"))
    with pytest.raises(ValueError):
        SingleR1(float("inf"))

    hash(SingleR1(10))


@pytest.mark.order(12)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_interval():
    IntervalR1(-10, 10)
    IntervalR1(float("-inf"), 10)
    IntervalR1(-10, float("inf"))
    with pytest.raises(ValueError):
        IntervalR1(float("-inf"), float("inf"))

    hash(IntervalR1(-10, 10))


@pytest.mark.order(12)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_disjoint():
    pass


@pytest.mark.order(12)
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
