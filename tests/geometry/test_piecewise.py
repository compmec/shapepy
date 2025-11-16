"""
Tests the PiecewiseCurve class
"""

import pytest

from shapepy.geometry.factory import FactorySegment
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
    points = [
        ((0, 0), (1, 0)),
        ((1, 0), (1, 1)),
        ((1, 1), (0, 1)),
        ((0, 1), (0, 0)),
    ]
    segments = (
        FactorySegment.bezier(pts, [i, i + 1]) for i, pts in enumerate(points)
    )
    PiecewiseCurve(segments)


@pytest.mark.order(14)
@pytest.mark.dependency(depends=["test_build"])
def test_box():
    points = [
        ((0, 0), (1, 0)),
        ((1, 0), (1, 1)),
        ((1, 1), (0, 1)),
        ((0, 1), (0, 0)),
    ]
    segments = (
        FactorySegment.bezier(pts, [i, i + 1]) for i, pts in enumerate(points)
    )
    piecewise = PiecewiseCurve(segments)
    box = piecewise.box()
    assert box.lowpt == (0, 0)
    assert box.toppt == (1, 1)


@pytest.mark.order(14)
@pytest.mark.dependency(depends=["test_build"])
def test_evaluate():
    points = [
        ((0, 0), (1, 0)),
        ((1, 0), (1, 1)),
        ((1, 1), (0, 1)),
        ((0, 1), (0, 0)),
    ]
    segments = (
        FactorySegment.bezier(pts, [i, i + 1]) for i, pts in enumerate(points)
    )
    piecewise = PiecewiseCurve(segments)
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
    segments = (
        FactorySegment.bezier(pts, [i, i + 1]) for i, pts in enumerate(points)
    )
    piecewise = PiecewiseCurve(segments)
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
