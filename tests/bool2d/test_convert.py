import pytest

from shapepy.bool2d.base import EmptyR2
from shapepy.bool2d.bool2d import intersect, invert, unite
from shapepy.bool2d.converter import from_any
from shapepy.bool2d.singles import PointR2


@pytest.mark.order(55)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_from_string():
    assert from_any(r"{}") == EmptyR2()
    assert from_any(r"{(-10, 10)}") == PointR2((-10, 10))

    text = "NOT[{(-10, 10)}]"
    subset = invert(PointR2((-10, 10)))
    assert from_any(text) == subset

    text = "OR[{(-10, 10)}, {(10, 10)}]"
    union = unite(PointR2((-10, 10)), PointR2((10, 10)))
    assert from_any(text) == union

    text = "AND[{(-10, 10)}, {(10, 10)}]"
    subset = intersect(PointR2((-10, 10)), PointR2((10, 10)))
    assert from_any(text) == subset


@pytest.mark.order(55)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_from_set():
    assert from_any(set()) == EmptyR2()

    obj = {(-10, 10), (10, 10)}
    points = [(-10, 10), (10, 10)]
    union = unite(*map(PointR2, points))
    assert from_any(obj) == union


@pytest.mark.order(55)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_from_dict():
    assert from_any({}) == EmptyR2()


@pytest.mark.order(55)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_from_string",
        "test_from_set",
        "test_from_dict",
    ]
)
def test_all():
    pass
