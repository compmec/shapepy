import pytest

from shapepy.bool2d.base import EmptyR2, SubSetR2, WholeR2
from shapepy.bool2d.bool2d import contains, intersect, invert, unite
from shapepy.bool2d.container import ContainerNot, expand
from shapepy.bool2d.converter import from_any
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
def test_direct_compare():
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
@pytest.mark.dependency(depends=["test_direct_compare"])
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
@pytest.mark.dependency(
    depends=[
        "test_direct_compare",
        "test_invert",
    ]
)
def test_compare():
    pointa = SinglePointR2((-1, 1))
    pointb = SinglePointR2((2, 0))

    assert pointa == pointa
    assert pointa != pointb
    assert ~pointa != pointa
    assert ~pointa != pointb
    assert ~pointa == ~pointa
    assert ~pointa != ~pointb
    assert pointa != ~pointa
    assert pointa != ~pointb

    assert pointa == {(-1, 1)}
    assert {(-1, 1)} == pointa
    assert pointa != {(2, 0)}
    assert {(2, 0)} != pointa


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_compare"])
def test_weird_compare():
    point = SinglePointR2((-1, 1))

    weirds = ["(])"]
    for weird in weirds:
        assert point != weird
        assert ~point != weird
        assert weird != point
        assert weird != ~point


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_compare"])
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


class TestSelfOperation:

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_or(self):
        whole = WholeR2()

        points = [(0, 0), (1, 1), (-1, -1)]
        points = map(SinglePointR2, points)
        for subset in points:
            assert subset | subset == subset
            assert simplify(subset | (~subset)) == whole
            assert simplify((~subset) | subset) == whole
            assert (~subset) | (~subset) == ~subset

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_and(self):
        empty = EmptyR2()

        points = [(0, 0), (1, 1), (-1, -1)]
        points = map(SinglePointR2, points)
        for subset in points:
            assert subset & subset == subset
            assert simplify(subset & (~subset)) == empty
            assert simplify((~subset) & subset) == empty
            assert (~subset) & (~subset) == ~subset

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=["TestSelfOperation::test_or", "TestSelfOperation::test_and"]
    )
    def test_xor(self):
        empty = EmptyR2()
        whole = WholeR2()

        points = [(0, 0), (1, 1), (-1, -1)]
        points = map(SinglePointR2, points)
        for subset in points:
            assert subset ^ subset == empty
            assert subset ^ (~subset) == whole
            assert (~subset) ^ subset == whole
            assert (~subset) ^ (~subset) == empty

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestSelfOperation::test_and"])
    def test_sub(self):
        empty = EmptyR2()

        points = [(0, 0), (1, 1), (-1, -1)]
        points = map(SinglePointR2, points)
        for subset in points:
            assert subset - subset == empty
            assert subset - (~subset) == subset
            assert (~subset) - subset == ~subset
            assert (~subset) - (~subset) == empty

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestSelfOperation::test_or"])
    def test_add(self):
        whole = WholeR2()

        points = [(0, 0), (1, 1), (-1, -1)]
        points = map(SinglePointR2, points)
        for subset in points:
            assert subset + subset == subset
            assert subset + (~subset) == whole
            assert (~subset) + subset == whole
            assert (~subset) + (~subset) == ~subset

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestSelfOperation::test_and"])
    def test_mul(self):
        empty = EmptyR2()

        points = [(0, 0), (1, 1), (-1, -1)]
        points = map(SinglePointR2, points)
        for subset in points:
            assert subset * subset == subset
            assert subset * (~subset) == empty
            assert (~subset) * subset == empty
            assert (~subset) * (~subset) == ~subset

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestSelfOperation::test_or"])
    def test_unite(self):
        whole = WholeR2()

        points = [(0, 0), (1, 1), (-1, -1)]
        points = map(SinglePointR2, points)
        for subset in points:
            assert unite(subset, subset) == subset
            assert simplify(unite(subset, ~subset)) == whole
            assert simplify(unite(~subset, subset)) == whole
            assert unite(~subset, ~subset) == ~subset

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestSelfOperation::test_and"])
    def test_intersect(self):
        empty = EmptyR2()

        points = [(0, 0), (1, 1), (-1, -1)]
        points = map(SinglePointR2, points)
        for subset in points:
            assert intersect(subset, subset) == subset
            assert intersect(~subset, ~subset) == ~subset
            assert simplify(intersect(subset, ~subset)) == empty
            assert simplify(intersect(~subset, subset)) == empty

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestSelfOperation::test_or",
            "TestSelfOperation::test_and",
            "TestSelfOperation::test_xor",
            "TestSelfOperation::test_sub",
            "TestSelfOperation::test_add",
            "TestSelfOperation::test_mul",
            "TestSelfOperation::test_unite",
            "TestSelfOperation::test_intersect",
        ]
    )
    def test_all(self):
        pass


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_print():
    origin = SinglePointR2((0, 0))

    str(origin)
    repr(origin)


class TestConvert:

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_build"])
    def test_single_from_string(self):
        obj = r"{(-10, 10)}"
        subset = from_any(obj)
        assert isinstance(subset, SubSetR2)
        assert isinstance(subset, SinglePointR2)
        assert subset.internal == (-10, 10)

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_build"])
    def test_single_from_set(self):
        obj = {(-10, 10)}
        subset = from_any(obj)
        assert isinstance(subset, SubSetR2)
        assert isinstance(subset, SinglePointR2)
        assert subset.internal == (-10, 10)

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=["test_contains", "TestConvert::test_single_from_string"]
    )
    def test_disjoint_from_string(self):
        obj = r"{(-10, 10), (10, -10)}"
        subset = from_any(obj)
        assert isinstance(subset, SubSetR2)
        for point in [(-10, 10), (10, -10)]:
            assert SinglePointR2(point) in subset

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestConvert::test_single_from_set"])
    def test_disjoint_from_set(self):
        obj = {(-10, 10), (10, -10)}
        subset = from_any(obj)
        assert isinstance(subset, SubSetR2)
        for point in [(-10, 10), (10, -10)]:
            assert SinglePointR2(point) in subset

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestConvert::test_single_from_string"])
    def test_container_not(self):
        obj = r"NOT[{(-10, 10)}]"
        subset = from_any(obj)
        assert isinstance(subset, SubSetR2)
        assert isinstance(subset, ContainerNot)
        assert isinstance(~subset, SinglePointR2)

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestConvert::test_single_from_string"])
    def test_container_or(self):
        obj = r"OR[{(-10, 10)}, {(10, -10)}]"
        subset = from_any(obj)
        assert isinstance(subset, SubSetR2)
        for point in [(-10, 10), (10, -10)]:
            point = SinglePointR2(point)
            assert point in subset

    @pytest.mark.order(25)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestConvert::test_single_from_string"])
    def test_container_and(self):
        obj = r"AND[NOT[{(-10, 10)}], NOT[{(10, -10)}]]"
        subset = from_any(obj)
        assert isinstance(subset, SubSetR2)
        for point in [(-10, 10), (10, -10)]:
            point = SinglePointR2(point)
            assert point not in subset


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
        "TestSelfOperation::test_all",
    ]
)
def test_all():
    pass
