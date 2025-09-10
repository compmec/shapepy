"""
This file contains the code to test the relative position
of an object with respect to another
"""

from fractions import Fraction as frac

import pytest

from shapepy import lebesgue_density
from shapepy.bool2d.base import EmptyShape, WholeShape
from shapepy.bool2d.density import lebesgue_density_jordan
from shapepy.bool2d.primitive import Primitive
from shapepy.bool2d.shape import ConnectedShape, DisjointShape, SimpleShape
from shapepy.geometry.factory import FactoryJordan
from shapepy.geometry.point import polar
from shapepy.loggers import enable_logger
from shapepy.scalar.angle import degrees, turns


@pytest.mark.order(23)
@pytest.mark.dependency(
    depends=[
        # "tests/geometry/test_integral.py::test_all",
        # "tests/geometry/test_jordan_polygon.py::test_all",
        # "tests/bool2d/test_empty_whole.py::test_end",
        # "tests/bool2d/test_primitive.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestJordan:
    """
    Tests the respective position
    """

    @pytest.mark.order(23)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(23)
    @pytest.mark.dependency(
        depends=[
            "TestJordan::test_begin",
        ]
    )
    def test_standard_square(self):
        vertices = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        jordan = FactoryJordan.polygon(vertices)
        assert jordan.length == 8
        assert jordan.area == 4

        interiors = {
            (0, 0),
            (0.5, 0.5),
            (-0.5, 0.5),
            (-0.5, -0.5),
            (0.5, -0.5),
        }
        exteriors = {
            (2, 1),
            (2, 2),
            (3, 3),
            (-1, -2),
        }
        mid_edges = {
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1),
        }
        corners = {
            (-1, -1): 0.25,
            (1, -1): 0.25,
            (1, 1): 0.25,
            (-1, 1): 0.25,
        }
        for point in interiors:
            assert lebesgue_density_jordan(jordan, point) == 1
        for point in exteriors:
            assert lebesgue_density_jordan(jordan, point) == 0
        for point in mid_edges:
            assert lebesgue_density_jordan(jordan, point) == 0.5
        for point, density in corners.items():
            assert lebesgue_density_jordan(jordan, point) == density

    @pytest.mark.order(23)
    @pytest.mark.dependency(
        depends=[
            "TestJordan::test_begin",
            "TestJordan::test_standard_square",
        ]
    )
    def test_inverted_square(self):
        vertices = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
        jordan = FactoryJordan.polygon(vertices)
        assert jordan.length == 8
        assert jordan.area == -4

        interiors = {
            (2, 1),
            (2, 2),
            (3, 3),
            (-1, -2),
        }
        exteriors = {(0, 0)}
        mid_edges = {
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1),
        }
        corners = {
            (-1, -1): 0.75,
            (1, -1): 0.75,
            (1, 1): 0.75,
            (-1, 1): 0.75,
        }
        for point in interiors:
            assert lebesgue_density_jordan(jordan, point) == 1
        for point in exteriors:
            assert lebesgue_density_jordan(jordan, point) == 0
        for point in mid_edges:
            assert lebesgue_density_jordan(jordan, point) == 0.5
        for point, density in corners.items():
            assert lebesgue_density_jordan(jordan, point) == density

    @pytest.mark.order(23)
    @pytest.mark.dependency(
        depends=[
            "TestJordan::test_begin",
            "TestJordan::test_standard_square",
            "TestJordan::test_inverted_square",
        ]
    )
    def test_standard_triangle(self):
        vertices = [(0, 0), (3, 0), (0, 3)]
        jordan = FactoryJordan.polygon(vertices)
        assert jordan.area == 9 / 2

        interiors = {(1, 1)}
        exteriors = {
            (2, 2),
            (3, 3),
            (-1, -1),
        }
        mid_edges = {
            (1, 0),
            (2, 0),
            (2, 1),
            (1, 2),
            (0, 2),
            (0, 1),
        }
        corners = {
            (0, 0): 0.25,
            (3, 0): 0.125,
            (0, 3): 0.125,
        }
        for point in interiors:
            assert lebesgue_density_jordan(jordan, point) == 1
        for point in exteriors:
            assert lebesgue_density_jordan(jordan, point) == 0
        for point in mid_edges:
            assert lebesgue_density_jordan(jordan, point) == 0.5
        for point, density in corners.items():
            assert lebesgue_density_jordan(jordan, point) == density

    @pytest.mark.order(23)
    @pytest.mark.dependency(
        depends=[
            "TestJordan::test_begin",
            "TestJordan::test_inverted_square",
            "TestJordan::test_standard_triangle",
        ]
    )
    def test_inverted_triangle(self):
        vertices = [(0, 0), (0, 3), (3, 0)]
        jordan = FactoryJordan.polygon(vertices)
        assert jordan.area == -9 / 2

        interiors = {
            (2, 2),
            (3, 3),
            (-1, -1),
        }
        exteriors = {(1, 1)}
        mid_edges = {
            (1, 0),
            (2, 0),
            (2, 1),
            (1, 2),
            (0, 2),
            (0, 1),
        }
        corners = {
            (0, 0): 0.75,
            (3, 0): 0.875,
            (0, 3): 0.875,
        }
        for point in interiors:
            assert lebesgue_density_jordan(jordan, point) == 1
        for point in exteriors:
            assert lebesgue_density_jordan(jordan, point) == 0
        for point in mid_edges:
            assert lebesgue_density_jordan(jordan, point) == 0.5
        for point, density in corners.items():
            assert lebesgue_density_jordan(jordan, point) == density

    @pytest.mark.order(23)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestJordan::test_begin",
            "TestJordan::test_standard_square",
            "TestJordan::test_inverted_square",
            "TestJordan::test_standard_triangle",
            "TestJordan::test_inverted_triangle",
        ]
    )
    def test_regular_polygon(self):
        for nsides in range(3, 10):
            angles = (turns(frac(i, nsides)) for i in range(nsides))
            ctrlpoints = tuple((a.cos(), a.sin()) for a in angles)

            # Counter clockwise
            vertices = tuple(ctrlpoints)
            jordancurve = FactoryJordan.polygon(vertices)
            density = lebesgue_density_jordan(jordancurve)
            assert density == 1

            # Clockwise
            vertices = tuple(ctrlpoints[::-1])
            jordancurve = FactoryJordan.polygon(vertices)
            density = lebesgue_density_jordan(jordancurve)
            assert density == 0

    @pytest.mark.order(23)
    @pytest.mark.dependency(
        depends=[
            "TestJordan::test_begin",
            "TestJordan::test_standard_square",
            "TestJordan::test_inverted_square",
            "TestJordan::test_standard_triangle",
            "TestJordan::test_inverted_triangle",
            "TestJordan::test_regular_polygon",
        ]
    )
    def test_all(self):
        pass


@pytest.mark.order(23)
@pytest.mark.dependency(depends=["test_begin", "TestJordan::test_all"])
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


@pytest.mark.order(23)
@pytest.mark.dependency(
    depends=["test_begin", "test_empty_whole", "TestJordan::test_all"]
)
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


@pytest.mark.order(23)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty_whole",
        "test_simple_shape",
        "TestJordan::test_all",
    ]
)
def test_connected_shape():
    big = Primitive.square(side=6)
    small = Primitive.square(side=2)
    with enable_logger("shapepy.bool2d.boole"):
        invsmall = ~small
        assert isinstance(invsmall, SimpleShape)
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


@pytest.mark.order(23)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_simple_shape",
        "test_connected_shape",
        "TestJordan::test_all",
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


@pytest.mark.order(23)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "TestJordan::test_all",
        "test_empty_whole",
        "test_simple_shape",
        "test_connected_shape",
        "test_disjoint_shape",
    ]
)
def test_end():
    pass
