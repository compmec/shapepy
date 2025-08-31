"""
This file contains tests functions to test the module polygon.py
"""

import math

import numpy as np
import pytest

from shapepy.geometry.factory import FactoryJordan
from shapepy.geometry.integral import lebesgue_density_jordan
from shapepy.geometry.jordancurve import clean_jordan
from shapepy.scalar.angle import degrees, radians


@pytest.mark.order(15)
@pytest.mark.dependency(
    depends=[
        "tests/geometry/test_point.py::test_all",
        "tests/geometry/test_box.py::test_all",
        "tests/geometry/test_segment.py::test_all",
        "tests/geometry/test_piecewise.py::test_all",
        "tests/geometry/test_usegment.py::test_all",
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
        param0 = square0.parametrize()
        param1 = square1.parametrize()

        inters = param0 & param0
        assert inters.all_subsets[id(param0)] == [0, 4]
        assert inters.all_knots[id(param0)] == {0, 1, 2, 3, 4}
        inters = param1 & param1
        assert inters.all_subsets[id(param1)] == [0, 4]
        assert inters.all_knots[id(param1)] == {0, 1, 2, 3, 4}

        inters = param0 & param1
        print(param0)
        print(param1)
        print(inters)
        assert inters.all_subsets[id(param0)] == {0.5, 3.5}
        assert inters.all_knots[id(param0)] == {0, 0.5, 1, 2, 3, 3.5, 4}
        assert inters.all_subsets[id(param1)] == {0.5, 3.5}
        assert inters.all_knots[id(param1)] == {0, 0.5, 1, 2, 3, 3.5, 4}

        vertices1 = [(-1, 0), (1, -2), (3, 0), (1, 2)]
        square1 = FactoryJordan.polygon(vertices1)
        param1 = square1.parametrize()

        inters = param0 & param0
        assert inters.all_subsets[id(param0)] == [0, 4]
        assert inters.all_knots[id(param0)] == {0, 1, 2, 3, 4}
        inters = param1 & param1
        assert inters.all_subsets[id(param1)] == [0, 4]
        assert inters.all_knots[id(param1)] == {0, 1, 2, 3, 4}

        inters = param0 & param1
        assert inters.all_subsets[id(param0)] == {0.5, 3.5}
        assert inters.all_knots[id(param0)] == {0, 0.5, 1, 2, 3, 3.5, 4}
        assert inters.all_subsets[id(param1)] == {0.5, 3.5}
        assert inters.all_knots[id(param1)] == {0, 0.5, 1, 2, 3, 3.5, 4}

        vertices1 = [(1, -2), (3, 0), (1, 2), (-1, 0)]
        square1 = FactoryJordan.polygon(vertices1)
        param1 = square1.parametrize()

        inters = param0 & param0
        assert inters.all_subsets[id(param0)] == [0, 4]
        assert inters.all_knots[id(param0)] == {0, 1, 2, 3, 4}
        inters = param1 & param1
        assert inters.all_subsets[id(param1)] == [0, 4]
        assert inters.all_knots[id(param1)] == {0, 1, 2, 3, 4}

        inters = param0 & param1
        assert inters.all_subsets[id(param0)] == {0.5, 3.5}
        assert inters.all_knots[id(param0)] == {0, 0.5, 1, 2, 3, 3.5, 4}
        assert inters.all_subsets[id(param1)] == {2.5, 3.5}
        assert inters.all_knots[id(param1)] == {0, 1, 2, 2.5, 3, 3.5, 4}

    @pytest.mark.order(15)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestJordanPolygon::test_begin",
            "TestJordanPolygon::test_creation",
            "TestJordanPolygon::test_error_creation",
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
        test_rectangle.scale((2, 3))
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
        test_square.rotate(radians(np.pi / 6))  # 30 degrees
        assert test_square != good_square
        test_square.rotate(degrees(60))
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
    def test_density_regular_polygon(self):
        # Counter clockwise
        for nsides in range(3, 10):
            angles = np.linspace(0, math.tau, nsides + 1)
            ctrlpoints = np.vstack([np.cos(angles), np.sin(angles)]).T
            jordancurve = FactoryJordan.polygon(ctrlpoints)
            density = lebesgue_density_jordan(jordancurve)
            assert abs(density - 1) < 1e-9

        # Clockwise
        for nsides in range(3, 10):
            angles = np.linspace(math.tau, 0, nsides + 1)
            ctrlpoints = np.vstack([np.cos(angles), np.sin(angles)]).T
            jordancurve = FactoryJordan.polygon(ctrlpoints)
            density = lebesgue_density_jordan(jordancurve)
            assert abs(density - 0) < 1e-9

    @pytest.mark.order(15)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestIntegrateJordan::test_begin"])
    def test_lenght_triangle(self):
        vertices = [(0, 0), (3, 0), (0, 4)]
        jordan_curve = FactoryJordan.polygon(vertices)
        assert jordan_curve.length == 12
        assert jordan_curve.area == 6

        vertices = [(0, 0), (0, 4), (3, 0)]
        jordan_curve = FactoryJordan.polygon(vertices)
        assert jordan_curve.length == 12
        assert jordan_curve.area == -6

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
        assert jordan_curve.length == 4 * side
        assert jordan_curve.area == side * side

        side = 3
        square_vertices = [
            (-side / 2, -side / 2),
            (-side / 2, side / 2),
            (side / 2, side / 2),
            (side / 2, -side / 2),
        ]
        jordan_curve = FactoryJordan.polygon(square_vertices)
        assert jordan_curve.length == 4 * side
        assert jordan_curve.area == -side * side

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
            area = nsides * np.sin(2 * math.pi / nsides) / 2
            angles = np.linspace(0, math.tau, nsides + 1)
            ctrlpoints = np.vstack([np.cos(angles), np.sin(angles)]).T
            jordan_curve = FactoryJordan.polygon(ctrlpoints)
            assert abs(jordan_curve.length - lenght) < 1e-15
            assert abs(jordan_curve.area - area) < 1e-15

            assert (jordan_curve.length - lenght) < 1e-9

    @pytest.mark.order(15)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestIntegrateJordan::test_begin",
            "TestIntegrateJordan::test_density_regular_polygon",
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
