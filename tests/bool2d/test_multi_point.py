import pytest

from shapepy.bool2d.base import EmptyR2, SubSetR2, WholeR2
from shapepy.bool2d.bool2d import contains, intersect, invert, unite
from shapepy.bool2d.container import ContainerNot, expand
from shapepy.bool2d.converter import from_any
from shapepy.bool2d.simplify import simplify
from shapepy.bool2d.singles import SinglePointR2


@pytest.mark.order(26)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/bool2d/test_single_point.py::test_all",
    ],
    scope="session",
)
def test_build():
    points = [(-10, 0), (3, 4), (-3, -4), (5, 6)]
    singles = tuple(map(SinglePointR2, points))
    unite(*singles)
    intersect(*map(invert, singles))


@pytest.mark.order(26)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build"])
def test_hash():
    points = [(-10, 0), (3, 4), (-3, -4), (5, 6)]
    singles = tuple(map(SinglePointR2, points))
    union = unite(*singles)
    inter = intersect(*map(invert, singles))

    assert hash(union) + hash(inter) == 0


@pytest.mark.order(26)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build"])
def test_contains():
    points = [(-10, 0), (3, 4), (-3, -4), (5, 6)]
    singles = tuple(map(SinglePointR2, points))
    union = unite(*singles)
    inter = intersect(*map(invert, singles))

    for single in singles:
        assert single in union
        assert single not in inter
        assert contains(union, single)
        assert not contains(inter, single)

        assert union not in single
        assert inter not in single
        assert not contains(single, union)
        assert not contains(single, inter)


@pytest.mark.order(26)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build"])
def test_expand():
    points = [(-10, 0), (3, 4), (-3, -4), (5, 6)]
    singles = tuple(map(SinglePointR2, points))
    union = unite(*singles)
    inter = intersect(*map(invert, singles))

    assert expand(union) == union
    assert expand(inter) == inter

    assert expand(~union) == inter
    assert expand(~inter) == union


@pytest.mark.order(26)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build"])
def test_simplify():
    points = [(-10, 0), (3, 4), (-3, -4), (5, 6)]
    singles = tuple(map(SinglePointR2, points))
    union = unite(*singles)
    inter = intersect(*map(invert, singles))

    assert simplify(union) == union
    assert simplify(inter) == inter

    assert simplify(~union) == inter
    assert simplify(~inter) == union


@pytest.mark.order(26)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_build"])
def test_weird_compare():
    points = [(-10, 0), (3, 4), (-3, -4), (5, 6)]
    singles = tuple(map(SinglePointR2, points))
    union = unite(*singles)
    inter = intersect(*map(invert, singles))

    weirds = ["([)"]
    for weird in weirds:
        assert union != weird
        assert inter != weird
        assert weird != union
        assert weird != inter


@pytest.mark.order(26)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_build",
        "test_hash",
        "test_contains",
        "test_expand",
        "test_simplify",
        "test_weird_compare",
    ]
)
def test_all():
    pass
