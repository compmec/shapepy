import pytest

from compmec.shape import JordanCurve, Shape, primitive


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "tests/test_buildup.py::test_end",
        "tests/test_comparison.py::test_end",
        "tests/test_transformation.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestOperationSum:
    @pytest.mark.order(4)
    @pytest.mark.skip(reason="Needs implementation")
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperationSum::test_begin"])
    def test_supresssum(self):
        """
        If B is inside A, then A + B == A
        """
        small_triangle = primitive.triangle(side=1, center=(0, 0))
        big_triangle = primitive.triangle(side=2, center=(0, 0))
        assert big_triangle + small_triangle == big_triangle

        small_square = primitive.square(side=1, center=(0, 0))
        big_square = primitive.square(side=2, center=(0, 0))
        assert big_square + small_square == big_square

    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperationSum::test_begin"])
    def test_twotriangles2onesquare(self):
        points1 = [(-1, 1), (-1, -1), (1, 1), (-1, 1)]
        points2 = [(1, -1), (1, 1), (-1, -1), (1, -1)]
        curve = JordanCurve.init_from_points(points1)
        triangle1 = Shape([curve])
        curve = JordanCurve.init_from_points(points2)
        triangle2 = Shape([curve])
        square = primitive.square(side=2, center=(0, 0))
        assert square == triangle1 + triangle2
        assert square == triangle2 + triangle1

    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperationSum::test_begin"])
    def test_othersways(self):
        triangle = primitive.regular_polygon(3)
        square = primitive.regular_polygon(4)
        result = triangle + square
        assert result == triangle | square
        assert result == triangle or square

    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperationSum::test_begin"])
    def test_end(self):
        pass


class TestOperation:
    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.skip(reason="Needs implementation")
    @pytest.mark.dependency(depends=["TestOperationSum::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperation::test_begin"])
    def test_sub_regular(self):
        triangle = primitive.regular_polygon(3)
        square = primitive.regular_polygon(4)
        triangle - square
        square - triangle

    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperation::test_begin"])
    def test_mul_regular(self):
        triangle = primitive.regular_polygon(3)
        square = primitive.regular_polygon(4)
        triangle * square
        triangle & square
        square and triangle

    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperation::test_begin"])
    def test_xor_regular(self):
        triangle = primitive.regular_polygon(3)
        square = primitive.regular_polygon(4)
        triangle ^ square

    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestOperation::test_sum_regular",
            "TestOperation::test_sub_regular",
            "TestOperation::test_mul_regular",
            "TestOperation::test_xor_regular",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_begin", "TestOperation::test_end"])
def test_end():
    pass
