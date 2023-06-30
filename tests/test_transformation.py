import numpy as np
import pytest

from compmec.shape import primitive


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "tests/test_buildup.py::test_end",
        "tests/test_comparison.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestTransformation:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestTransformation::test_begin"])
    def test_move(self):
        good_square = primitive.square(side=1, center=(1, 2))
        test_square = primitive.square(side=1, center=(0, 0))
        test_square.move(1, 2)
        assert test_square == good_square

        good_triangle = primitive.triangle(side=1, center=(1, 2))
        test_triangle = primitive.triangle(side=1, center=(0, 0))
        test_triangle.move(1, 2)
        assert test_triangle == good_triangle

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestTransformation::test_begin"])
    def test_rotate(self):
        good_square = primitive.square(side=1, center=(0, 0))
        test_square = primitive.square(side=1, center=(0, 0))
        assert test_square == good_square
        test_square.rotate_degrees(45)
        assert test_square != good_square
        test_square.rotate_radians(np.pi / 4)
        assert test_square == good_square

        good_triangle = primitive.triangle(side=1, center=(0, 0))
        test_triangle = primitive.triangle(side=1, center=(0, 0))
        assert test_triangle == good_triangle
        test_triangle.rotate_degrees(45)
        assert test_triangle != good_triangle
        test_triangle.rotate_radians(np.pi / 6)
        assert test_triangle != good_triangle
        test_triangle.rotate_degrees(45)
        assert test_triangle == good_triangle

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestTransformation::test_begin"])
    def test_scale(self):
        good_square = primitive.square(side=3, center=(0, 0))
        test_square = primitive.square(side=1, center=(0, 0))
        test_square.scale(3, 3)
        assert test_square == good_square

        good_triangle = primitive.triangle(side=3, center=(0, 0))
        test_triangle = primitive.triangle(side=1, center=(0, 0))
        test_triangle.scale(3, 3)
        assert test_triangle == good_triangle

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestTransformation::test_begin"])
    def test_invert(self):
        good_square = primitive.square(side=1, center=(0, 0))
        test_square = primitive.square(side=1, center=(0, 0))
        test_square.invert()
        assert test_square != good_square
        test_square.invert()
        assert test_square == good_square

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestTransformation::test_move",
            "TestTransformation::test_rotate",
            "TestTransformation::test_scale",
            "TestTransformation::test_invert",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin", "TestTransformation::test_end"])
def test_end():
    pass
