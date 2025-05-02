import pytest

from shapepy.bool2d.base import EmptyR2, WholeR2
from shapepy.bool2d.bool2d import invert
from shapepy.bool2d.container import ContainerNot, expand
from shapepy.bool2d.simplify import simplify
from shapepy.bool2d.singles import SinglePointR2


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_build():
    SinglePointR2((0, 0))
    SinglePointR2((1, 1))


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build"])
def test_compare():
    pointa = SinglePointR2((0, 0))
    pointb = SinglePointR2((0, 0))
    pointc = SinglePointR2((1, 1))

    assert pointa == pointb
    assert pointc != pointa


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_empty_whole():
    empty = EmptyR2()
    whole = WholeR2()
    point = SinglePointR2((0, 0))

    assert point != empty
    assert point != whole
    assert empty != point
    assert whole != point

    assert point not in empty
    assert point in whole
    assert empty in point
    assert whole not in point


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_expand():
    point = SinglePointR2((0, 0))
    assert expand(point) == point


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_simplify():
    point = SinglePointR2((0, 0))
    assert simplify(point) == point


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_invert():
    point = SinglePointR2((0, 0))
    assert ~point == ContainerNot(point)
    assert -point == ContainerNot(point)
    assert invert(point) == ContainerNot(point)


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_print():
    origin = SinglePointR2((0, 0))

    str(origin)
    repr(origin)


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_build",
        "test_compare",
        "test_empty_whole",
        "test_expand",
        "test_simplify",
        "test_print",
    ]
)
def test_all():
    pass
