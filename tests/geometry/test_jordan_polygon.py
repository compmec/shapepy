"""
This file contains tests functions to test the module polygon.py
"""

import math

import numpy as np
import pytest

from shapepy.geometry.factory import FactoryJordan
from shapepy.geometry.integral import IntegrateJordan
from shapepy.geometry.jordancurve import clean_jordan


@pytest.mark.order(15)
@pytest.mark.dependency(
    depends=[
        "tests/geometry/test_point.py::test_all",
        "tests/geometry/test_box.py::test_all",
        "tests/geometry/test_segment.py::test_all",
        "tests/geometry/test_piecewise.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


class TestJordanPolygon:
    @pytest.mark.order(15)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(15)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestJordanPolygon::test_begin"])
    def test_creation(self):
        points = [(0, 0), (1, 0), (0, 1)]
        FactoryJordan.polygon(points)

        points = [(0, 0), (1, 0), (1, 1), (0, 1)]
        FactoryJordan.polygon(points)

    @pytest.mark.order(15)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
        ]
    )
    def test_error_creation(self):
        with pytest.raises(ValueError):
            FactoryJordan.polygon("asd")

    @pytest.mark.order(15)
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
        jordan = FactoryJordan.polygon(points)
        segments = jordan.segments
        for i, segi in enumerate(segments):
            segj = segments[(i + 1) % len(segments)]
            last_point = segi.ctrlpoints[-1]
            first_point = segj.ctrlpoints[0]
            assert last_point == first_point
            assert id(last_point) == id(first_point)

    @pytest.mark.order(15)
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
        postri0 = FactoryJordan.polygon([(0, 0), (1, 0), (0, 1)])
        postri1 = FactoryJordan.polygon([(1, 0), (0, 1), (0, 0)])
        postri2 = FactoryJordan.polygon([(0, 1), (0, 0), (1, 0)])
        positives = (postri0, postri1, postri2)
        for pos0 in positives:
            for pos1 in positives:
                assert pos0 == pos1

        negtri0 = FactoryJordan.polygon([(0, 0), (0, 1), (1, 0)])
        negtri1 = FactoryJordan.polygon([(1, 0), (0, 0), (0, 1)])
        negtri2 = FactoryJordan.polygon([(0, 1), (1, 0), (0, 0)])
        negatives = (negtri0, negtri1, negtri2)
        for neg0 in negatives:
            for neg1 in negatives:
                assert neg0 == neg1

    @pytest.mark.order(15)
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
        postri0 = FactoryJordan.polygon([(0, 0), (1, 0), (0, 1)])
        postri1 = FactoryJordan.polygon([(1, 0), (0, 1), (0, 0)])
        postri2 = FactoryJordan.polygon([(0, 1), (0, 0), (1, 0)])
        negtri0 = FactoryJordan.polygon([(0, 0), (0, 1), (1, 0)])
        negtri1 = FactoryJordan.polygon([(1, 0), (0, 0), (0, 1)])
        negtri2 = FactoryJordan.polygon([(0, 1), (1, 0), (0, 0)])
        positives = (postri0, postri1, postri2)
        negatives = (negtri0, negtri1, negtri2)
        for pos in positives:
            for neg in negatives:
                assert pos != neg

        square = FactoryJordan.polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        assert square != postri0
        assert square != postri1
        assert square != postri2

    @pytest.mark.order(15)
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
        postri0 = FactoryJordan.polygon([(0, 0), (1, 0), (0, 1)])
        postri1 = FactoryJordan.polygon([(1, 0), (0, 1), (0, 0)])
        postri2 = FactoryJordan.polygon([(0, 1), (0, 0), (1, 0)])
        negtri0 = FactoryJordan.polygon([(0, 0), (0, 1), (1, 0)])
        negtri1 = FactoryJordan.polygon([(1, 0), (0, 0), (0, 1)])
        negtri2 = FactoryJordan.polygon([(0, 1), (1, 0), (0, 0)])
        for pos in (postri0, postri1, postri2):
            for neg in (negtri0, negtri1, negtri2):
                assert pos == (~neg)
                # assert (~pos) == neg
                # assert ~(~pos) == pos
                # assert ~(~neg) == neg

    @pytest.mark.order(15)
    @pytest.mark.timeout(20)
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
    def test_intersection(self):
        vertices0 = [(1, 0), (-1, 2), (-3, 0), (-1, -2)]
        square0 = FactoryJordan.polygon(vertices0)
        vertices1 = [(-1, 0), (1, 2), (3, 0), (1, -2)]
        square1 = FactoryJordan.polygon(vertices1)

        inters = square0 & square0
        assert inters.all_subsets[id(square0)] == [0, 4]
        assert inters.all_knots[id(square0)] == {0, 1, 2, 3, 4}
        inters = square1 & square1
        assert inters.all_subsets[id(square1)] == [0, 4]
        assert inters.all_knots[id(square1)] == {0, 1, 2, 3, 4}

        inters = square0 & square1
        assert inters.all_subsets[id(square0)] == {0.5, 3.5}
        assert inters.all_knots[id(square0)] == {0, 0.5, 1, 2, 3, 3.5, 4}
        assert inters.all_subsets[id(square1)] == {0.5, 3.5}
        assert inters.all_knots[id(square1)] == {0, 0.5, 1, 2, 3, 3.5, 4}

        vertices1 = [(-1, 0), (1, -2), (3, 0), (1, 2)]
        square1 = FactoryJordan.polygon(vertices1)

        inters = square0 & square0
        assert inters.all_subsets[id(square0)] == [0, 4]
        assert inters.all_knots[id(square0)] == {0, 1, 2, 3, 4}
        inters = square1 & square1
        assert inters.all_subsets[id(square1)] == [0, 4]
        assert inters.all_knots[id(square1)] == {0, 1, 2, 3, 4}

        inters = square0 & square1
        assert inters.all_subsets[id(square0)] == {0.5, 3.5}
        assert inters.all_knots[id(square0)] == {0, 0.5, 1, 2, 3, 3.5, 4}
        assert inters.all_subsets[id(square1)] == {0.5, 3.5}
        assert inters.all_knots[id(square1)] == {0, 0.5, 1, 2, 3, 3.5, 4}

        vertices1 = [(1, -2), (3, 0), (1, 2), (-1, 0)]
        square1 = FactoryJordan.polygon(vertices1)

        inters = square0 & square0
        assert inters.all_subsets[id(square0)] == [0, 4]
        assert inters.all_knots[id(square0)] == {0, 1, 2, 3, 4}
        inters = square1 & square1
        assert inters.all_subsets[id(square1)] == [0, 4]
        assert inters.all_knots[id(square1)] == {0, 1, 2, 3, 4}

        inters = square0 & square1
        assert inters.all_subsets[id(square0)] == {0.5, 3.5}
        assert inters.all_knots[id(square0)] == {0, 0.5, 1, 2, 3, 3.5, 4}
        assert inters.all_subsets[id(square1)] == {2.5, 3.5}
        assert inters.all_knots[id(square1)] == {0, 1, 2, 2.5, 3, 3.5, 4}

    @pytest.mark.order(15)
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
            "TestJordanPolygon::test_intersection",
        ]
    )
    def test_end(self):
        pass


class TestTransformationPolygon:
    @pytest.mark.order(15)
    @pytest.mark.dependency(depends=["TestJordanPolygon::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(15)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestTransformationPolygon::test_begin"])
    def test_move(self):
        good_square_pts = [(2, 4), (3, 4), (3, 5), (2, 5)]
        good_square = FactoryJordan.polygon(good_square_pts)

        test_square_pts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        test_square = FactoryJordan.polygon(test_square_pts)
        test_square.move((1, 2))
        test_square.move((1, 2))

        assert test_square == good_square

    @pytest.mark.order(15)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestTransformationPolygon::test_begin",
            "TestTransformationPolygon::test_move",
        ]
    )
    def test_scale(self):
        good_rectangle_pts = [(0, 0), (2, 0), (2, 3), (0, 3)]
        good_rectangle = FactoryJordan.polygon(good_rectangle_pts)
        test_rectangle_pts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        test_rectangle = FactoryJordan.polygon(test_rectangle_pts)
        test_rectangle.scale(2, 3)
        assert test_rectangle == good_rectangle

    @pytest.mark.order(15)
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
        good_square = FactoryJordan.polygon(good_square_pts)
        test_square_pts = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        test_square = FactoryJordan.polygon(test_square_pts)

        assert test_square == good_square
        test_square.rotate(np.pi / 6)  # 30 degrees
        assert test_square != good_square
        test_square.rotate(60, degrees=True)
        assert test_square == good_square

    @pytest.mark.order(15)
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
        orig_square = FactoryJordan.polygon(orig_square_pts)
        inve_square = FactoryJordan.polygon(inve_square_pts)
        test_square = FactoryJordan.polygon(test_square_pts)

        assert inve_square != orig_square
        assert test_square == orig_square
        assert test_square != inve_square
        test_square.invert()
        assert test_square != orig_square
        assert test_square == inve_square
        test_square.invert()
        assert test_square == orig_square
        assert test_square != inve_square

    @pytest.mark.order(15)
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
        good_square = FactoryJordan.polygon(square_pts)
        test_square = FactoryJordan.polygon(square_pts)
        test_square.split((0, 2, 3), (0.5, 0.5, 0.5))
        assert test_square == good_square

    @pytest.mark.order(15)
    @pytest.mark.timeout(20)
    @pytest.mark.dependency(
        depends=[
            "TestTransformationPolygon::test_begin",
            "TestTransformationPolygon::test_move",
            "TestTransformationPolygon::test_scale",
            "TestTransformationPolygon::test_rotate",
            "TestTransformationPolygon::test_invert",
            "TestTransformationPolygon::test_split",
        ]
    )
    def test_keep_ids(self):
        square_vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        square = FactoryJordan.polygon(square_vertices)
        good_ids = tuple(id(vertex) for vertex in square.vertices)

        square.move((2, 3))
        test_ids = tuple(id(vertex) for vertex in square.vertices)
        assert len(test_ids) == len(good_ids)
        assert test_ids == good_ids

        square.rotate(90, degrees=True)
        test_ids = tuple(id(vertex) for vertex in square.vertices)
        assert len(test_ids) == len(good_ids)
        assert test_ids == good_ids

        square.scale(5, 4)
        test_ids = tuple(id(vertex) for vertex in square.vertices)
        assert len(test_ids) == len(good_ids)
        assert test_ids == good_ids

    @pytest.mark.order(15)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestTransformationPolygon::test_move",
            "TestTransformationPolygon::test_rotate",
            "TestTransformationPolygon::test_scale",
            "TestTransformationPolygon::test_invert",
            "TestTransformationPolygon::test_split",
            "TestTransformationPolygon::test_keep_ids",
        ]
    )
    def test_end(self):
        pass


class TestIntegrateJordan:
    @pytest.mark.order(15)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestJordanPolygon::test_end",
            "TestTransformationPolygon::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(15)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestIntegrateJordan::test_begin"])
    def test_winding_regular_polygon(self):
        for nsides in range(3, 10):
            angles = np.linspace(0, math.tau, nsides + 1)
            ctrlpoints = np.vstack([np.cos(angles), np.sin(angles)]).T
            jordancurve = FactoryJordan.polygon(ctrlpoints)
            wind = IntegrateJordan.winding_number(jordancurve)
            assert abs(wind - 1) < 1e-9

        for nsides in range(3, 10):
            angles = np.linspace(math.tau, 0, nsides + 1)
            ctrlpoints = np.vstack([np.cos(angles), np.sin(angles)]).T
            jordancurve = FactoryJordan.polygon(ctrlpoints)
            wind = IntegrateJordan.winding_number(jordancurve)
            assert abs(wind + 1) < 1e-9

    @pytest.mark.order(15)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestIntegrateJordan::test_begin"])
    def test_lenght_triangle(self):
        vertices = [(0, 0), (3, 0), (0, 4)]
        jordan_curve = FactoryJordan.polygon(vertices)
        test = float(jordan_curve)
        good = 12
        assert abs(test - good) < 1e-3

        vertices = [(0, 0), (0, 4), (3, 0)]
        jordan_curve = FactoryJordan.polygon(vertices)
        test = float(jordan_curve)
        good = -12
        assert abs(test - good) < 1e-3

    @pytest.mark.order(15)
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
        jordan_curve = FactoryJordan.polygon(square_vertices)
        lenght = float(jordan_curve)
        assert lenght > 0
        assert abs(lenght - 4 * side) < 1e-9

        side = 3
        square_vertices = [
            (-side / 2, -side / 2),
            (-side / 2, side / 2),
            (side / 2, side / 2),
            (side / 2, -side / 2),
        ]
        jordan_curve = FactoryJordan.polygon(square_vertices)
        lenght = float(jordan_curve)
        assert lenght < 0
        assert abs(lenght + 4 * side) < 1e-9

    @pytest.mark.order(15)
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
            jordan_curve = FactoryJordan.polygon(ctrlpoints)
            assert (float(jordan_curve) - lenght) < 1e-9

    @pytest.mark.order(15)
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
    @pytest.mark.order(15)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_end",
            "TestTransformationPolygon::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(15)
    @pytest.mark.dependency(depends=["TestOthers::test_begin"])
    def test_print(self):
        points = [(1, 1), (2, 2), (0, 3)]
        triangle = FactoryJordan.polygon(points)
        str(triangle)
        repr(triangle)

        points = [(1.0, 1.0), (2.0, 2.0), (0.0, 3.0)]
        triangle = FactoryJordan.polygon(points)
        str(triangle)
        repr(triangle)

        str(triangle.vertices)

    @pytest.mark.order(15)
    @pytest.mark.dependency(depends=["TestOthers::test_begin"])
    def test_clean(self):
        verticesa = [(-1, 0), (0, 0), (1, 0), (0, 1)]
        jordana = FactoryJordan.polygon(verticesa)
        jordana = clean_jordan(jordana)
        verticesb = [(-1, 0), (1, 0), (0, 1)]
        jordanb = FactoryJordan.polygon(verticesb)
        assert jordana == jordanb

        verticesa = [(-1.0, 0.0), (0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
        jordana = FactoryJordan.polygon(verticesa)
        jordana = clean_jordan(jordana)
        verticesb = [(-1.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
        jordanb = FactoryJordan.polygon(verticesb)
        assert jordana == jordanb

        verticesa = [(0, 0), (1, 0), (0, 1), (-1, 0)]
        jordana = FactoryJordan.polygon(verticesa)
        jordana = clean_jordan(jordana)
        verticesb = [(-1, 0), (1, 0), (0, 1)]
        jordanb = FactoryJordan.polygon(verticesb)
        assert jordana == jordanb

        verticesa = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)]
        jordana = FactoryJordan.polygon(verticesa)
        jordana = clean_jordan(jordana)
        verticesb = [(-1.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
        jordanb = FactoryJordan.polygon(verticesb)
        assert jordana == jordanb

    @pytest.mark.order(15)
    @pytest.mark.dependency(
        depends=["TestOthers::test_begin", "TestOthers::test_clean"]
    )
    def test_equal_divided(self):
        verticesa = [(-1, 0), (1, 0), (0, 1)]
        jordana = FactoryJordan.polygon(verticesa)
        verticesb = [(-1, 0), (0, 0), (1, 0), (0, 1)]
        jordanb = FactoryJordan.polygon(verticesb)
        assert jordana == jordanb

    @pytest.mark.order(15)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
            "TestOthers::test_print",
            "TestOthers::test_clean",
            "TestOthers::test_equal_divided",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(15)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "TestJordanPolygon::test_end",
        "TestTransformationPolygon::test_end",
        "TestIntegrateJordan::test_end",
        "TestOthers::test_end",
    ]
)
def test_all():
    pass
