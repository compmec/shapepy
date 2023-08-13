"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction as frac

import numpy as np
import pytest

from compmec.shape.polygon import (
    ConvexHull,
    ConvexPolygon,
    Point2D,
    Polygon,
    Segment,
    SimplePolygon,
)


@pytest.mark.order(2)
@pytest.mark.dependency()
def test_begin():
    pass


class TestPoint:
    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(2)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestPoint::test_begin"])
    def test_creation(self):
        Point2D(0, 0)
        Point2D(1, 1)
        Point2D(0.0, 0.0)
        zero = frac(0)
        Point2D(zero, zero)

        Point2D((0, 0))
        point = (0, 0)
        Point2D(point)
        point = [0, 0]
        Point2D(point)

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=["TestPoint::test_begin", "TestPoint::test_creation"]
    )
    def test_error_creation(self):
        with pytest.raises(TypeError):
            Point2D("1", 1.0)
        with pytest.raises(TypeError):
            Point2D(1, "asd")
        with pytest.raises(TypeError):
            Point2D(1, None)

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestPoint::test_begin",
            "TestPoint::test_creation",
            "TestPoint::test_error_creation",
        ]
    )
    def test_indexable(self):
        point = Point2D(0, 0)
        assert point[0] == 0
        assert point[1] == 0

        point = Point2D(1, 2)
        assert point[0] == 1
        assert point[1] == 2

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestPoint::test_begin",
            "TestPoint::test_creation",
            "TestPoint::test_indexable",
        ]
    )
    def test_addsub(self):
        pointa = Point2D(0, 0)
        pointb = Point2D(1, 1)
        assert pointa + pointb == pointb
        assert pointa - pointb == -pointb
        assert pointb + pointa == pointb
        assert pointb - pointa == pointb

        pointa = Point2D(3, 4)
        pointb = Point2D(12, 5)
        aplusb = Point2D(15, 9)
        aminusb = Point2D(-9, -1)
        assert pointa + pointb == aplusb
        assert pointa - pointb == aminusb
        assert pointb + pointa == aplusb
        assert pointb - pointa == -aminusb

        assert pointa + (12, 5) == aplusb
        assert pointa - (12, 5) == aminusb

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestPoint::test_begin",
            "TestPoint::test_creation",
            "TestPoint::test_indexable",
        ]
    )
    def test_norm(self):
        point = Point2D(0, 0)
        assert abs(point) == 0
        point = Point2D(1, 0)
        assert abs(point) == 1
        point = Point2D(3, 4)
        assert abs(point) == 5
        point = Point2D(5, 12)
        assert abs(point) == 13

        point = Point2D(frac(3, 5), frac(4, 5))
        assert abs(point) == 1
        point = Point2D(frac(5, 13), frac(12, 13))
        assert abs(point) == 1

        point = Point2D(0.0, 0.0)
        assert abs(point) == 0.0
        point = Point2D(1.0, 0.0)
        assert abs(point) == 1.0
        point = Point2D(3.0, 4.0)
        assert abs(point) == 5
        point = Point2D(5.0, 12.0)
        assert abs(point) == 13

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestPoint::test_begin",
            "TestPoint::test_creation",
            "TestPoint::test_norm",
        ]
    )
    def test_inner(self):
        pointa = Point2D(0, 0)
        pointb = Point2D(0, 0)
        assert pointa.inner(pointb) == 0
        assert pointb.inner(pointa) == 0

        pointa = Point2D(1, 0)
        pointb = Point2D(0, 1)
        assert pointa.inner(pointb) == 0
        assert pointb.inner(pointa) == 0

        pointa = Point2D(1, 1)
        pointb = Point2D(1, 1)
        assert pointa.inner(pointb) == 2
        assert pointb.inner(pointa) == 2

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=["TestPoint::test_begin", "TestPoint::test_creation"]
    )
    def test_cross(self):
        pointa = Point2D(0, 0)
        pointb = Point2D(0, 0)
        assert pointa.cross(pointb) == 0
        assert pointb.cross(pointa) == 0

        pointa = Point2D(1, 0)
        pointb = Point2D(0, 1)
        assert pointa.cross(pointb) == 1
        assert pointb.cross(pointa) == -1

        pointa = Point2D(1, 1)
        pointb = Point2D(1, 1)
        assert pointa.cross(pointb) == 0
        assert pointb.cross(pointa) == 0

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestPoint::test_begin",
            "TestPoint::test_creation",
            "TestPoint::test_norm",
            "TestPoint::test_inner",
            "TestPoint::test_cross",
        ]
    )
    def test_equivalent_expression(self):
        pta = Point2D(frac(5, 13), frac(12, 13))
        ptb = Point2D(frac(3, 5), frac(4, 5))
        assert pta | ptb == pta.inner(ptb)
        assert ptb | pta == ptb.inner(pta)
        assert pta * ptb == pta.inner(ptb)
        assert ptb * pta == ptb.inner(pta)
        assert pta ^ ptb == pta.cross(ptb)
        assert ptb ^ pta == ptb.cross(pta)

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestPoint::test_begin",
            "TestPoint::test_creation",
            "TestPoint::test_error_creation",
            "TestPoint::test_indexable",
            "TestPoint::test_addsub",
            "TestPoint::test_inner",
            "TestPoint::test_norm",
            "TestPoint::test_cross",
            "TestPoint::test_equivalent_expression",
        ]
    )
    def test_end(self):
        pass


class TestSegment:
    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestPoint::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(2)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestSegment::test_begin"])
    def test_creation(self):
        pta = Point2D(0, 0)
        ptb = Point2D(1, 1)
        Segment(pta, ptb)

        half = frac(1, 2)
        pta = (half, half)
        ptb = (3 * half, half)
        Segment(pta, ptb)

    @pytest.mark.order(2)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestSegment::test_begin"])
    def test_projection(self):
        one = frac(1)

        pta = Point2D(0, 0)
        ptb = Point2D(1, 1)
        seg = Segment(pta, ptb)
        point = (one / 2, one / 2)
        assert seg.projection(point) == one / 2
        point = (one / 3, one / 3)
        assert seg.projection(point) == one / 3

        pta = Point2D(0, 0)
        ptb = Point2D(1, 0)
        seg = Segment(pta, ptb)
        assert seg.projection((0, 0)) == 0
        assert seg.projection((1, 0)) == 1
        assert seg.projection((2, 0)) == 2
        assert seg.projection((-1, 0)) == -1

        pta = Point2D(10, 0)
        ptb = Point2D(11, 0)
        seg = Segment(pta, ptb)
        assert seg.projection((0, 0)) == -10
        assert seg.projection((1, 0)) == -9
        assert seg.projection((2, 0)) == -8
        assert seg.projection((10, 0)) == 0
        assert seg.projection((11, 0)) == 1
        assert seg.projection((12, 0)) == 2

    @pytest.mark.order(2)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestSegment::test_begin", "TestSegment::test_projection"]
    )
    def test_intersection(self):
        one = frac(1)

        # Parallel, but not colinear
        pta = Point2D(0, 0)
        ptb = Point2D(1, 0)
        seg0 = Segment(pta, ptb)
        pta = Point2D(0, 1)
        ptb = Point2D(1, 1)
        seg1 = Segment(pta, ptb)
        assert (seg0 & seg1) is None
        assert (seg1 & seg0) is None

        # Colinear, but not coincident
        pta = Point2D(0, 0)
        ptb = Point2D(1, 0)
        ptc = Point2D(2, 0)
        ptd = Point2D(3, 0)
        seg0 = Segment(pta, ptb)
        seg1 = Segment(ptc, ptd)
        assert (seg0 & seg1) is None
        assert (seg1 & seg0) is None

        # Colinear, but intersect only once
        pta = Point2D(0, 0)
        ptb = Point2D(1, 0)
        ptc = Point2D(2, 0)
        seg0 = Segment(pta, ptb)
        seg1 = Segment(ptb, ptc)
        assert (seg0 & seg1) == (1, 0)
        assert (seg1 & seg0) == (0, 1)
        seg1 = Segment(ptc, ptb)
        assert (seg0 & seg1) == (1, 1)
        assert (seg1 & seg0) == (1, 1)
        seg0 = Segment(ptb, pta)
        seg1 = Segment(ptb, ptc)
        assert (seg0 & seg1) == (0, 0)
        assert (seg1 & seg0) == (0, 0)
        seg1 = Segment(ptc, ptb)
        assert (seg0 & seg1) == (0, 1)
        assert (seg1 & seg0) == (1, 0)

        # Non parallel lines, intersect once
        pta = Point2D(0, 0)
        ptb = Point2D(1, 1)
        seg0 = Segment(pta, ptb)
        pta = Point2D(1, 0)
        ptb = Point2D(0, 1)
        seg1 = Segment(pta, ptb)
        assert seg0 & seg1 == (one / 2, one / 2)
        assert seg1 & seg0 == (one / 2, one / 2)

        pta = Point2D(0, 0)
        ptb = Point2D(2, 2)
        seg0 = Segment(pta, ptb)
        pta = Point2D(1, 0)
        ptb = Point2D(0, 1)
        seg1 = Segment(pta, ptb)
        assert (seg0 & seg1) == (one / 4, one / 2)
        assert (seg1 & seg0) == (one / 2, one / 4)

        # Colinear, intersect sub-interval
        pta = Point2D(0, 0)
        ptb = Point2D(1, 0)
        ptc = Point2D(2, 0)
        ptd = Point2D(3, 0)
        seg0 = Segment(pta, ptc)
        seg1 = Segment(ptb, ptd)
        assert (seg0 & seg1) == Segment(ptb, ptc)
        assert (seg1 & seg0) == Segment(ptb, ptc)
        seg0 = Segment(ptc, pta)
        seg1 = Segment(ptb, ptd)
        assert (seg0 & seg1) == Segment(ptc, ptb)
        assert (seg1 & seg0) == Segment(ptb, ptc)
        seg0 = Segment(ptc, pta)
        seg1 = Segment(ptd, ptb)
        assert (seg0 & seg1) == Segment(ptc, ptb)
        assert (seg1 & seg0) == Segment(ptc, ptb)
        seg0 = Segment(pta, ptc)
        seg1 = Segment(ptd, ptb)
        assert (seg0 & seg1) == Segment(ptb, ptc)
        assert (seg1 & seg0) == Segment(ptc, ptb)

    @pytest.mark.order(2)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestSegment::test_begin",
            "TestSegment::test_projection",
            "TestSegment::test_intersection",
        ]
    )
    def test_contains_point(self):
        one = frac(1)
        pta = Point2D(0, 0)
        ptb = Point2D(1, 0)
        seg0 = Segment(pta, ptb)
        assert (one / 2, 0) in seg0
        assert (one / 3, 0) in seg0
        assert (2 * one / 3, 0) in seg0

        assert (one / 2, one / 2) not in seg0

    @pytest.mark.order(2)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestSegment::test_begin",
            "TestSegment::test_projection",
            "TestSegment::test_intersection",
            "TestSegment::test_contains_point",
        ]
    )
    def test_contains_segment(self):
        pta = Point2D(0, 0)
        ptb = Point2D(1, 0)
        ptc = Point2D(2, 0)
        ptd = Point2D(3, 0)
        seg0 = Segment(pta, ptd)
        seg1 = Segment(ptb, ptc)
        assert seg0 in seg0
        assert seg1 in seg0
        assert seg0 not in seg1

        assert (seg0 & seg1) in seg0

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestSegment::test_begin",
            "TestSegment::test_creation",
            "TestSegment::test_projection",
            "TestSegment::test_intersection",
            "TestSegment::test_contains_point",
            "TestSegment::test_contains_segment",
        ]
    )
    def test_end(self):
        pass


class TestInitialPolygon:
    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestPoint::test_end", "TestSegment::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestInitialPolygon::test_begin"])
    def test_creation(self):
        points = [(0, 0), (1, 0), (0, 1)]
        Polygon(points)
        points = [(0, 0), (1, 0), (1, 1), (0, 1)]
        Polygon(points)
        points = [(0, 0), (3, 0), (1, 1), (0, 3)]
        Polygon(points)

        points = [(0, 0), (1, 0), (0, 1), (0, 0)]
        with pytest.raises(ValueError):
            Polygon(points)

    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestInitialPolygon::test_begin"])
    def test_fail_creation(self):
        points = [(0, 0), (3, 0), (1, 1), (0, 3), (0, 0)]
        with pytest.raises(ValueError):  # Init pt = End pt
            Polygon(points)

        points = [(0, 0), (1, 0), (0, 1), (1, 1)]
        with pytest.raises(ValueError):  # Intersection between lines
            Polygon(points)

        points = [(0, 0), (2, 0), (2, 1), (1, 0), (0, 1)]
        with pytest.raises(ValueError):
            Polygon(points)

        points = [(0, 0), (2, 0), (2, 1), (1, -1), (0, 1)]
        with pytest.raises(ValueError):
            Polygon(points)

        points = [(0, 0), (2, 0), (1, 0), (2, 1), (1, -1), (0, 1)]
        with pytest.raises(ValueError):
            Polygon(points)

        points = [(0, 0), (3, 0), (3, 1), (2, 0), (1, 0), (0, 1)]
        with pytest.raises(ValueError):
            Polygon(points)

        with pytest.raises(ValueError):
            Polygon("asd")

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestInitialPolygon::test_begin",
            "TestInitialPolygon::test_creation",
        ]
    )
    def test_vertices(self):
        points = [(0, 0), (1, 0), (0, 1)]
        poly = Polygon(points)
        for point, vertex in zip(points, poly.vertices):
            assert vertex == point
        points = [(0, 0), (1, 0), (1, 1), (0, 1)]
        poly = Polygon(points)
        for point, vertex in zip(points, poly.vertices):
            assert vertex == point
        points = [(0, 0), (3, 0), (1, 1), (0, 3)]
        poly = Polygon(points)
        for point, vertex in zip(points, poly.vertices):
            assert vertex == point

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=["TestInitialPolygon::test_begin", "TestInitialPolygon::test_creation"]
    )
    def test_clean(self):
        points = [(0, 0), (1, 0), (0, 1)]
        test_polygon = Polygon(points)
        test_polygon = test_polygon.clean()
        test_vertices = test_polygon.vertices
        good_vertices = [(0, 0), (1, 0), (0, 1)]
        for test_vertex, good_vertex in zip(test_vertices, good_vertices):
            assert test_vertex == good_vertex

        points = [(0, 0), (2, 0), (1, 1), (0, 2)]
        test_polygon = Polygon(points)
        test_polygon = test_polygon.clean()
        test_vertices = test_polygon.vertices
        good_vertices = [(0, 0), (2, 0), (0, 2)]
        for test_vertex, good_vertex in zip(test_vertices, good_vertices):
            assert test_vertex == good_vertex

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestInitialPolygon::test_begin",
            "TestInitialPolygon::test_creation",
            "TestInitialPolygon::test_clean",
        ]
    )
    def test_convex(self):
        points = [(0, 0), (1, 0), (0, 1)]
        assert type(Polygon(points)) is ConvexPolygon
        points = [(0, 0), (1, 0), (0.5, 0.5), (0, 1)]
        assert type(Polygon(points)) is ConvexPolygon
        points = [(0, 0), (1, 0), (1, 1), (0, 1)]
        assert type(Polygon(points)) is ConvexPolygon

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestInitialPolygon::test_begin",
            "TestInitialPolygon::test_creation",
            "TestInitialPolygon::test_convex",
            "TestInitialPolygon::test_clean",
        ]
    )
    def test_simple(self):
        vertices = [(0, 0), (3, 0), (1, 1), (0, 3)]
        assert type(Polygon(vertices)) is SimplePolygon
        vertices = [(0, 0), (2, 0), (1, 1), (2, 2), (0, 2), (0, 1)]
        assert type(Polygon(vertices)) is SimplePolygon
        vertices = [
            (0, 0),
            (3, 0),
            (2, 1),
            (3, 2),
            (2, 2),
            (1, 2),
            (0, 2),
            (1, 1),
            (0, 1),
        ]
        assert type(Polygon(vertices)) is SimplePolygon

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestInitialPolygon::test_begin",
            "TestInitialPolygon::test_creation",
            "TestInitialPolygon::test_clean",
            "TestInitialPolygon::test_convex",
            "TestInitialPolygon::test_simple",
        ]
    )
    def test_convex_hull(self):
        vertices = [(0, 0), (1, 0), (0, 1)]
        convex_hull = ConvexHull(Polygon(vertices))
        for test_vertex, good_vertex in zip(convex_hull.vertices, vertices):
            assert test_vertex == good_vertex

        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        convex_hull = ConvexHull(Polygon(vertices))
        for test_vertex, good_vertex in zip(convex_hull.vertices, vertices):
            assert test_vertex == good_vertex

        vertices = [(0, 0), (3, 0), (1, 1), (0, 3)]
        convex_hull = ConvexHull(Polygon(vertices))
        good_vertices = [(0, 0), (3, 0), (0, 3)]
        for test_vertex, good_vertex in zip(convex_hull.vertices, good_vertices):
            assert test_vertex == good_vertex

        vertices = [(0, 0), (2, 0), (1, 1), (2, 2), (0, 2), (0, 1)]
        convex_hull = ConvexHull(Polygon(vertices))
        good_vertices = [(0, 0), (2, 0), (2, 2), (0, 2)]
        for test_vertex, good_vertex in zip(convex_hull.vertices, good_vertices):
            assert test_vertex == good_vertex

        vertices = [
            (0, 0),
            (3, 0),
            (2, 1),
            (3, 2),
            (2, 2),
            (1, 2),
            (0, 2),
            (1, 1),
            (0, 1),
        ]
        convex_hull = ConvexHull(Polygon(vertices))
        good_vertices = [(0, 0), (3, 0), (3, 2), (0, 2)]
        for test_vertex, good_vertex in zip(convex_hull.vertices, good_vertices):
            assert test_vertex == good_vertex

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestInitialPolygon::test_begin",
            "TestInitialPolygon::test_creation",
            "TestInitialPolygon::test_convex",
            "TestInitialPolygon::test_simple",
            "TestInitialPolygon::test_convex_hull",
        ]
    )
    def test_end(self):
        pass


class TestComparatePolygons:
    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestInitialPolygon::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestComparatePolygons::test_begin"])
    def test_triangles(self):
        points = [(0, 0), (1, 0), (0, 1)]
        triangle = Polygon(points)
        assert triangle == triangle

        points0 = [(0, 0), (1, 0), (0, 1)]
        triangle0 = Polygon(points0)
        points1 = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
        triangle1 = Polygon(points1)
        assert triangle1 == triangle0

        points0 = [(0, 0), (1, 0), (0, 1)]
        triangle0 = Polygon(points0)
        points1 = [(1, 0), (0, 1), (0, 0)]
        triangle1 = Polygon(points1)
        assert triangle1 == triangle0

        points0 = [(0, 0), (1, 0), (0, 1)]
        triangle0 = Polygon(points0)
        points1 = [(0, 1), (0, 0), (1, 0)]
        triangle1 = Polygon(points1)
        assert triangle1 == triangle0

        points0 = [(0, 0), (1, 0), (0, 1)]
        triangle0 = Polygon(points0)
        points1 = [(0, 0), (-1, 0), (0, 1)]
        triangle1 = Polygon(points1)
        assert triangle1 != triangle0

    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestComparatePolygons::test_begin"])
    def test_square(self):
        points0 = [(0, 0), (1, 0), (1, 1), (0, 1)]
        square0 = Polygon(points0)
        assert square0 == square0
        points1 = [(1, 0), (1, 1), (0, 1), (0, 0)]
        square1 = Polygon(points1)
        assert square1 == square0
        points2 = [(1, 1), (0, 1), (0, 0), (1, 0)]
        square2 = Polygon(points2)
        assert square2 == square0
        points3 = [(0, 1), (0, 0), (1, 0), (1, 1)]
        square3 = Polygon(points3)
        assert square3 == square0

        points4 = [(2, 2), (3, 2), (3, 3), (2, 3)]
        square4 = Polygon(points4)
        assert square4 != square0

    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestComparatePolygons::test_begin"])
    def test_others(self):
        points = [(0, 0), (1, 0), (0, 1)]
        triangle = Polygon(points)
        points = [(0, 0), (1, 0), (1, 1), (0, 1)]
        square = Polygon(points)
        assert triangle != square

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestComparatePolygons::test_begin",
            "TestComparatePolygons::test_triangles",
            "TestComparatePolygons::test_square",
            "TestComparatePolygons::test_others",
        ]
    )
    def test_end(self):
        pass


class TestPointOnBoundary:
    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestInitialPolygon::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestPointOnBoundary::test_begin"])
    def test_integer(self):
        points = [[0, 0], [1, 0], [1, 1], [0, 1]]
        square = Polygon(points)
        assert (0, 0) in square
        assert (1, 0) in square
        assert (1, 1) in square
        assert (0, 1) in square

        points = [[0, 0], [2, 0], [2, 1], [0, 1]]
        square = Polygon(points)
        assert (0, 0) in square
        assert (1, 0) in square
        assert (2, 0) in square
        assert (2, 1) in square
        assert (1, 1) in square
        assert (0, 1) in square

        points = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        square = Polygon(points)
        assert (1, 0) in square
        assert (0, 1) in square
        assert (-1, 0) in square
        assert (0, -1) in square

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=["TestPointOnBoundary::test_begin", "TestPointOnBoundary::test_integer"]
    )
    def test_fraction(self):
        zero, half, one = frac(0), frac(1, 2), frac(1)
        points = [[0, 0], [1, 0], [1, 1], [0, 1]]
        square = Polygon(points)
        assert (zero, zero) in square
        assert (half, zero) in square
        assert (one, zero) in square
        assert (one, half) in square
        assert (one, one) in square
        assert (half, one) in square
        assert (zero, one) in square
        assert (zero, half) in square

        points = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        square = Polygon(points)
        assert (one, zero) in square
        assert (half, half) in square
        assert (zero, one) in square
        assert (-half, half) in square
        assert (-one, zero) in square
        assert (-half, -half) in square
        assert (zero, -one) in square
        assert (half, -half) in square

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestPointOnBoundary::test_begin",
            "TestPointOnBoundary::test_integer",
            "TestPointOnBoundary::test_fraction",
        ]
    )
    def test_end(self):
        pass


class TestPointInOpenset:
    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestInitialPolygon::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestPointInOpenset::test_begin"])
    def test_integer(self):
        points = [[0, 0], [2, 0], [2, 2], [0, 2]]
        square = Polygon(points)
        assert (1, 1) in square
        points = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        square = Polygon(points)
        assert (0, 0) in square

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=["TestPointInOpenset::test_begin", "TestPointInOpenset::test_integer"]
    )
    def test_fraction(self):
        one = frac(1)
        points = [[0, 0], [2, 0], [2, 2], [0, 2]]
        square = Polygon(points)
        for x in (one / 2, one, 3 * one / 2):
            for y in (one / 2, one, 3 * one / 2):
                assert (x, y) in square

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestPointInOpenset::test_begin",
            "TestPointInOpenset::test_integer",
            "TestPointInOpenset::test_fraction",
        ]
    )
    def test_end(self):
        pass


class TestInsideConvexPolygon:
    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestInitialPolygon::test_end",
            "TestPointOnBoundary::test_end",
            "TestPointInOpenset::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestInsideConvexPolygon::test_begin"])
    def test_same_polygon(self):
        points = [[0, 0], [1, 0], [1, 1], [0, 1]]
        square = Polygon(points)
        assert square in square

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestInsideConvexPolygon::test_begin",
            "TestInsideConvexPolygon::test_same_polygon",
        ]
    )
    def test_complete_inside(self):
        big_points = [[0, 0], [3, 0], [3, 3], [0, 3]]
        big_square = Polygon(big_points)
        small_points = [[1, 1], [2, 1], [2, 2], [1, 2]]
        small_square = Polygon(small_points)
        assert small_square in big_square
        assert big_square not in small_square

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestInsideConvexPolygon::test_begin",
            "TestInsideConvexPolygon::test_same_polygon",
            "TestInsideConvexPolygon::test_complete_inside",
        ]
    )
    def test_commum_vertices(self):
        hexagon_points = [(2, 0), (1, 1), (-1, 1), (-2, 0), (-1, -1), (1, -1)]
        hexagon = Polygon(hexagon_points)
        triangle_points = [(1, 1), (-2, 0), (1, -1)]
        triangle = Polygon(triangle_points)
        assert triangle in hexagon
        assert hexagon not in triangle
        triangle_points = [(-1, 1), (2, 0), (-1, -1)]
        triangle = Polygon(triangle_points)
        assert triangle in hexagon

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestInsideConvexPolygon::test_begin",
            "TestInsideConvexPolygon::test_same_polygon",
            "TestInsideConvexPolygon::test_complete_inside",
            "TestInsideConvexPolygon::test_commum_vertices",
        ]
    )
    def test_commum_edge(self):
        square_points = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
        square = Polygon(square_points)
        triangle = Polygon([[-1, -1], (1, -1), (1, 1)])
        assert triangle in square
        assert square not in triangle
        triangle = Polygon([[-1, -1], (1, 1), (-1, 1)])
        assert triangle in square
        assert square not in triangle

        hexagon_points = [(2, 0), (1, 1), (-1, 1), (-2, 0), (-1, -1), (1, -1)]
        hexagon = Polygon(hexagon_points)
        assert square in hexagon
        assert hexagon not in square

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestInsideConvexPolygon::test_begin",
            "TestInsideConvexPolygon::test_same_polygon",
            "TestInsideConvexPolygon::test_complete_inside",
            "TestInsideConvexPolygon::test_commum_vertices",
            "TestInsideConvexPolygon::test_commum_edge",
        ]
    )
    def test_combination(self):
        square_points = [(1, 0), (3, 0), (3, 3), (1, 3)]
        triangle_points = [(0, 0), (2, 4), (4, 0)]
        square = Polygon(square_points)
        triangle = Polygon(triangle_points)
        assert triangle not in square
        assert square not in triangle

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestInsideConvexPolygon::test_begin",
            "TestInsideConvexPolygon::test_same_polygon",
            "TestInsideConvexPolygon::test_complete_inside",
            "TestInsideConvexPolygon::test_commum_vertices",
            "TestInsideConvexPolygon::test_commum_edge",
            "TestInsideConvexPolygon::test_combination",
        ]
    )
    def test_end(self):
        pass


class TestInsideNonConvexPolygon:
    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestInsideConvexPolygon::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestInsideNonConvexPolygon::test_begin"])
    def test_same_polygon(self):
        points = [[0, 0], [3, 0], [1, 1], [0, 3]]
        polygon = Polygon(points)
        assert polygon in polygon

        points = [[0, 0], [3, 0], [2, 1], [3, 2], [0, 2], [1, 1], [0, 1]]
        polygon = Polygon(points)
        assert polygon in polygon

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestInsideNonConvexPolygon::test_begin",
            "TestInsideNonConvexPolygon::test_same_polygon",
        ]
    )
    def test_complete_inside(self):
        big_points = [[0, 0], [5, 0], [4, 1], [4, 2], [5, 3], [0, 3], [1, 2], [1, 1]]
        small_points = [[2, 1], [3, 1], [3, 2], [2, 2]]
        big_polygon = Polygon(big_points)
        small_square = Polygon(small_points)
        assert small_square in big_polygon
        assert big_polygon not in small_square

        big_points = [(0, 0), (5, 0), (5, 3), (3, 3), (3, 4), (5, 4), (5, 7), (0, 7)]
        small_points = [(1, 1), (4, 1), (4, 2), (2, 2), (2, 5), (4, 5), (4, 6), (2, 6)]
        big_polygon = Polygon(big_points)
        small_polygon = Polygon(small_points)
        assert small_polygon in big_polygon
        assert big_polygon not in small_polygon

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestInsideNonConvexPolygon::test_begin",
            "TestInsideNonConvexPolygon::test_same_polygon",
            "TestInsideNonConvexPolygon::test_complete_inside",
        ]
    )
    def test_others(self):
        big_points = [(0, 0), (5, 0), (5, 3), (3, 3), (3, 4), (5, 4), (5, 7), (0, 7)]
        small_points = [(1, 1), (4, 1), (4, 6), (1, 6)]
        big_poly = Polygon(big_points)
        small_poly = Polygon(small_points)
        assert small_poly not in big_poly
        assert big_poly not in small_poly

        big_points = [(0, 0), (3, 0), (3, 1), (2, 1), (2, 4), (3, 4), (3, 5), (0, 5)]
        small_points = [(1, 2), (2, 2), (2, 3), (1, 3)]
        big_poly = Polygon(big_points)
        small_poly = Polygon(small_points)
        assert small_poly in big_poly
        assert big_poly not in small_poly

        big_points = [
            (0, 0),
            (6, 0),
            (6, 2),
            (5, 2),
            (5, 3),
            (6, 3),
            (6, 4),
            (4, 4),
            (4, 5),
            (6, 5),
            (6, 7),
            (0, 7),
        ]
        small_points = [(1, 1), (5, 1), (5, 6), (1, 6)]
        big_poly = Polygon(big_points)
        small_poly = Polygon(small_points)
        assert small_poly not in big_poly
        assert big_poly not in small_poly

    @pytest.mark.order(2)
    @pytest.mark.dependency(
        depends=[
            "TestInsideNonConvexPolygon::test_begin",
            "TestInsideNonConvexPolygon::test_same_polygon",
            "TestInsideNonConvexPolygon::test_complete_inside",
            "TestInsideNonConvexPolygon::test_others",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(2)
@pytest.mark.dependency(
    depends=[
        "TestPoint::test_end",
        "TestSegment::test_end",
        "TestInitialPolygon::test_end",
        "TestComparatePolygons::test_end",
        "TestPointOnBoundary::test_end",
        "TestPointInOpenset::test_end",
        "TestInsideConvexPolygon::test_end",
        "TestInsideNonConvexPolygon::test_end",
    ]
)
def test_print():
    pointa = Point2D(0, 0)
    pointb = Point2D(1.0, 1.0)
    print(pointa)
    print(repr(pointa))
    print(type(pointa))
    print(pointb)
    print(repr(pointb))
    print(type(pointb))
    segment = Segment(pointa, pointb)
    print(segment)
    print(repr(segment))
    print(type(segment))
    points = [(0, 0), (1, 0), (0, 1)]
    polygon = Polygon(points)
    print(polygon)
    print(repr(polygon))
    print(type(polygon))


@pytest.mark.order(2)
@pytest.mark.dependency(
    depends=[
        "TestPoint::test_end",
        "TestSegment::test_end",
        "TestInitialPolygon::test_end",
        "TestComparatePolygons::test_end",
        "TestPointOnBoundary::test_end",
        "TestPointInOpenset::test_end",
        "TestInsideConvexPolygon::test_end",
        "TestInsideNonConvexPolygon::test_end",
    ]
)
def test_end():
    pass
