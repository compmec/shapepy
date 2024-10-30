"""
This file contains tests functions to test the module polygon.py
"""

import math

import numpy as np
import pytest

from shapepy.curve.nurbs.jordan import IntegrateJordan
from shapepy.curve.polygon import JordanPolygon


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "tests/test_point.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestJordanPolygon:
    @pytest.mark.order(4)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestJordanPolygon::test_begin"])
    def test_creation(self):
        points = [(0, 0), (1, 0), (0, 1)]
        JordanPolygon(points)

        points = [(0, 0), (1, 0), (1, 1), (0, 1)]
        JordanPolygon(points)

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
        ]
    )
    def test_error_creation(self):
        with pytest.raises(ValueError):
            JordanPolygon("asd")

    @pytest.mark.order(4)
    @pytest.mark.timeout(20)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
            "TestJordanPolygon::test_error_creation",
        ]
    )
    def test_id_points(self):
        points = [(0, 0), (1, 0), (1, 1), (0, 1)]
        jordan = JordanPolygon(points)
        segments = jordan.segments
        for i, segi in enumerate(segments):
            segj = segments[(i + 1) % len(segments)]
            last_point = segi.vertices[-1]
            first_point = segj.vertices[0]
            assert last_point == first_point
            assert id(last_point) == id(first_point)

    @pytest.mark.order(4)
    @pytest.mark.timeout(20)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
            "TestJordanPolygon::test_error_creation",
            "TestJordanPolygon::test_id_points",
        ]
    )
    def test_equal_curves(self):
        postri0 = JordanPolygon([(0, 0), (1, 0), (0, 1)])
        postri1 = JordanPolygon([(1, 0), (0, 1), (0, 0)])
        postri2 = JordanPolygon([(0, 1), (0, 0), (1, 0)])
        positives = (postri0, postri1, postri2)
        for pos0 in positives:
            for pos1 in positives:
                assert pos0 == pos1

        negtri0 = JordanPolygon([(0, 0), (0, 1), (1, 0)])
        negtri1 = JordanPolygon([(1, 0), (0, 0), (0, 1)])
        negtri2 = JordanPolygon([(0, 1), (1, 0), (0, 0)])
        negatives = (negtri0, negtri1, negtri2)
        for neg0 in negatives:
            for neg1 in negatives:
                assert neg0 == neg1

    @pytest.mark.order(4)
    @pytest.mark.timeout(20)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
            "TestJordanPolygon::test_error_creation",
            "TestJordanPolygon::test_id_points",
            "TestJordanPolygon::test_equal_curves",
        ]
    )
    def test_nonequal_curves(self):
        postri0 = JordanPolygon([(0, 0), (1, 0), (0, 1)])
        postri1 = JordanPolygon([(1, 0), (0, 1), (0, 0)])
        postri2 = JordanPolygon([(0, 1), (0, 0), (1, 0)])
        negtri0 = JordanPolygon([(0, 0), (0, 1), (1, 0)])
        negtri1 = JordanPolygon([(1, 0), (0, 0), (0, 1)])
        negtri2 = JordanPolygon([(0, 1), (1, 0), (0, 0)])
        positives = (postri0, postri1, postri2)
        negatives = (negtri0, negtri1, negtri2)
        for pos in positives:
            for neg in negatives:
                assert pos != neg

        square = JordanPolygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        assert square != postri0
        assert square != postri1
        assert square != postri2

    @pytest.mark.order(4)
    @pytest.mark.timeout(20)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
            "TestJordanPolygon::test_error_creation",
            "TestJordanPolygon::test_id_points",
            "TestJordanPolygon::test_equal_curves",
        ]
    )
    def test_invert_curves(self):
        postri0 = JordanPolygon([(0, 0), (1, 0), (0, 1)])
        postri1 = JordanPolygon([(1, 0), (0, 1), (0, 0)])
        postri2 = JordanPolygon([(0, 1), (0, 0), (1, 0)])
        negtri0 = JordanPolygon([(0, 0), (0, 1), (1, 0)])
        negtri1 = JordanPolygon([(1, 0), (0, 0), (0, 1)])
        negtri2 = JordanPolygon([(0, 1), (1, 0), (0, 0)])
        for pos in (postri0, postri1, postri2):
            for neg in (negtri0, negtri1, negtri2):
                assert pos == (~neg)
                # assert (~pos) == neg
                # assert ~(~pos) == pos
                # assert ~(~neg) == neg

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
            "TestJordanPolygon::test_error_creation",
            "TestJordanPolygon::test_id_points",
            "TestJordanPolygon::test_equal_curves",
            "TestJordanPolygon::test_nonequal_curves",
            "TestJordanPolygon::test_invert_curves",
        ]
    )
    def test_end(self):
        pass


class TestTransformationPolygon:
    @pytest.mark.order(4)
    @pytest.mark.dependency(depends=["TestJordanPolygon::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestTransformationPolygon::test_begin"])
    def test_move(self):
        good_square_pts = [(2, 4), (3, 4), (3, 5), (2, 5)]
        good_square = JordanPolygon(good_square_pts)

        test_square_pts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        test_square = JordanPolygon(test_square_pts)
        test_square.move((2, 4))

        assert test_square == good_square

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestTransformationPolygon::test_begin",
            "TestTransformationPolygon::test_move",
        ]
    )
    def test_scale(self):
        good_rectangle_pts = [(0, 0), (2, 0), (2, 3), (0, 3)]
        good_rectangle = JordanPolygon(good_rectangle_pts)
        test_rectangle_pts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        test_rectangle = JordanPolygon(test_rectangle_pts)
        test_rectangle.scale(2, 3)
        assert test_rectangle == good_rectangle

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestTransformationPolygon::test_begin",
            "TestTransformationPolygon::test_move",
            "TestTransformationPolygon::test_scale",
        ]
    )
    def test_rotate(self):
        good_square_pts = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        good_square = JordanPolygon(good_square_pts)
        test_square_pts = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        test_square = JordanPolygon(test_square_pts)

        assert test_square == good_square
        test_square.rotate(np.pi / 6)  # 30 degrees
        assert test_square != good_square
        test_square.rotate(60, degrees=True)
        assert test_square == good_square

    @pytest.mark.order(4)
    @pytest.mark.timeout(20)
    @pytest.mark.dependency(
        depends=[
            "TestTransformationPolygon::test_begin",
            "TestTransformationPolygon::test_move",
            "TestTransformationPolygon::test_scale",
            "TestTransformationPolygon::test_rotate",
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
        test_square = ~test_square
        assert test_square != orig_square
        assert test_square == inve_square
        test_square = ~test_square
        assert test_square == orig_square
        assert test_square != inve_square

    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestTransformationPolygon::test_move",
            "TestTransformationPolygon::test_rotate",
            "TestTransformationPolygon::test_scale",
            "TestTransformationPolygon::test_invert",
        ]
    )
    def test_end(self):
        pass


class TestIntegrateJordan:
    @pytest.mark.order(4)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestJordanPolygon::test_end",
            "TestTransformationPolygon::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestIntegrateJordan::test_begin"])
    def test_winding_regular_polygon(self):
        for nsides in range(3, 10):
            angles = np.linspace(0, math.tau, nsides + 1)
            ctrlpoints = np.vstack([np.cos(angles), np.sin(angles)]).T
            jordancurve = JordanPolygon(ctrlpoints)
            wind = jordancurve.winding((0, 0))
            assert abs(wind - 1) < 1e-9

        for nsides in range(3, 10):
            angles = np.linspace(math.tau, 0, nsides + 1)
            ctrlpoints = np.vstack([np.cos(angles), np.sin(angles)]).T
            jordancurve = JordanPolygon(ctrlpoints)
            wind = jordancurve.winding((0, 0))
            assert abs(wind) < 1e-9

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestIntegrateJordan::test_begin"])
    def test_lenght_triangle(self):
        vertices = [(0, 0), (3, 0), (0, 4)]
        jordan_curve = JordanPolygon(vertices)
        good = 12
        assert abs(jordan_curve.lenght - good) < 1e-3

        vertices = [(0, 0), (0, 4), (3, 0)]
        jordan_curve = JordanPolygon(vertices)
        good = 12
        assert abs(jordan_curve.lenght - good) < 1e-3

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestIntegrateJordan::test_begin",
            "TestIntegrateJordan::test_lenght_triangle",
        ]
    )
    def test_lenght_square(self):
        side = 3
        square_vertices = [
            (-side / 2, -side / 2),
            (side / 2, -side / 2),
            (side / 2, side / 2),
            (-side / 2, side / 2),
        ]
        jordan_curve = JordanPolygon(square_vertices)
        assert jordan_curve.lenght > 0
        assert abs(jordan_curve.lenght - 4 * side) < 1e-9

        side = 3
        square_vertices = [
            (-side / 2, -side / 2),
            (-side / 2, side / 2),
            (side / 2, side / 2),
            (side / 2, -side / 2),
        ]
        jordan_curve = JordanPolygon(square_vertices)
        assert jordan_curve.lenght > 0
        assert abs(jordan_curve.lenght - 4 * side) < 1e-9

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestIntegrateJordan::test_begin",
            "TestIntegrateJordan::test_lenght_triangle",
            "TestIntegrateJordan::test_lenght_square",
        ]
    )
    def test_lenght_regular_polygon(self):
        for nsides in range(3, 10):
            lenght = 2 * nsides * np.sin(math.pi / nsides)
            angles = np.linspace(0, math.tau, nsides + 1)
            ctrlpoints = np.vstack([np.cos(angles), np.sin(angles)]).T
            jordan_curve = JordanPolygon(ctrlpoints)
            assert (jordan_curve.lenght - lenght) < 1e-9

    @pytest.mark.order(4)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestIntegrateJordan::test_begin",
            "TestIntegrateJordan::test_winding_regular_polygon",
            "TestIntegrateJordan::test_lenght_triangle",
            "TestIntegrateJordan::test_lenght_square",
            "TestIntegrateJordan::test_lenght_regular_polygon",
        ]
    )
    def test_end(self):
        pass


class TestOthers:
    @pytest.mark.order(4)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_end",
            "TestTransformationPolygon::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.dependency(depends=["TestOthers::test_begin"])
    def test_print(self):
        points = [(1, 1), (2, 2), (0, 3)]
        triangle = JordanPolygon(points)
        str(triangle)
        repr(triangle)

        points = [(1.0, 1.0), (2.0, 2.0), (0.0, 3.0)]
        triangle = JordanPolygon(points)
        str(triangle)
        repr(triangle)

        str(triangle.vertices)

    @pytest.mark.order(4)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
            "TestOthers::test_print",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "TestJordanPolygon::test_end",
        "TestTransformationPolygon::test_end",
        "TestIntegrateJordan::test_end",
    ]
)
def test_end():
    pass
