import math

import pytest

from shapepy.geometry.factory import FactoryJordan, FactorySegment


@pytest.mark.order(15)
@pytest.mark.dependency(
    depends=[
        "tests/analytic/test_derivate.py::test_all",
        "tests/analytic/test_integrate.py::test_all",
        "tests/geometry/test_point.py::test_all",
        "tests/geometry/test_box.py::test_all",
        "tests/geometry/test_segment.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(15)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_segment_length():
    points = [(0, 0), (1, 0)]
    curve = FactorySegment.bezier(points)
    assert abs(curve.length - 1) < 1e-9

    points = [(1, 0), (0, 0)]
    curve = FactorySegment.bezier(points)
    assert abs(curve.length - 1) < 1e-9

    points = [(0, 1), (1, 0)]
    curve = FactorySegment.bezier(points)
    assert abs(curve.length - math.sqrt(2)) < 1e-9


@pytest.mark.order(15)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin", "test_segment_length"])
def test_jordan_length():
    vertices = [(0, 0), (3, 0), (0, 4)]
    jordan = FactoryJordan.polygon(vertices)
    assert jordan.length == 3 + 4 + 5

    vertices = [(0, 0), (0, 4), (3, 0)]
    jordan = FactoryJordan.polygon(vertices)
    assert jordan.length == 3 + 4 + 5


@pytest.mark.order(15)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin", "test_jordan_length"])
def test_area():
    vertices = [(0, 0), (3, 0), (0, 4)]
    jordan = FactoryJordan.polygon(vertices)
    assert jordan.area == 6

    vertices = [(0, 0), (0, 4), (3, 0)]
    jordan = FactoryJordan.polygon(vertices)
    assert jordan.area == -6


@pytest.mark.order(15)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_segment_length",
        "test_jordan_length",
        "test_area",
    ]
)
def test_all():
    pass
