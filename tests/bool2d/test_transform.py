"""File to test the functions `move`, `scale` and `rotate`"""

import pytest

from shapepy.bool2d.primitive import Primitive
from shapepy.bool2d.shape import ConnectedShape, DisjointShape
from shapepy.geometry.box import Box
from shapepy.scalar.angle import degrees


@pytest.mark.order(24)
@pytest.mark.dependency(
    depends=[
        "tests/bool2d/test_primitive.py::test_end",
        "tests/bool2d/test_contains.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(24)
@pytest.mark.dependency(depends=["test_begin"])
def test_move_simple():
    square = Primitive.square(2)
    assert square.box() == Box((-1, -1), (1, 1))

    square = square.move((1, 1))
    assert square.box() == Box((0, 0), (2, 2))


@pytest.mark.order(24)
@pytest.mark.dependency(depends=["test_begin"])
def test_scale_simple():
    square = Primitive.square(2)
    assert square.box() == Box((-1, -1), (1, 1))

    square = square.scale((3, 4))
    assert square.box() == Box((-3, -4), (3, 4))


@pytest.mark.order(24)
@pytest.mark.dependency(depends=["test_begin"])
def test_rotate_simple():
    square = Primitive.square(2)
    assert square.box() == Box((-1, -1), (1, 1))

    angle = degrees(90)
    square = square.rotate(angle)
    assert square.box() == Box((-1, -1), (1, 1))


@pytest.mark.order(24)
@pytest.mark.dependency(depends=["test_move_simple"])
def test_move_connected():
    small_square = Primitive.square(2)
    big_square = Primitive.square(4)
    connected = ConnectedShape([big_square, -small_square])
    assert connected.box() == Box((-2, -2), (2, 2))

    connected = connected.move((2, 2))
    assert connected.box() == Box((0, 0), (4, 4))


@pytest.mark.order(24)
@pytest.mark.dependency(depends=["test_scale_simple"])
def test_scale_connected():
    small_square = Primitive.square(2)
    big_square = Primitive.square(4)
    connected = ConnectedShape([big_square, -small_square])
    assert connected.box() == Box((-2, -2), (2, 2))

    connected = connected.scale((3, 4))
    assert connected.box() == Box((-6, -8), (6, 8))


@pytest.mark.order(24)
@pytest.mark.dependency(depends=["test_rotate_simple"])
def test_rotate_connected():
    small_square = Primitive.square(2)
    big_square = Primitive.square(4)
    connected = ConnectedShape([big_square, -small_square])
    assert connected.box() == Box((-2, -2), (2, 2))

    angle = degrees(90)
    connected = connected.rotate(angle)
    assert connected.box() == Box((-2, -2), (2, 2))


@pytest.mark.order(24)
@pytest.mark.dependency(depends=["test_move_simple"])
def test_move_disjoint():
    left_square = Primitive.square(2, (-2, 0))
    right_square = Primitive.square(2, (2, 0))
    disjoint = DisjointShape([left_square, right_square])
    assert disjoint.box() == Box((-3, -1), (3, 1))

    disjoint = disjoint.move((2, 2))
    assert disjoint.box() == Box((-1, 1), (5, 3))


@pytest.mark.order(24)
@pytest.mark.dependency(depends=["test_scale_simple"])
def test_scale_disjoint():
    left_square = Primitive.square(2, (-2, 0))
    right_square = Primitive.square(2, (2, 0))
    disjoint = DisjointShape([left_square, right_square])
    assert disjoint.box() == Box((-3, -1), (3, 1))

    disjoint = disjoint.scale((3, 4))
    assert disjoint.box() == Box((-9, -4), (9, 4))


@pytest.mark.order(24)
@pytest.mark.dependency(depends=["test_rotate_simple"])
def test_rotate_disjoint():
    left_square = Primitive.square(2, (-2, 0))
    right_square = Primitive.square(2, (2, 0))
    disjoint = DisjointShape([left_square, right_square])
    assert disjoint.box() == Box((-3, -1), (3, 1))

    angle = degrees(90)
    disjoint = disjoint.rotate(angle)
    assert disjoint.box() == Box((-1, -3), (1, 3))


@pytest.mark.order(24)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_move_simple",
        "test_scale_simple",
        "test_rotate_simple",
        "test_move_connected",
        "test_scale_connected",
        "test_rotate_connected",
        "test_move_disjoint",
        "test_scale_disjoint",
        "test_rotate_disjoint",
    ]
)
def test_end():
    pass
