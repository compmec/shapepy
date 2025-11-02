"""
Tests the PiecewiseCurve class
"""

import pytest

from shapepy.geometry.factory import FactoryPiecewise, FactorySegment
from shapepy.geometry.piecewise import PiecewiseCurve


@pytest.mark.order(14)
@pytest.mark.dependency(
    depends=[
        "tests/geometry/test_point.py::test_all",
        "tests/geometry/test_box.py::test_all",
        "tests/geometry/test_segment.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(14)
@pytest.mark.dependency(depends=["test_begin"])
def test_build():
    vertices = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
    FactoryPiecewise.polygonal(vertices)

    points = [
        ((0, 0), (1, 0)),
        ((1, 0), (1, 1)),
        ((1, 1), (0, 1)),
        ((0, 1), (0, 0)),
    ]
    FactoryPiecewise.bezier(points)


@pytest.mark.order(14)
@pytest.mark.dependency(depends=["test_build"])
def test_box():

    vertices = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
    piecewise = FactoryPiecewise.polygonal(vertices)
    box = piecewise.box()
    assert box.lowpt == (0, 0)
    assert box.toppt == (1, 1)

    points = [
        ((0, 0), (1, 0)),
        ((1, 0), (1, 1)),
        ((1, 1), (0, 1)),
        ((0, 1), (0, 0)),
    ]
    piecewise = FactoryPiecewise.bezier(points)
    box = piecewise.box()
    assert box.lowpt == (0, 0)
    assert box.toppt == (1, 1)


@pytest.mark.order(14)
@pytest.mark.dependency(depends=["test_build"])
def test_evaluate():
    vertices = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
    piecewise = FactoryPiecewise.polygonal(vertices)
    box = piecewise.box()
    assert box.lowpt == (0, 0)
    assert box.toppt == (1, 1)

    points = [
        ((0, 0), (1, 0)),
        ((1, 0), (1, 1)),
        ((1, 1), (0, 1)),
        ((0, 1), (0, 0)),
    ]
    piecewise = FactoryPiecewise.bezier(points)
    assert piecewise(0) == (0, 0)
    assert piecewise(1) == (1, 0)
    assert piecewise(2) == (1, 1)
    assert piecewise(3) == (0, 1)
    assert piecewise(4) == (0, 0)

    with pytest.raises(ValueError):
        piecewise(-1)
    with pytest.raises(ValueError):
        piecewise(5)


@pytest.mark.order(14)
@pytest.mark.dependency(depends=["test_build"])
def test_print():
    points = [
        ((0, 0), (1, 0)),
        ((1, 0), (1, 1)),
        ((1, 1), (0, 1)),
        ((0, 1), (0, 0)),
    ]
    piecewise = FactoryPiecewise.bezier(points)
    str(piecewise)
    repr(piecewise)


@pytest.mark.order(14)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_build",
        "test_box",
        "test_evaluate",
        "test_print",
    ]
)
def test_all():
    pass
