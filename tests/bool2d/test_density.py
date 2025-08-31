"""
This file contains the code to test the relative position
of an object with respect to another
"""

import pytest

from shapepy import lebesgue_density
from shapepy.bool2d.base import EmptyShape, WholeShape
from shapepy.bool2d.primitive import Primitive
from shapepy.bool2d.shape import ConnectedShape, DisjointShape
from shapepy.geometry.point import polar
from shapepy.scalar.angle import degrees


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "tests/geometry/test_integral.py::test_all",
        "tests/bool2d/test_empty_whole.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(22)
@pytest.mark.dependency(depends=["test_begin"])
def test_empty_whole():
    empty = EmptyShape()
    whole = WholeShape()
    for point in [(0, 0), (1, 0), (0, 1)]:
        assert lebesgue_density(empty, point) == 0
        assert lebesgue_density(whole, point) == 1
        assert empty.density(point) == 0
        assert whole.density(point) == 1

    for deg in range(0, 360, 30):
        angle = degrees(deg)
        point = polar(float("inf"), angle)
        assert lebesgue_density(empty, point) == 0
        assert lebesgue_density(whole, point) == 1
        assert empty.density(point) == 0
        assert whole.density(point) == 1


@pytest.mark.order(22)
@pytest.mark.dependency(depends=["test_begin", "test_empty_whole"])
def test_simple_shape():
    shape = Primitive.triangle(3)
    # Corners
    points_density = {
        (0, 0): 0.25,
        (3, 0): 0.125,
        (0, 3): 0.125,
    }
    for point, value in points_density.items():
        assert lebesgue_density(shape, point) == value
        assert shape.density(point) == value
    # Mid edges
    points_density = {
        (1, 0): 0.5,
        (2, 0): 0.5,
        (2, 1): 0.5,
        (1, 2): 0.5,
        (0, 2): 0.5,
        (0, 1): 0.5,
    }
    for point, value in points_density.items():
        assert lebesgue_density(shape, point) == value
        assert shape.density(point) == value
    # Interior exterior
    points_density = {
        (1, 1): 1,
        (2, 2): 0,
        (3, 3): 0,
        (-1, -1): 0,
    }
    for point, value in points_density.items():
        assert lebesgue_density(shape, point) == value
        assert shape.density(point) == value


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty_whole",
        "test_simple_shape",
    ]
)
def test_connected_shape():
    big = Primitive.square(side=6)
    small = Primitive.square(side=2)
    shape = ConnectedShape([big, ~small])
    # Corners
    points_density = {
        (1, 1): 0.75,
        (-1, 1): 0.75,
        (-1, -1): 0.75,
        (1, -1): 0.75,
        (3, 3): 0.25,
        (-3, 3): 0.25,
        (-3, -3): 0.25,
        (3, -3): 0.25,
    }
    for point, value in points_density.items():
        assert lebesgue_density(shape, point) == value
        assert shape.density(point) == value
    # Mid edges
    points_density = {
        (1, 0): 0.5,
        (0, 1): 0.5,
        (-1, 0): 0.5,
        (0, -1): 0.5,
        (3, 0): 0.5,
        (0, 3): 0.5,
        (-3, 0): 0.5,
        (0, -3): 0.5,
    }
    for point, value in points_density.items():
        assert lebesgue_density(shape, point) == value
        assert shape.density(point) == value
    # Interior exterior
    points_density = {
        (0, 0): 0,
        (2, 2): 1,
        (0, 2): 1,
        (-2, 2): 1,
        (-2, 0): 1,
        (-2, -2): 1,
        (0, -2): 1,
        (2, -2): 1,
        (2, 0): 1,
    }
    for point, value in points_density.items():
        assert lebesgue_density(shape, point) == value
        assert shape.density(point) == value


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_simple_shape",
        "test_connected_shape",
    ]
)
def test_disjoint_shape():
    squarel = Primitive.square(side=2, center=(-3, 0))
    squarer = Primitive.square(side=2, center=(3, 0))
    shape = DisjointShape([squarel, squarer])
    # Corner
    points_density = {
        (-4, -1): 0.25,
        (-2, -1): 0.25,
        (-2, 1): 0.25,
        (-4, 1): 0.25,
        (4, -1): 0.25,
        (2, -1): 0.25,
        (2, 1): 0.25,
        (4, 1): 0.25,
    }
    for point, value in points_density.items():
        assert lebesgue_density(shape, point) == value
        assert shape.density(point) == value
    # Mid edge
    points_density = {
        (-3, -1): 0.5,
        (-2, 0): 0.5,
        (-3, 1): 0.5,
        (-4, 0): 0.5,
        (3, -1): 0.5,
        (2, 0): 0.5,
        (3, 1): 0.5,
        (4, 0): 0.5,
    }
    for point, value in points_density.items():
        assert lebesgue_density(shape, point) == value
        assert shape.density(point) == value
    # Interior exterior
    points_density = {(0, 0): 0, (-3, 0): 1, (3, 0): 1}
    for point, value in points_density.items():
        assert lebesgue_density(shape, point) == value
        assert shape.density(point) == value


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty_whole",
        "test_simple_shape",
        "test_connected_shape",
        "test_disjoint_shape",
    ]
)
def test_end():
    pass
