"""File to test the functions `move`, `scale` and `rotate`"""

from copy import copy, deepcopy

import pytest

from shapepy.bool2d.point import SinglePoint
from shapepy.geometry.point import cartesian, polar
from shapepy.scalar.angle import degrees
from shapepy.scalar.reals import Math


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "tests/geometry/test_point.py::test_all",
        "tests/bool2d/test_empty_whole.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(22)
@pytest.mark.dependency(depends=["test_begin"])
def test_build():
    SinglePoint(cartesian(0, 0))
    SinglePoint(cartesian(1, 0))
    SinglePoint(cartesian(0, 1))
    SinglePoint(cartesian(-1, 0))

    with pytest.raises(ValueError):
        SinglePoint(polar(Math.POSINF, 0))


@pytest.mark.order(22)
@pytest.mark.dependency(depends=["test_begin"])
def test_move():
    subset = SinglePoint(cartesian(0, 0))
    assert subset.move((1, 2)) == SinglePoint(cartesian(1, 2))

    subset = SinglePoint(cartesian(-1, 2))
    assert subset.move((-3, 5)) == SinglePoint(cartesian(-4, 7))


@pytest.mark.order(22)
@pytest.mark.dependency(depends=["test_begin"])
def test_scale():
    subset = SinglePoint(cartesian(0, 0))
    assert subset.scale(2) == SinglePoint(cartesian(0, 0))

    subset = SinglePoint(cartesian(-1, 2))
    assert subset.scale(2) == SinglePoint(cartesian(-2, 4))


@pytest.mark.order(22)
@pytest.mark.dependency(depends=["test_begin"])
def test_rotate():
    subset = SinglePoint(cartesian(-1, 2))
    assert subset.rotate(degrees(90)) == SinglePoint(cartesian(-2, -1))


@pytest.mark.order(22)
@pytest.mark.dependency(depends=["test_begin"])
def test_density():
    subset = SinglePoint(cartesian(-1, 2))

    assert subset.density((0, 0)) == 0
    assert subset.density((-1, 2)) == 0


@pytest.mark.order(22)
@pytest.mark.dependency(depends=["test_begin"])
def test_copy():
    subset = SinglePoint(cartesian(-1, 2))

    other = copy(subset)
    assert other == subset
    assert id(other) != id(subset)
    assert id(subset.internal) == id(other.internal)

    other = deepcopy(subset)
    assert other == subset
    assert id(other) != id(subset)
    assert id(subset.internal) != id(other.internal)


@pytest.mark.order(22)
@pytest.mark.dependency(depends=["test_begin"])
def test_hash():
    subseta = SinglePoint(cartesian(-1, 2))
    subsetb = SinglePoint(cartesian(-1, 2))
    assert hash(subseta) == hash(subsetb)


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_build",
        "test_move",
        "test_scale",
        "test_rotate",
        "test_density",
        "test_copy",
        "test_hash",
    ]
)
def test_end():
    pass
