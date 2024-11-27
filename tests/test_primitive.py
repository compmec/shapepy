"""
This file contains tests functions to test the module polygon.py
"""

import math

import pytest

from shapepy import Primitive


@pytest.mark.order(5)
@pytest.mark.dependency(
    depends=[
        "tests/test_point.py::test_end",
        "tests/curve/polygon/test_jordan_polygon.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestPrimitive:
    @pytest.mark.order(5)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestPrimitive::test_begin"])
    def test_creation(self):
        Primitive.square()
        Primitive.regular_polygon(3)
        Primitive.regular_polygon(4)

        with pytest.raises(ValueError):
            Primitive.square(side=-1)
        with pytest.raises(ValueError):
            Primitive.square(side=0)
        with pytest.raises(TypeError):
            Primitive.square(side="asd")

        with pytest.raises(ValueError):
            Primitive.regular_polygon(-1)
        with pytest.raises(ValueError):
            Primitive.regular_polygon(2)
        with pytest.raises(ValueError):
            Primitive.regular_polygon("asd")

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestPrimitive::test_begin", "TestPrimitive::test_creation"]
    )
    def test_square(self):
        square = Primitive.square()
        area = 1
        assert abs(square.area - area) < 1e-9

        square = Primitive.square(side=2)
        area = 4
        assert abs(square.area - area) < 1e-9

        square = Primitive.square(side=4)
        area = 16
        assert abs(square.area - area) < 1e-9

        square = Primitive.square(side=3, center=(1, 2))
        area = 9
        assert abs(square.area - area) < 1e-9

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestPrimitive::test_begin",
            "TestPrimitive::test_creation",
            "TestPrimitive::test_square",
        ]
    )
    def test_regular(self):
        for nsides in range(3, 10):
            polygon = Primitive.regular_polygon(nsides)
            area = nsides * math.sin(2 * math.pi / nsides) / 2
            assert abs(polygon.area - area) < 1e-9

        radius = 4
        for nsides in range(3, 10):
            polygon = Primitive.regular_polygon(nsides, radius=radius)
            area = radius**2 * nsides * math.sin(2 * math.pi / nsides) / 2
            assert abs(polygon.area - area) < 1e-9

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestPrimitive::test_begin",
            "TestPrimitive::test_creation",
            "TestPrimitive::test_square",
            "TestPrimitive::test_regular",
        ]
    )
    def test_point(self):
        points = [(0, 0), (1, 0), (0, 1)]
        triangle = Primitive.polygon(points)
        area = 0.5
        assert abs(triangle.area - area) < 1e-9

        points = [(0, 0), (0, 1), (1, 0)]
        triangle = Primitive.polygon(points)
        area = -0.5
        assert abs(triangle.area - area) < 1e-9

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestPrimitive::test_begin",
            "TestPrimitive::test_creation",
            "TestPrimitive::test_square",
            "TestPrimitive::test_regular",
            "TestPrimitive::test_point",
        ]
    )
    def test_circle(self):
        circle = Primitive.circle()
        assert abs(circle.area - math.pi) < 1e-3

        radius = 5
        circle = Primitive.circle(radius=radius)
        area = math.pi * radius**2
        assert abs(circle.area - area) < 1e-3 * radius**2

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestPrimitive::test_begin",
            "TestPrimitive::test_creation",
            "TestPrimitive::test_square",
            "TestPrimitive::test_regular",
            "TestPrimitive::test_point",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(5)
@pytest.mark.dependency(
    depends=[
        "TestPrimitive::test_end",
    ]
)
def test_end():
    pass
