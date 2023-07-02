import pytest

from compmec.shape import JordanCurve, Shape, primitive


@pytest.mark.order(2)
@pytest.mark.dependency(
    depends=[
        "tests/test_buildup.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestContainsPoint:
    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestContainsPoint::test_begin"])
    def test_RP_cont_origin(self):
        """
        Function to test if all regular polygons have origin inside
        """
        for nsides in range(3, 51):
            polygon = primitive.regular_polygon(nsides)
            assert polygon.contains((0, 0))

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestContainsPoint::test_RP_cont_origin"])
    def test_square_near_boundary(self):
        """
        RP = regular polygon
        """
        square = primitive.square(side=2, center=(0, 0))
        assert square.contains((0, 0))
        assert not square.omits((0, 0))
        assert not square.intersects((0, 0))

        # Near interior
        assert square.contains(
            [
                (0.99, 0.99),
                (0, 0.99),
                (-0.99, 0.99),
                (-0.99, 0),
                (-0.99, -0.99),
                (0, -0.99),
                (0.99, -0.99),
                (0.99, 0),
            ]
        )
        assert not square.omits((0.99, 0.99))
        assert not square.omits((0, 0.99))
        assert not square.omits((-0.99, 0.99))
        assert not square.omits((-0.99, 0))
        assert not square.omits((-0.99, -0.99))
        assert not square.omits((0, -0.99))
        assert not square.omits((0.99, -0.99))
        assert not square.omits((0.99, 0))
        assert not square.intersects((0.99, 0.99))
        assert not square.intersects((0, 0.99))
        assert not square.intersects((-0.99, 0.99))
        assert not square.intersects((-0.99, 0))
        assert not square.intersects((-0.99, -0.99))
        assert not square.intersects((0, -0.99))
        assert not square.intersects((0.99, -0.99))
        assert not square.intersects((0.99, 0))

        # Boundary
        assert not square.contains((1, 0))
        assert not square.contains((1, 1))
        assert not square.contains((0, 1))
        assert not square.contains((-1, 1))
        assert not square.contains((-1, 0))
        assert not square.contains((-1, -1))
        assert not square.contains((0, -1))
        assert not square.contains((1, -1))

        assert square.intersects((1, 0))
        assert square.intersects((1, 1))
        assert square.intersects((0, 1))
        assert square.intersects((-1, 1))
        assert square.intersects((-1, 0))
        assert square.intersects((-1, -1))
        assert square.intersects((0, -1))
        assert square.intersects((1, -1))

        assert not square.omits((1, 0))
        assert not square.omits((1, 1))
        assert not square.omits((0, 1))
        assert not square.omits((-1, 1))
        assert not square.omits((-1, 0))
        assert not square.omits((-1, -1))
        assert not square.omits((0, -1))
        assert not square.omits((1, -1))

        # Near exterior
        assert not square.contains((1.01, 0))
        assert not square.contains((1.01, 1.01))
        assert not square.contains((0, 1.01))
        assert not square.contains((-1.01, 1.01))
        assert not square.contains((-1.01, 0))
        assert not square.contains((-1.01, -1.01))
        assert not square.contains((0, -1.01))
        assert not square.contains((1.01, -1.01))

        assert not square.intersects((1.01, 0))
        assert not square.intersects((1.01, 1.01))
        assert not square.intersects((0, 1.01))
        assert not square.intersects((-1.01, 1.01))
        assert not square.intersects((-1.01, 0))
        assert not square.intersects((-1.01, -1.01))
        assert not square.intersects((0, -1.01))
        assert not square.intersects((1.01, -1.01))
        assert square.omits(
            [
                (1.01, 0),
                (1.01, 1.01),
                (0, 1.01),
                (-1.01, 1.01),
                (-1.01, 0),
                (-1.01, -1.01),
                (0, -1.01),
                (1.01, -1.01),
            ]
        )

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestContainsPoint::test_begin"])
    def test_shape_is_inside(self):
        small_triangle = primitive.triangle(side=1)
        small_square = primitive.square(side=1)
        big_square = primitive.square(side=3)
        assert big_square.contains(small_triangle)
        assert big_square.contains(small_square)
        assert not small_triangle.contains(big_square)
        assert not small_square.contains(big_square)

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.skip(reason="Fails, need check line intersection")
    @pytest.mark.dependency(depends=["TestContainsPoint::test_begin"])
    def test_shape_is_neither(self):
        small_triangle = primitive.regular_polygon(3)
        small_square = primitive.regular_polygon(4)
        assert not small_square.contains(small_triangle)
        assert not small_triangle.contains(small_square)

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestContainsPoint::test_RP_cont_origin",
            "TestContainsPoint::test_square_near_boundary",
            "TestContainsPoint::test_shape_is_inside",
            "TestContainsPoint::test_shape_is_neither",
        ]
    )
    def test_end(self):
        pass


class TestComparison:
    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestContainsPoint::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestComparison::test_begin"])
    def test_equal(self):
        square1 = primitive.square()
        square2 = primitive.square()
        assert square1 == square2

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestComparison::test_begin"])
    def test_inequal(self):
        triangle = primitive.triangle()
        square = primitive.square()
        assert triangle != square
        assert triangle.intersects(square)
        assert square.intersects(triangle)

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestComparison::test_begin"])
    def test_verticesvalues(self):
        square = primitive.square(2)
        pentagon_points = [(2, 0), (1, 1), (-1, 1), (-1, -1), (1, -1), (2, 0)]
        pentagon = Shape([JordanCurve.init_from_points(pentagon_points)])
        assert square != pentagon
        assert pentagon.intersects(pentagon)
        assert square.intersects(pentagon)

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=["TestComparison::test_equal", "TestComparison::test_inequal"]
    )
    def test_deepcopy(self):
        triangle = primitive.regular_polygon(3)
        new_triangle = triangle.deepcopy()
        assert triangle == new_triangle
        assert id(triangle) != id(new_triangle)

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestComparison::test_equal",
            "TestComparison::test_inequal",
            "TestComparison::test_deepcopy",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_begin", "TestComparison::test_end"])
def test_end():
    pass
