import math

import numpy as np
import pytest

from shapepy.geometry import integral
from shapepy.geometry.integral import IntegrateSegment
from shapepy.geometry.segment import Segment


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
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_lenght():
    points = [(0, 0), (1, 0)]
    curve = Segment(points)
    assert abs(curve.length - 1) < 1e-9

    points = [(1, 0), (0, 0)]
    curve = Segment(points)
    assert abs(curve.length - 1) < 1e-9

    points = [(0, 1), (1, 0)]
    curve = Segment(points)
    assert abs(curve.length - np.sqrt(2)) < 1e-9


@pytest.mark.order(14)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_winding_triangles():
    curve = Segment([(1, 0), (2, 0)])
    wind = IntegrateSegment.winding_number(curve)
    assert wind == 0

    curve = Segment([(1, 0), (1, 1)])
    wind = IntegrateSegment.winding_number(curve)
    assert abs(wind - 0.125) < 1e-9

    curve = Segment([(1, 0), (0, 1)])
    wind = IntegrateSegment.winding_number(curve)
    assert abs(wind - 0.25) < 1e-9

    curve = Segment([(1, 0), (-0.5, np.sqrt(3) / 2)])
    wind = IntegrateSegment.winding_number(curve)
    assert abs(3 * wind - 1) < 1e-9


@pytest.mark.order(14)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_winding_triangles",
    ]
)
def test_winding_unit_circle():
    ntests = 1000
    maxim = 0
    for _ in range(ntests):
        angle0 = np.random.uniform(0, 2 * np.pi)
        good_wind = np.random.uniform(-0.5, 0.5)
        angle1 = angle0 + 2 * np.pi * good_wind
        point0 = (np.cos(angle0), np.sin(angle0))
        point1 = (np.cos(angle1), np.sin(angle1))
        curve = Segment([point0, point1])
        test_wind = IntegrateSegment.winding_number(curve)
        diff = abs(good_wind - test_wind)
        maxim = max(maxim, diff)
        assert abs(good_wind - test_wind) < 1e-9


@pytest.mark.order(14)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_winding_triangles",
        "test_winding_unit_circle",
    ]
)
def test_winding_regular_polygon():
    for nsides in range(3, 10):
        angles = np.linspace(0, math.tau, nsides + 1)
        ctrlpoints = np.vstack([np.cos(angles), np.sin(angles)]).T
        pairs = zip(ctrlpoints[:-1], ctrlpoints[1:])
        curves = tuple(Segment(pair) for pair in pairs)
        for curve in curves:
            wind = IntegrateSegment.winding_number(curve)
            assert abs(nsides * wind - 1) < 1e-2

    for nsides in range(3, 10):
        angles = np.linspace(math.tau, 0, nsides + 1)
        ctrlpoints = np.vstack([np.cos(angles), np.sin(angles)]).T
        pairs = zip(ctrlpoints[:-1], ctrlpoints[1:])
        curves = tuple(Segment(pair) for pair in pairs)
        for curve in curves:
            wind = IntegrateSegment.winding_number(curve)
            assert abs(nsides * wind + 1) < 1e-2


@pytest.mark.order(14)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_lenght",
        "test_winding_triangles",
        "test_winding_unit_circle",
        "test_winding_regular_polygon",
    ]
)
def test_all():
    pass
