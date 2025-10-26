"""File to test the functions `move`, `scale` and `rotate`"""

from copy import copy, deepcopy

import pytest

from shapepy.bool2d.curve import SingleCurve
from shapepy.geometry.factory import FactorySegment
from shapepy.scalar.angle import degrees


@pytest.mark.order(23)
@pytest.mark.dependency(
    depends=[
        "tests/geometry/test_point.py::test_all",
        "tests/geometry/test_jordan_polygon.py::test_all",
        "tests/bool2d/test_empty_whole.py::test_end",
        "tests/bool2d/test_point.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(23)
@pytest.mark.dependency(depends=["test_begin"])
def test_build():
    segment = FactorySegment.bezier([(1, 2), (-4, 1)])
    SingleCurve(segment)


@pytest.mark.order(23)
@pytest.mark.dependency(depends=["test_begin", "test_build"])
def test_move():
    segment = FactorySegment.bezier([(1, 2), (-4, 1)])
    curve = SingleCurve(segment)

    test = curve.move((-3, 2))
    segment = FactorySegment.bezier([(-2, 4), (-7, 3)])
    good = SingleCurve(segment)

    assert test == good


@pytest.mark.order(23)
@pytest.mark.dependency(depends=["test_begin", "test_build"])
def test_scale():
    segment = FactorySegment.bezier([(1, 2), (-4, 1)])
    curve = SingleCurve(segment)

    test = curve.scale(4)
    segment = FactorySegment.bezier([(4, 8), (-16, 4)])
    good = SingleCurve(segment)

    assert test == good


@pytest.mark.order(23)
@pytest.mark.dependency(depends=["test_begin", "test_build"])
def test_rotate():
    segment = FactorySegment.bezier([(1, 2), (-4, 1)])
    curve = SingleCurve(segment)

    test = curve.rotate(degrees(90))
    segment = FactorySegment.bezier([(-2, 1), (-1, -4)])
    good = SingleCurve(segment)

    assert test == good


@pytest.mark.order(23)
@pytest.mark.dependency(depends=["test_begin"])
def test_density():
    segment = FactorySegment.bezier([(1, 2), (-4, 1)])
    subset = SingleCurve(segment)

    assert subset.density((0, 0)) == 0
    assert subset.density((-1, 2)) == 0
    assert subset.density((1, 2)) == 0
    assert subset.density((-4, 1)) == 0


@pytest.mark.order(23)
@pytest.mark.dependency(depends=["test_begin"])
def test_copy():
    segment = FactorySegment.bezier([(1, 2), (-4, 1)])
    subset = SingleCurve(segment)

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
    segment = FactorySegment.bezier([(1, 2), (-4, 1)])
    subseta = SingleCurve(segment)

    segment = FactorySegment.bezier([(1, 2), (-4, 1)])
    subsetb = SingleCurve(segment)
    assert hash(subseta) == hash(subsetb)


@pytest.mark.order(23)
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
