import pytest

from shapepy.bool2d.base import EmptyR2, WholeR2
from shapepy.bool2d.bool2d import contains, intersect, invert, unite
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
def test_contains():
    pointa = SinglePointR2((0, 0))
    pointb = SinglePointR2((10, -10))
    pointc = SinglePointR2((-3, 7))
    points = (pointa, pointb, pointc)

    for point in points:
        assert EmptyR2() in point

    for i, pointi in enumerate(points):
        assert pointi in pointi
        assert pointi not in (~pointi)
        assert (~pointi) not in pointi
        assert (~pointi) in (~pointi)

        assert contains(pointi, pointi)
        assert not contains(pointi, ~pointi)
        assert not contains(~pointi, pointi)
        assert contains(~pointi, ~pointi)

        for j, pointj in enumerate(points):
            if i == j:
                continue

            assert pointi not in pointj
            assert (~pointi) not in pointj
            assert pointi in (~pointj)
            assert (~pointi) not in (~pointj)

            assert not contains(pointi, pointj)
            assert not contains(pointi, ~pointj)
            assert contains(~pointi, pointj)
            assert not contains(~pointi, ~pointj)


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_self_operation():
    empty = EmptyR2()
    whole = WholeR2()

    points = [(0, 0), (1, 1), (-1, -1)]
    points = map(SinglePointR2, points)
    for subset in points:
        assert subset | subset == subset
        assert subset & subset == subset
        assert subset ^ subset == empty
        assert subset - subset == empty
        assert subset + subset == subset
        assert subset * subset == subset
        assert unite(subset, subset, subset) == subset
        assert intersect(subset, subset, subset) == subset

        assert subset | (~subset) == whole
        assert subset & (~subset) == empty
        assert subset ^ (~subset) == whole
        assert subset - (~subset) == subset
        assert subset + (~subset) == whole
        assert subset * (~subset) == empty
        assert unite(subset, ~subset) == whole
        assert intersect(subset, ~subset) == empty

        assert (~subset) | subset == whole
        assert (~subset) & subset == empty
        assert (~subset) ^ subset == whole
        assert (~subset) - subset == ~subset
        assert (~subset) + subset == whole
        assert (~subset) * subset == empty
        assert unite(~subset, subset) == whole
        assert intersect(~subset, subset) == empty

        assert (~subset) | (~subset) == ~subset
        assert (~subset) & (~subset) == ~subset
        assert (~subset) ^ (~subset) == empty
        assert (~subset) - (~subset) == empty
        assert (~subset) + (~subset) == ~subset
        assert (~subset) * (~subset) == ~subset
        assert unite(~subset, ~subset) == ~subset
        assert intersect(~subset, ~subset) == ~subset


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
