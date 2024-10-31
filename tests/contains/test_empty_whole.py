"""
This file contains the code to test the relative position of an object with respect
to another
"""

import pytest

from shapepy.core import Empty, Whole
from shapepy.curve.polygon import JordanPolygon
from shapepy.primitive import Primitive
from shapepy.shape import ConnectedShape, DisjointShape


@pytest.mark.order(20)
@pytest.mark.dependency(
    depends=[
        "tests/test_empty_whole.py::test_end",
        "tests/test_point.py::test_end",
        "tests/test_primitive.py::test_end",
        "tests/test_shape.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(20)
@pytest.mark.dependency(depends=["test_begin"])
def test_empty():
    empty = Empty()
    whole = Whole()
    assert empty in empty
    assert empty in whole


@pytest.mark.order(20)
@pytest.mark.dependency(
    depends=[
        "test_begin",
    ]
)
def test_whole():
    empty = Empty()
    whole = Whole()
    assert whole not in empty
    assert whole in whole


@pytest.mark.order(20)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
    ]
)
def test_point():
    empty = Empty()
    whole = Whole()
    for point in [(0, 0), (1, 1), (0, -1)]:
        assert point not in empty
        assert point in whole


@pytest.mark.order(20)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_point",
    ]
)
def test_jordan():
    empty = Empty()
    whole = Whole()

    vertices = [(0, 0), (1, 0), (0, 1)]
    jordan = JordanPolygon(vertices)
    assert jordan not in empty
    assert jordan in whole

    vertices = [(0, 0), (0, 1), (1, 0)]
    jordan = JordanPolygon(vertices)
    assert jordan not in empty
    assert jordan in whole


@pytest.mark.order(20)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_point",
        "test_jordan",
    ]
)
def test_simple_shape():
    empty = Empty()
    whole = Whole()

    shape = Primitive.triangle()
    assert shape not in empty
    assert shape in whole


@pytest.mark.order(20)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_simple_shape",
    ]
)
def test_connected_shape():
    empty = Empty()
    whole = Whole()

    big_square = Primitive.square(side=2)
    small_square = Primitive.square(side=1)
    shape = ConnectedShape([big_square, ~small_square])
    assert shape not in empty
    assert shape in whole


@pytest.mark.order(20)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_simple_shape",
        "test_connected_shape",
    ]
)
def test_disjoint_shape():
    empty = Empty()
    whole = Whole()

    square0 = Primitive.square(center=(-3, 0))
    square1 = Primitive.square(center=(3, 0))
    shape = DisjointShape([square0, square1])
    assert shape not in empty
    assert shape in whole


@pytest.mark.order(20)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_point",
        "test_jordan",
        "test_simple_shape",
        "test_connected_shape",
        "test_disjoint_shape",
    ]
)
def test_end():
    pass
