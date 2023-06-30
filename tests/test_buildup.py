import numpy as np
import pytest

from compmec.shape import primitive


@pytest.mark.order(1)
@pytest.mark.dependency()
def test_begin():
    pass


class TestInitial:
    @pytest.mark.order(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(1)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestInitial::test_begin"])
    def test_create_regular(self):
        primitive.regular_polygon(3)
        primitive.regular_polygon(4)
        primitive.regular_polygon(5)
        primitive.regular_polygon(101)

    @pytest.mark.order(1)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestInitial::test_begin"])
    def test_error_create_regular(self):
        with pytest.raises(TypeError):
            primitive.regular_polygon("asd")
        with pytest.raises(ValueError):
            primitive.regular_polygon(2)
        with pytest.raises(ValueError):
            primitive.regular_polygon(-1)

    @pytest.mark.order(1)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestInitial::test_create_regular"])
    def test_iterable(self):
        triangle = primitive.regular_polygon(3)
        for curve in triangle:
            for segment in curve:
                assert callable(segment)

    @pytest.mark.order(1)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestInitial::test_begin",
            "TestInitial::test_create_regular",
            "TestInitial::test_error_create_regular",
            "TestInitial::test_iterable",
        ]
    )
    def test_end(self):
        pass


class TestToPolygon:
    @pytest.mark.order(1)
    @pytest.mark.dependency(depends=["TestInitial::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(1)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestToPolygon::test_begin"])
    def test_regular3(self):
        triangle = primitive.regular_polygon(3)
        curve = triangle.curves[0]
        points_test = curve.polygon_points()
        points_good = [
            (1, 0),
            (np.cos(2 * np.pi / 3), np.sin(2 * np.pi / 3)),
            (np.cos(4 * np.pi / 3), np.sin(4 * np.pi / 3)),
            (1, 0),
        ]
        np.testing.assert_almost_equal(points_test, points_good)

    @pytest.mark.order(1)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestToPolygon::test_begin"])
    def test_regular4(self):
        diamond = primitive.regular_polygon(4)
        curve = diamond.curves[0]
        points_test = curve.polygon_points()
        points_good = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 0)]
        np.testing.assert_almost_equal(points_test, points_good)

    @pytest.mark.order(1)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestToPolygon::test_begin"])
    def test_triangle(self):
        triangle = primitive.triangle()
        curve = triangle.curves[0]
        points_test = curve.polygon_points()
        points_good = [
            (0, np.sqrt(3) / 3),
            (-1 / 2, -np.sqrt(3) / 6),
            (1 / 2, -np.sqrt(3) / 6),
            (0, np.sqrt(3) / 3),
        ]
        np.testing.assert_almost_equal(points_test, points_good)

    @pytest.mark.order(1)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestToPolygon::test_begin"])
    def test_square(self):
        square = primitive.square()
        curve = square.curves[0]
        points_test = curve.polygon_points()
        points_good = [
            (1 / 2, 1 / 2),
            (-1 / 2, 1 / 2),
            (-1 / 2, -1 / 2),
            (1 / 2, -1 / 2),
            (1 / 2, 1 / 2),
        ]
        np.testing.assert_almost_equal(points_test, points_good)

    @pytest.mark.order(1)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestToPolygon::test_begin"])
    def test_circle(self):
        circle = primitive.circle()
        curve = circle.curves[0]
        points_test = curve.polygon_points()
        for point in points_test:
            np.testing.assert_almost_equal(np.linalg.norm(point), 1)

    @pytest.mark.order(1)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestToPolygon::test_regular3",
            "TestToPolygon::test_regular4",
            "TestToPolygon::test_triangle",
            "TestToPolygon::test_square",
            "TestToPolygon::test_circle",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(1)
@pytest.mark.dependency(
    depends=["test_begin", "TestInitial::test_end", "TestToPolygon::test_end"]
)
def test_end():
    pass
