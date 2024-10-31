from fractions import Fraction

import numpy as np
import pytest

from shapepy import ConnectedShape, Empty, Primitive, Whole


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "tests/contains/test_empty_whole.py::test_end",
        "tests/contains/test_curve.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(22)
@pytest.mark.dependency(depends=["test_begin"])
def test_empty():
    empty = Empty()
    square = Primitive.square()
    assert empty in square
    assert square not in empty


@pytest.mark.order(22)
@pytest.mark.dependency(depends=["test_begin"])
def test_whole():
    whole = Whole()
    square = Primitive.square()
    assert whole not in square
    assert square in whole


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
    ]
)
def test_keep_ids():
    square = Primitive.square(side=4)
    jordan = square.jordan
    good_ids = tuple(id(vertex) for vertex in jordan.vertices)

    for k in range(100):  # number of tests
        point = np.random.uniform(-4, 4, 2)
        point in square
        jordan = square.jordan
        test_ids = tuple(id(vertex) for vertex in jordan.vertices)
        assert len(test_ids) == len(good_ids)
        assert test_ids == good_ids


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_keep_ids",
    ]
)
def test_keep_type():
    square = Primitive.square(side=4)
    good_types = []
    jordan = square.jordan
    for vertex in jordan.vertices:
        good_types.append((type(vertex[0]), type(vertex[0])))
    one = Fraction(1)
    for point in [(0, 0), (1, 2), (one / 2, -one / 2), (1.2, 3.5)]:
        point in square
        test_types = []
        jordan = square.jordan
        for vertex in jordan.vertices:
            test_types.append((type(vertex[0]), type(vertex[0])))
        assert len(test_types) == len(good_types)
        assert test_types == good_types


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_keep_ids",
        "test_keep_type",
    ]
)
def test_point():
    square = Primitive.square(side=4)

    # Interior points
    assert (0, 0) in square
    assert (-1, -1) in square
    assert (-1, 1) in square
    assert (1, -1) in square
    assert (1, 1) in square

    # Boundary points
    assert (-2, -2) in square
    assert (0, -2) in square
    assert (2, -2) in square
    assert (2, 0) in square
    assert (2, 2) in square
    assert (0, 2) in square
    assert (-2, 2) in square
    assert (-2, 0) in square

    # Exterior points
    assert (3, 3) not in square
    assert (-3, -3) not in square


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_keep_ids",
        "test_keep_type",
        "test_point",
    ]
)
def test_jordan():
    small_square = Primitive.square(side=2)
    big_square = Primitive.square(side=4)

    assert small_square.jordan in small_square
    assert small_square.jordan in big_square
    assert big_square.jordan not in small_square
    assert big_square.jordan in big_square

    assert ~(small_square.jordan) in small_square
    assert ~(small_square.jordan) in big_square
    assert ~(big_square.jordan) not in small_square
    assert ~(big_square.jordan) in big_square

    assert small_square.jordan not in (~small_square)
    assert small_square.jordan not in (~big_square)
    assert big_square.jordan in (~small_square)
    assert big_square.jordan not in (~big_square)

    assert ~(small_square.jordan) not in (~small_square)
    assert ~(small_square.jordan) not in (~big_square)
    assert ~(big_square.jordan) in (~small_square)
    assert ~(big_square.jordan) not in (~big_square)


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_keep_ids",
        "test_keep_type",
        "test_point",
        "test_jordan",
    ]
)
def test_simple():
    # Centered squares
    big_square = Primitive.square(side=4)
    small_square = Primitive.square(side=2)
    assert small_square in big_square
    assert big_square not in small_square
    assert (~small_square) not in big_square
    assert (~big_square) not in small_square
    assert small_square not in (~big_square)
    assert big_square not in (~small_square)
    assert (~small_square) not in (~big_square)
    assert (~big_square) in (~small_square)

    # Disjoint squares
    left = Primitive.square(side=2, center=(-3, 0))
    right = Primitive.square(side=2, center=(3, 0))
    assert left not in right
    assert right not in left
    assert (~left) not in right
    assert (~right) not in left
    assert left in (~right)
    assert right in (~left)
    assert (~left) not in (~right)
    assert (~right) not in (~left)


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_point",
        "test_jordan",
        "test_simple",
    ]
)
def test_connected():
    # centered squares
    big_square = Primitive.square(side=4)
    small_square = Primitive.square(side=2)
    connected = ConnectedShape([big_square, ~small_square])

    assert connected not in small_square
    assert connected in big_square
    assert connected in (~small_square)
    assert connected not in (~big_square)


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_point",
        "test_jordan",
        "test_simple",
        "test_connected",
    ]
)
def test_disjoint():
    square_left = Primitive.square(side=2, center=(-3, 0))
    square_right = Primitive.square(side=2, center=(3, 0))
    disj_shape = DisjointShape([square_left, square_right])

    square = Primitive.square(side=1, center=(-3, 0))
    assert square in square_left
    assert square not in square_right
    # assert square in disj_shape
    assert disj_shape not in square

    square = Primitive.square(side=1, center=(3, 0))
    assert square not in square_left
    assert square in square_right
    # assert square in disj_shape
    assert disj_shape not in square

    square = Primitive.square(side=9, center=(0, 0))
    assert disj_shape in square
    square = Primitive.square(side=8, center=(0, 0))
    assert disj_shape in square  # touchs boundary
    square = Primitive.square(side=7, center=(0, 0))
    assert disj_shape not in square


@pytest.mark.order(22)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_point",
        "test_jordan",
        "test_simple",
        "test_connected",
        "test_disjoint",
    ]
)
def test_end():
    pass
