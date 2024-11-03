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
    @pytest.mark.dependency(depends=["TestOpenCurve::test_compare"])
    def test_lenght(self):
        vertices = [(0, 0), (3, 0)]
        curvea = PolygonOpenCurve(vertices)
        assert curvea.lenght == 3

        vertices = [(0, 0), (3, 4)]
        curvea = PolygonOpenCurve(vertices)
        assert curvea.lenght == 5

        vertices = [(0, 0), (1, 0), (1, 1)]
        curvea = PolygonOpenCurve(vertices)
        assert curvea.lenght == 2

        vertices = [(0, 0), (3, 0), (3, 4)]
        curvea = PolygonOpenCurve(vertices)
        assert curvea.lenght == 7

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
            "TestOpenCurve::test_lenght",
        ]
    )
    def test_end(self):
        pass


class TestClosedCurve:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin", "TestOpenCurve::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_begin"])
    def test_build(self):
        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        PolygonClosedCurve(vertices)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_build"])
    def test_check_vertices(self):
        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        curve = PolygonClosedCurve(vertices)
        assert len(curve.vertices) == 4
        assert curve.vertices[0] == (0, 0)
        assert curve.vertices[1] == (1, 0)
        assert curve.vertices[2] == (1, 1)
        assert curve.vertices[3] == (0, 1)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_check_vertices"])
    def test_check_vectors(self):
        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        curve = PolygonClosedCurve(vertices)
        assert len(curve.vectors) == 4
        assert curve.vectors[0] == (1, 0)
        assert curve.vectors[1] == (0, 1)
        assert curve.vectors[2] == (-1, 0)
        assert curve.vectors[3] == (0, -1)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_check_vertices"])
    def test_evaluate_vertices(self):
        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        curve = PolygonClosedCurve(vertices)
        assert curve.eval(0) == curve.vertices[0]
        assert curve.eval(1) == curve.vertices[1]
        assert curve.eval(2) == curve.vertices[2]
        assert curve.eval(3) == curve.vertices[3]
        assert curve.eval(4) == curve.vertices[0]

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestClosedCurve::test_evaluate_vertices"]
    )
    def test_evaluate_middle(self):
        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        curve = PolygonClosedCurve(vertices)
        assert curve.eval(0.5) == (0.5, 0)
        assert curve.eval(1.5) == (1, 0.5)
        assert curve.eval(2.5) == (0.5, 1)
        assert curve.eval(3.5) == (0, 0.5)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestClosedCurve::test_evaluate_vertices"]
    )
    def test_evaluate_derivate(self):
        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        curve = PolygonClosedCurve(vertices)
        assert curve.eval(0, 1) == (1, 0)
        assert curve.eval(0.5, 1) == (1, 0)
        assert curve.eval(1, 1) == (0, 1)
        assert curve.eval(1.5, 1) == (0, 1)
        assert curve.eval(2, 1) == (-1, 0)
        assert curve.eval(2.5, 1) == (-1, 0)
        assert curve.eval(3, 1) == (0, -1)
        assert curve.eval(3.5, 1) == (0, -1)
        assert curve.eval(4, 1) == (1, 0)

        for node in (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4):
            assert curve.eval(node, 2) == (0, 0)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=["TestClosedCurve::test_evaluate_vertices"]
    )
    def test_projection(self):
        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        curve = PolygonClosedCurve(vertices)
        assert curve.projection((0, 0)) == (0, 4)
        assert curve.projection((1, 0)) == (1,)
        assert curve.projection((1, 1)) == (2,)
        assert curve.projection((0, 1)) == (3,)
        assert curve.projection((0.5, 0.5)) == (0.5, 1.5, 2.5, 3.5)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_check_vertices"])
    def test_compare(self):
        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        curvea = PolygonClosedCurve(vertices)
        curveb = PolygonClosedCurve(vertices)
        assert curvea == curvea
        assert curveb == curveb
        assert curvea == curveb
        assert id(curvea) != id(curveb)

        vertices = [(0, 0), (1, 0), (1, 2), (0, 1)]
        curvec = PolygonClosedCurve(vertices)
        assert curvea != curvec
        assert curveb != curvec

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_compare"])
    def test_section(self):
        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        curvea = PolygonClosedCurve(vertices)
        assert curvea.section(0, 4) == curvea

        vertices = [(0.5, 0), (1, 0), (1, 1), (0, 1), (0, 0.5)]
        curveb = PolygonOpenCurve(vertices)
        curvec = curvea.section(0.5, 3.5)
        assert isinstance(curvec, PolygonOpenCurve)
        assert curvec == curveb

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_build"])
    def test_lenght(self):
        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        curve = PolygonClosedCurve(vertices)
        assert curve.lenght == 4

        vertices = [(0, 0), (0, 1), (1, 1), (1, 0)]
        curve = PolygonClosedCurve(vertices)
        assert curve.lenght == 4

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_build"])
    def test_area(self):
        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        curvea = PolygonClosedCurve(vertices)
        assert curvea.area == 1

        vertices = [(0, 0), (0, 1), (1, 1), (1, 0)]
        curvea = PolygonClosedCurve(vertices)
        assert curvea.area == -1

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestClosedCurve::test_area"])
    def test_winding(self):
        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        curve = PolygonClosedCurve(vertices)
        assert curve.winding((0, 0)) == 0.25
        assert curve.winding((1, 0)) == 0.25
        assert curve.winding((1, 1)) == 0.25
        assert curve.winding((0, 1)) == 0.25
        assert curve.winding((0.5, 0)) == 0.5
        assert curve.winding((1, 0.5)) == 0.5
        assert curve.winding((0.5, 1)) == 0.5
        assert curve.winding((0, 0.5)) == 0.5
        assert curve.winding((0.5, 0.5)) == 1
        assert curve.winding((0.5, -1)) == 0

        vertices = [(0, 0), (0, 1), (1, 1), (1, 0)]
        curve = PolygonClosedCurve(vertices)
        assert curve.winding((0, 0)) == 0.75
        assert curve.winding((1, 0)) == 0.75
        assert curve.winding((1, 1)) == 0.75
        assert curve.winding((0, 1)) == 0.75
        assert curve.winding((0.5, 0)) == 0.5
        assert curve.winding((1, 0.5)) == 0.5
        assert curve.winding((0.5, 1)) == 0.5
        assert curve.winding((0, 0.5)) == 0.5
        assert curve.winding((0.5, 0.5)) == 0
        assert curve.winding((0.5, -1)) == 1

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestClosedCurve::test_begin",
            "TestClosedCurve::test_build",
            "TestClosedCurve::test_check_vertices",
            "TestClosedCurve::test_check_vectors",
            "TestClosedCurve::test_evaluate_vertices",
            "TestClosedCurve::test_evaluate_middle",
            "TestClosedCurve::test_evaluate_derivate",
            "TestClosedCurve::test_projection",
            "TestClosedCurve::test_compare",
            "TestClosedCurve::test_section",
            "TestClosedCurve::test_lenght",
            "TestClosedCurve::test_area",
            "TestClosedCurve::test_winding",
        ]
    )
    def test_end(self):
        pass


def test_print():
    vertices = [(0, 0), (1, 0), (1, 1)]
    curve = PolygonOpenCurve(vertices)
    str(curve)
    repr(curve)

    vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
    curve = PolygonClosedCurve(vertices)
    str(curve)
    repr(curve)


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "TestOpenCurve::test_end",
        "TestClosedCurve::test_end",
    ]
)
def test_end():
    pass
