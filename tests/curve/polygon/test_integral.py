"""
This file contains tests functions that computes the integrals
over a polygonal domain.

Basically we want to compute

I = int_D x^a * y^b * dx * dy

"""

from fractions import Fraction

import numpy as np
import pytest

from shapepy.curve.polygon.curve import polybidim


@pytest.mark.order(3)
@pytest.mark.dependency()
def test_begin():
    pass


class TestRectangle:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @staticmethod
    def rectangle(base: float, height: float):
        vertices = [
            (-base / 2, -height / 2),
            (base / 2, -height / 2),
            (base / 2, height / 2),
            (-base / 2, height / 2),
        ]
        return vertices

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestRectangle::test_begin"])
    def test_area(self):
        base = Fraction(5, 2)
        height = Fraction(7, 4)
        vertices = TestRectangle.rectangle(base, height)
        test_area = polybidim(vertices, 0, 0)
        assert test_area == base * height

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestRectangle::test_area"])
    def test_odd_exponents(self):
        base = Fraction(5, 2)
        height = Fraction(7, 4)
        vertices = TestRectangle.rectangle(base, height)
        for expx in range(12):
            for expy in range(12):
                if expx % 2 or expy % 2:
                    assert polybidim(vertices, expx, expy) == 0

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestRectangle::test_odd_exponents"])
    def test_even_exponents(self):
        base = Fraction(5, 2)
        height = Fraction(7, 4)
        vertices = TestRectangle.rectangle(base, height)
        for expx in range(12, 2):
            for expy in range(12, 2):
                test = polybidim(vertices, expx, expy)
                good = base ** (expx + 1) * height ** (expy + 1)
                good /= (1 + expx) * (1 + expy) * 2 ** (expx + expy)
                assert test == good

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestRectangle::test_begin",
            "TestRectangle::test_area",
            "TestRectangle::test_odd_exponents",
            "TestRectangle::test_even_exponents",
        ]
    )
    def test_end(self):
        pass


class TestRegularPolygon:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin", "TestRectangle::test_end"])
    def test_begin(self):
        pass

    @staticmethod
    def regular_polygon(nsides: int):
        vertices = [(1.0, 0.0)]
        for j in range(1, nsides):
            angle = 2 * j * np.pi / nsides
            xcoord = np.cos(angle)
            ycoord = np.sin(angle)
            vertices.append((xcoord, ycoord))
        return vertices

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestRegularPolygon::test_begin"])
    def test_triangle(self):
        vertices = TestRegularPolygon.regular_polygon(3)
        good_values = [
            [3 / 4, 0, 3 / 32, 0, 9 / 320],
            [0, 0, -3 / 160, 0, -9 / 1120],
            [3 / 32, 0, 3 / 320, 0, 117 / 35840],
            [3 / 160, 0, -3 / 1120, 0, -9 / 7168],
            [9 / 320, 0, 57 / 35840, 0, 99 / 179200],
        ]
        good_values = np.sqrt(3) * np.array(good_values)
        test_values = np.zeros(good_values.shape, dtype="float64")
        for expx in range(test_values.shape[0]):
            for expy in range(test_values.shape[1]):
                test = polybidim(vertices, expx, expy)
                test_values[expx, expy] = test
        np.testing.assert_allclose(test_values, good_values, atol=1e-9)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestRegularPolygon::test_triangle"])
    def test_square(self):
        vertices = TestRegularPolygon.regular_polygon(4)
        good_values = [
            [2, 0, 1 / 3, 0, 2 / 15],
            [0, 0, 0, 0, 0],
            [1 / 3, 0, 1 / 45, 0, 1 / 210],
            [0, 0, 0, 0, 0],
            [2 / 15, 0, 1 / 210, 0, 1 / 1575],
        ]
        good_values = np.array(good_values)
        test_values = np.zeros(good_values.shape, dtype="float64")
        for expx in range(test_values.shape[0]):
            for expy in range(test_values.shape[1]):
                test = polybidim(vertices, expx, expy)
                test_values[expx, expy] = test
        np.testing.assert_allclose(test_values, good_values, atol=1e-9)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestRegularPolygon::test_square"])
    def test_pentagon(self):
        vertices = TestRegularPolygon.regular_polygon(5)
        con0 = 5 * np.sqrt(10 + 2 * np.sqrt(5)) / 8
        con1 = 5 * np.sqrt(170 + 62 * np.sqrt(5)) / 192
        con2 = 5 * np.sqrt(25 + 10 * np.sqrt(5)) / 576
        good_values = [
            [con0, 0, con1],
            [0, 0, 0],
            [con1, 0, con2],
        ]
        good_values = np.array(good_values)
        test_values = np.zeros(good_values.shape, dtype="float64")
        for expx in range(test_values.shape[0]):
            for expy in range(test_values.shape[1]):
                test = polybidim(vertices, expx, expy)
                test_values[expx, expy] = test
        np.testing.assert_allclose(test_values, good_values, atol=1e-9)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestRegularPolygon::test_begin",
            "TestRegularPolygon::test_triangle",
            "TestRegularPolygon::test_square",
            "TestRegularPolygon::test_pentagon",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "TestRectangle::test_end",
        "TestRegularPolygon::test_end",
    ]
)
def test_end():
    pass
