"""
This file contains tests functions to test the module polygon.py
"""

import math

import pytest

from shapepy import primitive


@pytest.mark.order(51)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "tests/analytic/test_piecewise.py::test_all",
    ],
    scope="session",
)
def test_square():
    primitive.square()
    with pytest.raises(ValueError):
        primitive.square(side=-1)
    with pytest.raises(ValueError):
        primitive.square(side=0)
    with pytest.raises(ValueError):
        primitive.square(side="asd")

    square = primitive.square()
    area = 1
    assert abs(square.area - area) < 1e-9

    square = primitive.square(side=2)
    area = 4
    assert abs(square.area - area) < 1e-9

    square = primitive.square(side=4)
    area = 16
    assert abs(square.area - area) < 1e-9


@pytest.mark.order(51)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "tests/analytic/test_piecewise.py::test_all",
    ],
    scope="session",
)
def test_triangle():
    primitive.square()
    with pytest.raises(ValueError):
        primitive.square(side=-1)
    with pytest.raises(ValueError):
        primitive.square(side=0)
    with pytest.raises(ValueError):
        primitive.square(side="asd")

    square = primitive.square()
    area = 1
    assert abs(square.area - area) < 1e-9

    square = primitive.square(side=2)
    area = 4
    assert abs(square.area - area) < 1e-9

    square = primitive.square(side=4)
    area = 16
    assert abs(square.area - area) < 1e-9


@pytest.mark.order(51)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "tests/analytic/test_piecewise.py::test_all",
    ],
    scope="session",
)
def test_regular_polygon():
    primitive.regular_polygon(3)
    primitive.regular_polygon(4)
    primitive.regular_polygon(5)

    with pytest.raises(ValueError):
        primitive.regular_polygon(-1)
    with pytest.raises(ValueError):
        primitive.regular_polygon(2)
    with pytest.raises(ValueError):
        primitive.regular_polygon("asd")

    for nsides in range(3, 7):
        polygon = primitive.regular_polygon(nsides)
        area = nsides * math.sin(2 * math.pi / nsides) / 2
        assert abs(polygon.area - area) < 1e-9

    radius = 4
    for nsides in range(3, 7):
        polygon = primitive.regular_polygon(nsides, radius=radius)
        area = radius**2 * nsides * math.sin(2 * math.pi / nsides) / 2
        assert abs(polygon.area - area) < 1e-9


@pytest.mark.order(51)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "tests/analytic/test_piecewise.py::test_all",
    ],
    scope="session",
)
def test_polygon():
    points = [(0, 0), (1, 0), (0, 1)]
    triangle = primitive.polygon(points)
    area = 0.5
    assert abs(triangle.area - area) < 1e-9

    points = [(0, 0), (0, 1), (1, 0)]
    triangle = primitive.polygon(points)
    area = -0.5
    assert abs(triangle.area - area) < 1e-9


@pytest.mark.order(51)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "test_polygon",
        "test_square",
        "test_triangle",
        "test_regular_polygon",
    ],
)
def test_all():
    pass
