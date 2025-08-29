"""
This file contains tests functions to test the module polygon.py
"""

import pytest

from shapepy.geometry.box import Box
from shapepy.geometry.factory import FactorySegment
from shapepy.geometry.unparam import USegment
from shapepy.scalar.angle import Angle


@pytest.mark.order(14)
@pytest.mark.dependency(
    depends=[
        "tests/geometry/test_segment.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(14)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_build():
    points = [(0, 0), (1, 0), (0, 1)]
    segment = FactorySegment.bezier(points)
    USegment(segment)


@pytest.mark.order(14)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_length():
    segment = FactorySegment.bezier([(0, 0), (3, 4)])
    usegment = USegment(segment)
    assert usegment.length == 5


@pytest.mark.order(14)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_box():
    segment = FactorySegment.bezier([(0, 0), (3, 4)])
    usegment = USegment(segment)
    assert usegment.box() == Box((0, 0), (3, 4))


@pytest.mark.order(14)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_move():
    segment = FactorySegment.bezier([(0, 0), (3, 4)])
    usegment = USegment(segment)
    usegment.move((1, 2))

    good = FactorySegment.bezier([(1, 2), (4, 6)])
    assert usegment.parametrize() == good


@pytest.mark.order(14)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_scale():
    segment = FactorySegment.bezier([(0, 0), (3, 4)])
    usegment = USegment(segment)
    usegment.scale(4)

    good = FactorySegment.bezier([(0, 0), (12, 16)])
    assert usegment.parametrize() == good


@pytest.mark.order(14)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_rotate():
    segment = FactorySegment.bezier([(0, 0), (3, 4)])
    usegment = USegment(segment)
    angle = Angle.degrees(90)
    usegment.rotate(angle)

    good = FactorySegment.bezier([(0, 0), (-4, 3)])
    assert usegment.parametrize() == good


@pytest.mark.order(14)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_build",
        "test_length",
        "test_box",
        "test_move",
        "test_scale",
        "test_rotate",
    ]
)
def test_all():
    pass
