"""
This file contains tests functions to test the module polygon.py
"""

import math
from fractions import Fraction

import pytest

from compmec.shape import Primitive


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "tests/test_polygon.py::test_end",
        "tests/test_jordan_polygon.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestPrimitive:
    @pytest.mark.order(4)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestPrimitive::test_begin"])
    def test_creation(self):
        Primitive.circle()
        Primitive.square()

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestPrimitive::test_begin", "TestPrimitive::test_creation"]
    )
    def test_square(self):
        square = Primitive.square()
        area = 4
        assert abs(float(square) - area) < 1e-9

    @pytest.mark.order(4)
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
            assert abs(float(polygon) - area) < 1e-9

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestPrimitive::test_begin",
            "TestPrimitive::test_creation",
            "TestPrimitive::test_square",
            "TestPrimitive::test_regular",
        ]
    )
    def test_circle(self):
        circle = Primitive.circle()
        area = math.pi
        assert abs(float(circle) - area) < 1e-3

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestPrimitive::test_begin",
            "TestPrimitive::test_creation",
            "TestPrimitive::test_square",
            "TestPrimitive::test_regular",
            "TestPrimitive::test_circle",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "TestPrimitive::test_end",
    ]
)
def test_end():
    pass
