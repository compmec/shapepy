import pytest

from compmec.shape import primitive


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
    def test_RP_notcontains(self):
        """
        RP = regular polygon
        """
        for nsides in range(3, 15):
            print("nsides = ", nsides)
            polygon = primitive.regular_polygon(nsides)
            assert polygon.contains((0.99, 0))
            assert not polygon.contains((1, 0))
            assert not polygon.contains((0, 1))
            assert not polygon.contains((-1, 0))
            assert not polygon.contains((0, -1))

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestContainsPoint::test_RP_cont_origin",
            "TestContainsPoint::test_RP_notcontains",
        ]
    )
    def test_square_boundary(self):
        """
        RP = regular polygon
        """
        square = primitive.square(side=2)
        assert square.contains((0, 0))
        assert not square.omits((0, 0))
        assert square.contains((0.99, 0.99))
        assert square.contains((-0.99, 0.99))
        assert square.contains((-0.99, -0.99))
        assert square.contains((0.99, -0.99))

        # Vertex
        assert not square.contains((1, 1))
        assert not square.contains((-1, 1))
        assert not square.contains((-1, -1))
        assert not square.contains((1, -1))

        # Lines
        assert not square.contains((1, 0))
        assert not square.contains((0, 1))
        assert not square.contains((-1, 0))
        assert not square.contains((0, -1))

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
            "TestContainsPoint::test_RP_notcontains",
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
        square1 = primitive.regular_polygon(4)
        square2 = primitive.regular_polygon(4)
        assert square1 == square2

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestComparison::test_begin"])
    def test_inequal(self):
        triangle = primitive.regular_polygon(3)
        square = primitive.regular_polygon(4)
        assert triangle != square

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
