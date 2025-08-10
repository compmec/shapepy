"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction

import pytest

from shapepy.geometry.segment import Segment, clean_segment


@pytest.mark.order(13)
@pytest.mark.dependency(
    depends=[
        "tests/analytic/test_bezier.py::test_all",
        "tests/analytic/test_polynomial.py::test_all",
        "tests/analytic/test_derivate.py::test_all",
        "tests/analytic/test_integrate.py::test_all",
        "tests/analytic/test_tools.py::test_all",
        "tests/geometry/test_point.py::test_all",
        "tests/geometry/test_box.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(13)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin"])
def test_build():
    Segment([(0, 0), (1, 0), (0, 1)])


class TestDerivate:
    @pytest.mark.order(13)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "test_build",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestDerivate::test_begin"])
    def test_planar_bezier(self):
        points = [(0, 0), (1, 0), (0, 1)]
        curve = Segment(points)
        dcurve = curve.derivate()
        assert id(dcurve) != id(curve)

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestDerivate::test_begin",
            "TestDerivate::test_planar_bezier",
        ]
    )
    def test_end(self):
        pass


class TestOperations:
    @pytest.mark.order(13)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOperations::test_begin"])
    def test_clean_segment(self):
        points = [(0, 0), (1, 0)]
        curve = clean_segment(Segment(points))
        assert curve.degree == 1

        points = [(2, 3), (-1, 4)]
        curve = clean_segment(Segment(points))
        assert curve.degree == 1

        points = [(2, 3), (-1, 4)]
        curve = clean_segment(Segment(points))
        assert curve.degree == 1

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestOperations::test_begin",
            "TestOperations::test_clean_segment",
        ]
    )
    def test_clean_quadratic(self):
        points = [(0, 0), (1, 0), (2, 0)]
        curve = Segment(points)
        assert curve.degree == 2
        curve = clean_segment(curve)
        assert curve.degree == 1

        points = [(0, 2), (1, 4), (2, 6)]
        curve = Segment(points)
        assert curve.degree == 2
        curve = clean_segment(curve)
        assert curve.degree == 1

        points = [(2, 3), (-1, 4), (-4, 5)]
        curve = Segment(points)
        assert curve.degree == 2
        curve = clean_segment(curve)
        assert curve.degree == 1

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestOperations::test_begin",
            "TestOperations::test_clean_segment",
            "TestOperations::test_clean_quadratic",
        ]
    )
    def test_end(self):
        pass


class TestContains:
    @pytest.mark.order(13)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestContains::test_begin"])
    def test_line(self):
        points = [(0, 0), (1, 0)]
        curve = Segment(points)
        assert (0, 0) in curve
        assert (1, 0) in curve
        assert (0.5, 0) in curve
        assert (0, 1) not in curve
        assert (0, -1) not in curve

        points = [(0, 1), (0, 0)]
        curve = Segment(points)
        assert (0, 0) in curve
        assert (0, 1) in curve
        assert (0, 0.5) in curve
        assert (1, 0) not in curve
        assert (-1, 0) not in curve

        points = [(0, 0), (1, 1)]
        curve = Segment(points)
        assert (0, 0) in curve
        assert (1, 1) in curve
        assert (0.5, 0.5) in curve
        assert (0.25, 0.5) not in curve
        assert (0.75, 0.5) not in curve
        assert (-1, -1) not in curve
        assert (-0.1, -0.1) not in curve

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestContains::test_begin",
            "TestContains::test_line",
        ]
    )
    def test_end(self):
        pass


class TestSplitUnite:
    @pytest.mark.order(13)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestSplitUnite::test_begin"])
    def test_middle(self):
        half = Fraction(1, 2)
        points = [(0, 0), (1, 0)]
        curve = Segment(points)
        curvea, curveb = curve.split([half])
        assert curvea == Segment([(0, 0), (half, 0)])
        assert curveb == Segment([(half, 0), (1, 0)])

        test = curvea | curveb
        assert test == curve

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestSplitUnite::test_begin",
            "TestSplitUnite::test_middle",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(13)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_build",
    ]
)
def test_print():
    segment = Segment([(0, 0), (1, 0), (0, 1)])
    str(segment)
    repr(segment)


@pytest.mark.order(13)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_build",
        "TestDerivate::test_end",
        "TestOperations::test_end",
        "TestContains::test_end",
        "TestSplitUnite::test_end",
        "test_print",
    ]
)
def test_all():
    pass
