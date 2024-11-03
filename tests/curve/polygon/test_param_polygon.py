"""
This file contains tests functions to test the module polygon.py
"""

import pytest

from shapepy.curve.polygon import PolygonClosedCurve, PolygonOpenCurve


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "tests/test_point.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestOpenCurve:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_begin"])
    def test_build(self):
        vertices = [(0, 0), (1, 0), (1, 1)]
        PolygonOpenCurve(vertices)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_build"])
    def test_check_vertices(self):
        vertices = [(0, 0), (1, 0), (1, 1)]
        curve = PolygonOpenCurve(vertices)
        assert len(curve.vertices) == 3
        assert curve.vertices[0] == (0, 0)
        assert curve.vertices[1] == (1, 0)
        assert curve.vertices[2] == (1, 1)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_check_vertices"])
    def test_check_vectors(self):
        vertices = [(0, 0), (1, 0), (1, 1)]
        curve = PolygonOpenCurve(vertices)
        assert len(curve.vectors) == 2
        assert curve.vectors[0] == (1, 0)
        assert curve.vectors[1] == (0, 1)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_check_vertices"])
    def test_evaluate_vertices(self):
        vertices = [(0, 0), (1, 0), (1, 1)]
        curve = PolygonOpenCurve(vertices)
        assert curve.eval(0) == curve.vertices[0]
        assert curve.eval(1) == curve.vertices[1]
        assert curve.eval(2) == curve.vertices[2]

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_evaluate_vertices"])
    def test_evaluate_middle(self):
        vertices = [(0, 0), (1, 0), (1, 1)]
        curve = PolygonOpenCurve(vertices)
        assert curve.eval(0.5) == (0.5, 0)
        assert curve.eval(1.5) == (1, 0.5)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_evaluate_vertices"])
    def test_evaluate_derivate(self):
        vertices = [(0, 0), (1, 0), (1, 1)]
        curve = PolygonOpenCurve(vertices)
        assert curve.eval(0, 1) == (1, 0)
        assert curve.eval(0.5, 1) == (1, 0)
        assert curve.eval(1, 1) == (0, 1)
        assert curve.eval(1.5, 1) == (0, 1)
        assert curve.eval(2, 1) == (0, 1)

        assert curve.eval(0, 2) == (0, 0)
        assert curve.eval(0.5, 2) == (0, 0)
        assert curve.eval(1, 2) == (0, 0)
        assert curve.eval(1.5, 2) == (0, 0)
        assert curve.eval(2, 2) == (0, 0)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_evaluate_vertices"])
    def test_projection(self):
        vertices = [(0, 0), (1, 0), (1, 1)]
        curve = PolygonOpenCurve(vertices)
        assert curve.projection((0, 0)) == (0,)
        assert curve.projection((1, 0)) == (1,)
        assert curve.projection((1, 1)) == (2,)
        assert curve.projection((0.5, 0)) == (0.5,)
        assert curve.projection((1, 0.5)) == (1.5,)
        assert curve.projection((0.5, 0.5)) == (0.5, 1.5)
        assert curve.projection((0.875, 0.125)) == (0.875, 1.125)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_check_vertices"])
    def test_compare(self):
        vertices = [(0, 0), (1, 0), (1, 1)]
        curvea = PolygonOpenCurve(vertices)
        curveb = PolygonOpenCurve(vertices)
        assert curvea == curvea
        assert curveb == curveb
        assert curvea == curveb
        assert id(curvea) != id(curveb)

        vertices = [(0, 0), (1, 0), (1, 2)]
        curvec = PolygonClosedCurve(vertices)
        assert curvea != curvec
        assert curveb != curvec

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestOpenCurve::test_compare"])
    def test_section(self):
        vertices = [(0, 0), (1, 0), (1, 1)]
        curvea = PolygonOpenCurve(vertices)
        assert curvea.section(0, 2) == curvea
        vertices = [(0.5, 0), (1, 0), (1, 0.5)]
        curveb = PolygonOpenCurve(vertices)
        assert curvea.section(0.5, 1.5) == curveb

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestOpenCurve::test_begin",
            "TestOpenCurve::test_build",
            "TestOpenCurve::test_check_vertices",
            "TestOpenCurve::test_check_vectors",
            "TestOpenCurve::test_evaluate_vertices",
            "TestOpenCurve::test_evaluate_middle",
            "TestOpenCurve::test_evaluate_derivate",
            "TestOpenCurve::test_projection",
            "TestOpenCurve::test_compare",
            "TestOpenCurve::test_section",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "test_begin",
    ]
)
def test_end():
    pass
