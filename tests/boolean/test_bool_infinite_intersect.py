"""
This module tests when two shapes have common edges/segments
"""

import pytest

from shapepy.primitive import Primitive


@pytest.mark.order(9)
@pytest.mark.dependency(
    depends=[
        "tests/test_point.py::test_end",
        "tests/test_jordan_polygon.py::test_end",
        "tests/test_jordan_curve.py::test_end",
        "tests/test_primitive.py::test_end",
        "tests/test_contains.py::test_end",
        "tests/test_empty_whole.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestTriangle:
    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(9)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestTriangle::test_begin"])
    def test_or_triangles(self):
        vertices0 = [(0, 0), (1, 0), (0, 1)]
        vertices1 = [(0, 0), (0, 1), (-1, 0)]
        triangle0 = Primitive.polygon(vertices0)
        triangle1 = Primitive.polygon(vertices1)
        test = triangle0 | triangle1

        vertices = [(1, 0), (0, 1), (-1, 0)]
        good = Primitive.polygon(vertices)
        assert test == good

    @pytest.mark.order(9)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestTriangle::test_begin",
            "TestTriangle::test_or_triangles",
        ]
    )
    def test_and_triangles(self):
        vertices0 = [(0, 0), (2, 0), (0, 2)]
        vertices1 = [(0, 0), (1, 0), (0, 1)]
        triangle0 = Primitive.polygon(vertices0)
        triangle1 = Primitive.polygon(vertices1)
        test = triangle0 & triangle1

        vertices = [(0, 0), (1, 0), (0, 1)]
        good = Primitive.polygon(vertices)
        assert test == good

    @pytest.mark.order(9)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(
        depends=[
            "TestTriangle::test_begin",
            "TestTriangle::test_or_triangles",
            "TestTriangle::test_and_triangles",
        ]
    )
    def test_sub_triangles(self):
        vertices0 = [(0, 0), (2, 0), (0, 2)]
        vertices1 = [(0, 0), (1, 0), (0, 1)]
        triangle0 = Primitive.polygon(vertices0)
        triangle1 = Primitive.polygon(vertices1)
        test = triangle0 - triangle1

        vertices = [(1, 0), (2, 0), (0, 2), (0, 1)]
        good = Primitive.polygon(vertices)

        assert test == good

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestTriangle::test_begin",
            "TestTriangle::test_or_triangles",
            "TestTriangle::test_and_triangles",
            "TestTriangle::test_sub_triangles",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(9)
@pytest.mark.dependency(
    depends=[
        "TestTriangle::test_end",
    ]
)
def test_end():
    pass
