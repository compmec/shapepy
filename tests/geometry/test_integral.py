import math

import pytest

from shapepy.geometry.factory import FactoryJordan, FactorySegment
from shapepy.geometry.integral import lebesgue_density_jordan


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


class TestDensity:
    """
    Tests the respective position
    """

    @pytest.mark.order(15)
    @pytest.mark.dependency(depends=["test_begin", "test_area"])
    def test_begin(self):
        pass

    @pytest.mark.order(15)
    @pytest.mark.dependency(
        depends=[
            "TestDensity::test_begin",
        ]
    )
    def test_standard_square(self):
        vertices = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        jordan = FactoryJordan.polygon(vertices)
        assert jordan.length == 8
        assert jordan.area == 4

        interiors = {(0, 0)}
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

    @pytest.mark.order(15)
    @pytest.mark.dependency(
        depends=[
            "TestDensity::test_begin",
            "TestDensity::test_standard_square",
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

    @pytest.mark.order(15)
    @pytest.mark.dependency(
        depends=[
            "TestDensity::test_begin",
            "TestDensity::test_standard_square",
            "TestDensity::test_inverted_square",
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

    @pytest.mark.order(15)
    @pytest.mark.dependency(
        depends=[
            "TestDensity::test_begin",
            "TestDensity::test_inverted_square",
            "TestDensity::test_standard_triangle",
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

    @pytest.mark.order(15)
    @pytest.mark.dependency(
        depends=[
            "TestDensity::test_begin",
            "TestDensity::test_standard_square",
            "TestDensity::test_inverted_square",
            "TestDensity::test_standard_triangle",
            "TestDensity::test_inverted_triangle",
        ]
    )
    def test_all(self):
        pass


@pytest.mark.order(15)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_segment_length",
        "test_jordan_length",
        "test_area",
        "TestDensity::test_all",
    ]
)
def test_all():
    pass
