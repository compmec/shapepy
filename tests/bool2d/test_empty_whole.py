import pytest

from shapepy.bool2d.base import EmptyR2, WholeR2
from shapepy.bool2d.bool2d import contains, intersect, invert, unite
from shapepy.bool2d.container import expand
from shapepy.bool2d.simplify import simplify


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/bool2d/test_build.py::test_empty",
        "tests/bool2d/test_build.py::test_whole",
    ],
    scope="session",
)
def test_compare():
    empty = EmptyR2()
    whole = WholeR2()

    assert empty == empty
    assert empty != whole
    assert whole != empty
    assert whole == whole


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_compare"])
def test_expand():
    empty = EmptyR2()
    whole = WholeR2()
    assert expand(empty) == empty
    assert expand(whole) == whole


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_compare", "test_expand"])
def test_simplify():
    empty = EmptyR2()
    whole = WholeR2()
    assert simplify(empty) == empty
    assert simplify(whole) == whole


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_compare"])
def test_inverse():
    empty = EmptyR2()
    whole = WholeR2()

    assert ~empty == whole
    assert ~whole == empty

    assert -empty == whole
    assert -whole == empty

    assert invert(empty) == whole
    assert invert(whole) == empty


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_compare"])
def test_weird_compare():
    empty = EmptyR2()
    whole = WholeR2()

    weirds = ["(])"]
    for weird in weirds:
        assert empty != weird
        assert whole != weird
        assert weird != empty
        assert weird != whole


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_compare"])
def test_self_operation():
    empty = EmptyR2()
    whole = WholeR2()

    for subset in (empty, whole):
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


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_compare"])
def test_switch_operation():
    empty = EmptyR2()
    whole = WholeR2()

    assert empty | whole == whole
    assert empty & whole == empty
    assert empty ^ whole == whole
    assert empty - whole == empty
    assert empty + whole == whole
    assert empty * whole == empty

    assert whole | empty == whole
    assert whole & empty == empty
    assert whole ^ empty == whole
    assert whole - empty == whole
    assert whole + empty == whole
    assert whole * empty == empty

    assert unite(empty, whole) == whole
    assert intersect(empty, whole) == empty


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_compare"])
def test_contains():
    empty = EmptyR2()
    whole = WholeR2()

    assert empty in empty
    assert empty in whole
    assert whole not in empty
    assert whole in whole

    assert contains(empty, empty)
    assert contains(whole, empty)
    assert not contains(empty, whole)
    assert contains(whole, whole)


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_compare",
        "test_expand",
        "test_simplify",
        "test_inverse",
        "test_self_operation",
        "test_switch_operation",
        "test_contains",
    ]
)
def test_all():
    pass
