import numpy as np
import pytest

from compmec.shape.jordancurve import JordanPolygon


@pytest.mark.order(5)
@pytest.mark.dependency(
    depends=[
        # "tests/test_polygon.py::test_end",
        # "tests/test_jordan.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestJordanCurve:
    @pytest.mark.order(5)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestJordanCurve::test_begin"])
    def test_move(self):
        good_square_pts = [(1, 2), (2, 2), (2, 3), (1, 3)]
        good_square = JordanPolygon(good_square_pts)

        test_square_pts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        test_square = JordanPolygon(test_square_pts)
        test_square.move((1, 2))

        assert test_square == good_square

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestJordanCurve::test_begin", "TestJordanCurve::test_move"]
    )
    def test_scale(self):
        good_rectangle_pts = [(0, 0), (2, 0), (2, 3), (0, 3)]
        good_rectangle = JordanPolygon(good_rectangle_pts)
        test_rectangle_pts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        test_rectangle = JordanPolygon(test_rectangle_pts)
        test_rectangle.scale(2, 3)
        assert test_rectangle == good_rectangle

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestJordanCurve::test_begin",
            "TestJordanCurve::test_move",
            "TestJordanCurve::test_scale",
        ]
    )
    def test_rotate(self):
        good_square_pts = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        good_square = JordanPolygon(good_square_pts)
        test_square_pts = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        test_square = JordanPolygon(test_square_pts)

        assert test_square == good_square
        test_square.rotate(np.pi / 6)  # 30 degrees
        print("test_square = ")
        print(test_square.vertices)
        assert test_square != good_square
        test_square.rotate(60, degrees=True)
        print("test_square = ")
        print(test_square)
        print(np.array(test_square.vertices))
        assert test_square == good_square

    @pytest.mark.order(5)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestJordanCurve::test_begin",
            "TestJordanCurve::test_move",
            "TestJordanCurve::test_scale",
            "TestJordanCurve::test_rotate",
        ]
    )
    def test_invert(self):
        orig_square_pts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        inve_square_pts = [(0, 0), (0, 1), (1, 1), (1, 0)]
        test_square_pts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        orig_square = JordanPolygon(orig_square_pts)
        inve_square = JordanPolygon(inve_square_pts)
        test_square = JordanPolygon(test_square_pts)

        assert inve_square != orig_square
        assert test_square == orig_square
        assert test_square != inve_square
        test_square.invert()
        assert test_square != orig_square
        assert test_square == inve_square
        test_square.invert()
        assert test_square == orig_square
        assert test_square != inve_square

    @pytest.mark.order(5)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestJordanCurve::test_move",
            "TestJordanCurve::test_rotate",
            "TestJordanCurve::test_scale",
            "TestJordanCurve::test_invert",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(5)
@pytest.mark.dependency(depends=["test_begin", "TestJordanCurve::test_end"])
def test_end():
    pass
