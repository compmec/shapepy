"""
This file contains tests functions to test the module polygon.py
"""

from fractions import Fraction

import pytest

from shapepy.geometry.factory import FactorySegment


@pytest.mark.order(13)
@pytest.mark.dependency(
    depends=[
        "tests/analytic/test_bezier.py::test_all",
        "tests/analytic/test_polynomial.py::test_all",
        "tests/analytic/test_random.py::test_all",
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
    FactorySegment.bezier([(0, 0), (1, 0), (0, 1)])


@pytest.mark.order(13)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_begin", "test_build"])
def test_invert():
    bezier = FactorySegment.bezier([(0, 0), (1, 0), (0, 1)])
    invbez = ~bezier
    assert bezier.domain == invbez.domain
    assert bezier.knots == invbez.knots
    assert bezier(bezier.knots[0]) == invbez(invbez.knots[-1])
    assert bezier(bezier.knots[-1]) == invbez(invbez.knots[0])


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
        curve = FactorySegment.bezier(points)
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
        curve = FactorySegment.bezier(points)
        assert (0, 0) in curve
        assert (1, 0) in curve
        assert (0.5, 0) in curve
        assert (0, 1) not in curve
        assert (0, -1) not in curve

        points = [(0, 1), (0, 0)]
        curve = FactorySegment.bezier(points)
        assert (0, 0) in curve
        assert (0, 1) in curve
        assert (0, 0.5) in curve
        assert (1, 0) not in curve
        assert (-1, 0) not in curve

        points = [(0, 0), (1, 1)]
        curve = FactorySegment.bezier(points)
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
        curve = FactorySegment.bezier(points)
        curvea = FactorySegment.bezier([(0, 0), (half, 0)], [0, 0.5])
        curveb = FactorySegment.bezier([(half, 0), (1, 0)], [0.5, 1])
        assert curve.section([0, half]) == curvea
        assert curve.section([half, 1]) == curveb

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
    segment = FactorySegment.bezier([(0, 0), (1, 0), (0, 1)])
    str(segment)
    repr(segment)


@pytest.mark.order(13)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_build",
        "test_invert",
        "TestDerivate::test_end",
        "TestContains::test_end",
        "TestSplitUnite::test_end",
        "test_print",
    ]
)
def test_all():
    pass
