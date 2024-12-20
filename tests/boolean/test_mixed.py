"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve
"""

import pytest

from shapepy.core import Math
from shapepy.primitive import Primitive


@pytest.mark.order(37)
@pytest.mark.dependency(
    depends=[
        "tests/test_point.py::test_end",
        "tests/test_primitive.py::test_end",
        "tests/test_shape.py::test_end",
        "tests/boolean/test_empty_whole.py::test_end",
        "tests/boolean/test_nobound_intersect.py::test_end",
        "tests/boolean/test_finite_intersect.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(37)
@pytest.mark.dependency(
    depends=[
        "test_begin",
    ]
)
def test_polygon_circle():
    circle = Primitive.circle(radius=2, center=(1, 0))
    square = Primitive.square(side=2, center=(0, 0))
    shape = square | circle

    jordan = shape.jordan
    print(type(jordan))
    for i, (xfunc, yfunc) in enumerate(jordan.functions):
        print(f"x{i} = {xfunc}")
        print(f"y{i} = {yfunc}")
    assert shape.area == 2 + Math.tau

    assert False

@pytest.mark.order(37)
@pytest.mark.dependency(
    depends=[
        "test_polygon_circle",
    ]
)
def test_end():
    pass
