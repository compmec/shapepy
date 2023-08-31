"""
This file contains tests functions to test the module polygon.py
"""

import numpy as np
import pytest

from compmec.shape.jordancurve import JordanCurve


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "tests/test_polygon.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestJordanPolygon:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestJordanPolygon::test_begin"])
    def test_creation(self):
        points = [(0, 0), (1, 0), (0, 1)]
        JordanCurve.from_vertices(points)

        points = [(0, 0), (1, 0), (1, 1), (0, 1)]
        JordanCurve.from_vertices(points)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestJordanPolygon::test_begin", "TestJordanPolygon::test_creation"]
    )
    def test_error_creation(self):
        with pytest.raises(TypeError):
            JordanCurve.from_vertices("asd")

    @pytest.mark.order(3)
    @pytest.mark.timeout(20)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
            "TestJordanPolygon::test_error_creation",
        ]
    )
    def test_equal_curves(self):
        postri0 = JordanCurve.from_vertices([(0, 0), (1, 0), (0, 1)])
        postri1 = JordanCurve.from_vertices([(1, 0), (0, 1), (0, 0)])
        postri2 = JordanCurve.from_vertices([(0, 1), (0, 0), (1, 0)])
        positives = (postri0, postri1, postri2)
        for pos0 in positives:
            for pos1 in positives:
                assert pos0 == pos1

        negtri0 = JordanCurve.from_vertices([(0, 0), (0, 1), (1, 0)])
        negtri1 = JordanCurve.from_vertices([(1, 0), (0, 0), (0, 1)])
        negtri2 = JordanCurve.from_vertices([(0, 1), (1, 0), (0, 0)])
        negatives = (negtri0, negtri1, negtri2)
        for neg0 in negatives:
            for neg1 in negatives:
                assert neg0 == neg1

    @pytest.mark.order(3)
    @pytest.mark.timeout(20)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
            "TestJordanPolygon::test_error_creation",
            "TestJordanPolygon::test_equal_curves",
        ]
    )
    def test_nonequal_curves(self):
        postri0 = JordanCurve.from_vertices([(0, 0), (1, 0), (0, 1)])
        postri1 = JordanCurve.from_vertices([(1, 0), (0, 1), (0, 0)])
        postri2 = JordanCurve.from_vertices([(0, 1), (0, 0), (1, 0)])
        negtri0 = JordanCurve.from_vertices([(0, 0), (0, 1), (1, 0)])
        negtri1 = JordanCurve.from_vertices([(1, 0), (0, 0), (0, 1)])
        negtri2 = JordanCurve.from_vertices([(0, 1), (1, 0), (0, 0)])
        positives = (postri0, postri1, postri2)
        negatives = (negtri0, negtri1, negtri2)
        for pos in positives:
            for neg in negatives:
                assert pos != neg

        square = JordanCurve.from_vertices([(0, 0), (1, 0), (1, 1), (0, 1)])
        assert square != postri0
        assert square != postri1
        assert square != postri2

    @pytest.mark.order(3)
    @pytest.mark.timeout(20)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
            "TestJordanPolygon::test_error_creation",
            "TestJordanPolygon::test_equal_curves",
        ]
    )
    def test_invert_curves(self):
        postri0 = JordanCurve.from_vertices([(0, 0), (1, 0), (0, 1)])
        postri1 = JordanCurve.from_vertices([(1, 0), (0, 1), (0, 0)])
        postri2 = JordanCurve.from_vertices([(0, 1), (0, 0), (1, 0)])
        negtri0 = JordanCurve.from_vertices([(0, 0), (0, 1), (1, 0)])
        negtri1 = JordanCurve.from_vertices([(1, 0), (0, 0), (0, 1)])
        negtri2 = JordanCurve.from_vertices([(0, 1), (1, 0), (0, 0)])
        for pos in (postri0, postri1, postri2):
            for neg in (negtri0, negtri1, negtri2):
                assert pos == (~neg)
                # assert (~pos) == neg
                # assert ~(~pos) == pos
                # assert ~(~neg) == neg

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
            "TestJordanPolygon::test_error_creation",
            "TestJordanPolygon::test_equal_curves",
            "TestJordanPolygon::test_invert_curves",
        ]
    )
    def test_contains_boundary_point(self):
        # Test if the points are in boundary
        triangle = JordanCurve.from_vertices([(0, 0), (1, 0), (0, 1)])
        assert (0, 0) in triangle
        assert (1, 0) in triangle
        assert (0, 1) in triangle
        assert (0.5, 0) in triangle
        assert (0.5, 0.5) in triangle
        assert (0, 0.5) in triangle

        square = JordanCurve.from_vertices([(0, 0), (1, 0), (1, 1), (0, 1)])
        assert (0, 0) in square
        assert (1, 0) in square
        assert (1, 1) in square
        assert (0, 1) in square
        assert (0.5, 0) in square
        assert (1, 0.5) in square
        assert (0.5, 1) in square
        assert (0, 0.5) in square

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
            "TestJordanPolygon::test_error_creation",
            "TestJordanPolygon::test_equal_curves",
            "TestJordanPolygon::test_invert_curves",
            "TestJordanPolygon::test_contains_boundary_point",
        ]
    )
    def test_notcontains_point(self):
        # Test if the points are in boundary
        triangle = JordanCurve.from_vertices([(0, 0), (1, 0), (0, 1)])
        assert (-1, -1) not in triangle
        assert (1, 1) not in triangle

        square = JordanCurve.from_vertices([(0, 0), (1, 0), (1, 1), (0, 1)])
        assert (-1, -1) not in square
        assert (2, 2) not in square

    @pytest.mark.order(3)
    @pytest.mark.timeout(20)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
            "TestJordanPolygon::test_error_creation",
            "TestJordanPolygon::test_equal_curves",
            "TestJordanPolygon::test_nonequal_curves",
            "TestJordanPolygon::test_invert_curves",
            "TestJordanPolygon::test_contains_boundary_point",
            "TestJordanPolygon::test_notcontains_point",
        ]
    )
    def test_intersection(self):
        vertices0 = [(1, 0), (-1, 2), (-3, 0), (-1, -2)]
        square0 = JordanCurve.from_vertices(vertices0)
        vertices1 = [(-1, 0), (1, 2), (3, 0), (1, -2)]
        square1 = JordanCurve.from_vertices(vertices1)

        equal_squares = tuple()
        assert square0 & square0 == equal_squares
        assert square1 & square1 == equal_squares
        good = [(0, 0, 0.5, 0.5), (3, 3, 0.5, 0.5)]
        test = np.array(square0 & square1, dtype="float64")
        assert np.all(test == good)
        test = np.array(square1 & square0, dtype="float64")
        assert np.all(test == good)

        vertices1 = [(-1, 0), (1, -2), (3, 0), (1, 2)]
        square1 = JordanCurve.from_vertices(vertices1)

        assert square0 & square0 == equal_squares
        assert square1 & square1 == equal_squares
        good = [(0, 3, 0.5, 0.5), (3, 0, 0.5, 0.5)]
        test = np.array(square0 & square1, dtype="float64")
        assert np.all(test == good)
        test = np.array(square1 & square0, dtype="float64")
        assert np.all(test == good)

        vertices1 = [(1, -2), (3, 0), (1, 2), (-1, 0)]
        square1 = JordanCurve.from_vertices(vertices1)

        assert square0 & square0 == equal_squares
        assert square1 & square1 == equal_squares
        good = [(0, 2, 0.5, 0.5), (3, 3, 0.5, 0.5)]
        test = np.array(square0 & square1, dtype="float64")
        assert np.all(test == good)
        good = [(2, 0, 0.5, 0.5), (3, 3, 0.5, 0.5)]
        test = np.array(square1 & square0, dtype="float64")
        assert np.all(test == good)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
            "TestJordanPolygon::test_error_creation",
            "TestJordanPolygon::test_equal_curves",
            "TestJordanPolygon::test_nonequal_curves",
            "TestJordanPolygon::test_invert_curves",
            "TestJordanPolygon::test_contains_boundary_point",
            "TestJordanPolygon::test_notcontains_point",
            "TestJordanPolygon::test_intersection",
        ]
    )
    def test_end(self):
        pass


class TestTransformationPolygon:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["TestJordanPolygon::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestTransformationPolygon::test_begin"])
    def test_move(self):
        good_square_pts = [(1, 2), (2, 2), (2, 3), (1, 3)]
        good_square = JordanCurve.from_vertices(good_square_pts)

        test_square_pts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        test_square = JordanCurve.from_vertices(test_square_pts)
        test_square.move((1, 2))

        assert test_square == good_square

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestTransformationPolygon::test_begin",
            "TestTransformationPolygon::test_move",
        ]
    )
    def test_scale(self):
        good_rectangle_pts = [(0, 0), (2, 0), (2, 3), (0, 3)]
        good_rectangle = JordanCurve.from_vertices(good_rectangle_pts)
        test_rectangle_pts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        test_rectangle = JordanCurve.from_vertices(test_rectangle_pts)
        test_rectangle.scale(2, 3)
        assert test_rectangle == good_rectangle

    @pytest.mark.order(3)
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
        good_square = JordanCurve.from_vertices(good_square_pts)
        test_square_pts = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        test_square = JordanCurve.from_vertices(test_square_pts)

        assert test_square == good_square
        test_square.rotate(np.pi / 6)  # 30 degrees
        assert test_square != good_square
        test_square.rotate(60, degrees=True)
        assert test_square == good_square

    @pytest.mark.order(3)
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
        orig_square = JordanCurve.from_vertices(orig_square_pts)
        inve_square = JordanCurve.from_vertices(inve_square_pts)
        test_square = JordanCurve.from_vertices(test_square_pts)

        assert inve_square != orig_square
        assert test_square == orig_square
        assert test_square != inve_square
        test_square.invert()
        assert test_square != orig_square
        assert test_square == inve_square
        test_square.invert()
        assert test_square == orig_square
        assert test_square != inve_square

    @pytest.mark.order(3)
    @pytest.mark.timeout(20)
    @pytest.mark.dependency(
        depends=[
            "TestTransformationPolygon::test_begin",
            "TestTransformationPolygon::test_move",
            "TestTransformationPolygon::test_scale",
            "TestTransformationPolygon::test_rotate",
            "TestTransformationPolygon::test_invert",
        ]
    )
    def test_split(self):
        square_pts = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        good_square = JordanCurve.from_vertices(square_pts)
        test_square = JordanCurve.from_vertices(square_pts)
        test_square.split((0, 2, 3), (0.5, 0.5, 0.5))
        assert test_square == good_square

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestTransformationPolygon::test_move",
            "TestTransformationPolygon::test_rotate",
            "TestTransformationPolygon::test_scale",
            "TestTransformationPolygon::test_invert",
            "TestTransformationPolygon::test_split",
        ]
    )
    def test_end(self):
        pass


class TestOthers:
    @pytest.mark.order(3)
    @pytest.mark.dependency(
        depends=["TestJordanPolygon::test_end", "TestTransformationPolygon::test_end"]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["TestOthers::test_begin"])
    def test_print(self):
        points = [(1, 1), (2, 2), (0, 3)]
        triangle = JordanCurve.from_vertices(points)
        str(triangle)
        repr(triangle)

        points = [(1.0, 1.0), (2.0, 2.0), (0.0, 3.0)]
        triangle = JordanCurve.from_vertices(points)
        str(triangle)
        repr(triangle)

        str(triangle.vertices)

    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["TestOthers::test_begin"])
    def test_self_intersection(self):
        points = [(0, 0), (1, 0), (0, 1)]
        jordana = JordanCurve.from_vertices(points)
        jordanb = JordanCurve.from_vertices(points)
        assert id(jordana) != id(jordanb)
        inters = jordana & jordanb
        assert not bool(inters)
        inters = jordana.intersection(jordanb, equal_beziers=False, end_points=False)
        assert not bool(inters)
        inters = jordana.intersection(jordanb, equal_beziers=False, end_points=True)
        assert bool(inters)
        inters = jordana.intersection(jordanb, equal_beziers=True, end_points=False)
        assert bool(inters)
        inters = jordana.intersection(jordanb, equal_beziers=True, end_points=True)
        assert bool(inters)

    @pytest.mark.order(3)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
            "TestOthers::test_print",
            "TestOthers::test_self_intersection",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "TestJordanPolygon::test_end",
        "TestTransformationPolygon::test_end",
        "TestOthers::test_end",
    ]
)
def test_end():
    pass
