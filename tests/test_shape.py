"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve 
"""

import math

import pytest

from shapepy.curve.polygon import JordanPolygon
from shapepy.primitive import Primitive
from shapepy.shape import SimpleShape


@pytest.mark.order(8)
@pytest.mark.dependency(
    depends=[
        "tests/test_empty_whole.py::test_end",
        "tests/test_point.py::test_end",
        "tests/test_jordan_polygon.py::test_end",
        "tests/test_jordan_curve.py::test_end",
        "tests/test_primitive.py::test_end",
        "tests/test_contains.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestOthers:
    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
        ]
    )
    def test_print(self):
        points = [(0, 0), (1, 0), (0, 1)]
        jordancurve = JordanPolygon(points)
        shape = SimpleShape(jordancurve)
        str(shape)
        repr(shape)

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
        ]
    )
    def test_compare(self):
        shapea = Primitive.regular_polygon(3)
        shapeb = Primitive.regular_polygon(4)
        assert shapea != shapeb
        with pytest.raises(ValueError):
            shapea != 0

    @pytest.mark.order(8)
    @pytest.mark.dependency(
        depends=[
            "TestOthers::test_begin",
            "TestOthers::test_print",
            "TestOthers::test_compare",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(8)
@pytest.mark.dependency(
    depends=[
        "TestIntegrate::test_end",
        "TestOthers::test_end",
    ]
)
def test_end():
    pass
