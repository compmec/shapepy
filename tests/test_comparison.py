import pytest

from compmec.shape.primitive import regular_polygon


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "tests/test_buildup.py::test_end",
        "tests/test_transformation.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestComparison:
    @pytest.mark.order(3)
    @pytest.mark.skip(reason="Needs implementation")
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestComparison::test_begin"])
    def test_equal(self):
        square1 = regular_polygon(4)
        square2 = regular_polygon(4)
        assert square1 == square2

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestComparison::test_begin"])
    def test_inequal(self):
        triangle = regular_polygon(3)
        square = regular_polygon(4)
        assert triangle != square

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=["TestComparison::test_begin", "TestTransformation::test_end"]
    )
    def test_shape_is_inside(self):
        small_triangle = regular_polygon(3)
        small_square = regular_polygon(4)
        big_square = regular_polygon(4).scale(3, 3)
        assert small_triangle < big_square
        assert small_square < big_square

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=["TestComparison::test_begin", "TestTransformation::test_end"]
    )
    def test_shape_is_outside(self):
        small_triangle = regular_polygon(3)
        small_square = regular_polygon(4)
        big_square = regular_polygon(4).scale(3, 3)
        assert big_square > small_triangle
        assert big_square > small_square

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=["TestComparison::test_begin", "TestTransformation::test_end"]
    )
    def test_shape_is_neither(self):
        small_triangle = regular_polygon(3)
        small_square = regular_polygon(4)
        assert not (small_triangle > small_square)
        assert not (small_triangle == small_square)
        assert not (small_triangle < small_square)

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestComparison::test_equal",
            "TestComparison::test_inequal",
            "TestComparison::test_shape_is_inside",
            "TestComparison::test_shape_is_outside",
            "TestComparison::test_shape_is_neither",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin", "TestComparison::test_end"])
def test_end():
    pass
