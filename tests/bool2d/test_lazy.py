"""
This module tests when two shapes have common edges/segments
"""

from copy import copy, deepcopy

import pytest

from shapepy.bool2d.base import EmptyShape, WholeShape
from shapepy.bool2d.lazy import LazyAnd, LazyNot, LazyOr, RecipeLazy
from shapepy.bool2d.primitive import Primitive
from shapepy.scalar.angle import degrees


@pytest.mark.order(33)
@pytest.mark.dependency(
    depends=[
        "tests/bool2d/test_primitive.py::test_end",
        "tests/bool2d/test_contains.py::test_end",
        "tests/bool2d/test_empty_whole.py::test_end",
        "tests/bool2d/test_shape.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(33)
@pytest.mark.dependency(depends=["test_begin"])
def test_invert():
    empty = EmptyShape()
    whole = WholeShape()
    square = Primitive.square()
    circle = Primitive.circle()

    assert RecipeLazy.invert(empty) is whole
    assert RecipeLazy.invert(whole) is empty

    for shape in (square, circle):
        invshape = RecipeLazy.invert(shape)
        assert RecipeLazy.invert(invshape) is shape

    LazyNot(empty)
    LazyNot(whole)


@pytest.mark.order(33)
@pytest.mark.dependency(depends=["test_begin", "test_invert"])
def test_unite():
    empty = EmptyShape()
    whole = WholeShape()
    square = Primitive.square()
    circle = Primitive.circle()

    assert RecipeLazy.unite((empty, empty, empty)) is empty
    assert RecipeLazy.unite((whole, whole, whole)) is whole

    for shape in (square, circle):
        assert RecipeLazy.unite((shape, shape, shape)) is shape

    LazyOr((empty, empty))
    LazyOr((empty, whole))
    LazyOr((whole, whole))
    LazyOr((whole, empty))


@pytest.mark.order(33)
@pytest.mark.dependency(depends=["test_begin", "test_invert", "test_unite"])
def test_intersect():
    empty = EmptyShape()
    whole = WholeShape()
    square = Primitive.square()
    circle = Primitive.circle()

    assert RecipeLazy.intersect((empty, empty, empty)) is empty
    assert RecipeLazy.intersect((whole, whole, whole)) is whole

    for shape in (square, circle):
        assert RecipeLazy.intersect((shape, shape, shape)) is shape

    LazyAnd((empty, empty))
    LazyAnd((empty, whole))
    LazyAnd((whole, whole))
    LazyAnd((whole, empty))


@pytest.mark.order(33)
@pytest.mark.dependency(
    depends=["test_begin", "test_invert", "test_unite", "test_intersect"]
)
def test_hash():
    square = Primitive.square()
    circle = Primitive.circle()

    lazyNot = LazyNot(circle)
    assert hash(lazyNot) + hash(circle) == 0

    lazyOr = LazyOr((square, circle))
    assert hash(lazyOr) == hash((square, circle))

    lazyAnd = LazyAnd((square, circle))
    hash(lazyAnd)
    # assert hash(lazyAnd) == -hash((-hash(square), hash(circle)))


@pytest.mark.order(33)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_invert",
        "test_unite",
        "test_intersect",
        "test_hash",
    ]
)
def test_xor():
    empty = EmptyShape()
    whole = WholeShape()
    square = Primitive.square()
    circle = Primitive.circle()

    assert RecipeLazy.xor((empty,)) is empty
    assert RecipeLazy.xor((whole,)) is whole
    assert RecipeLazy.xor((empty, empty)) is empty
    assert RecipeLazy.xor((whole, whole)) is empty
    assert RecipeLazy.xor((empty, empty, empty)) is empty
    assert RecipeLazy.xor((whole, whole, whole)) is whole

    for shape in (square, circle):
        assert RecipeLazy.xor((shape,)) is shape
        assert RecipeLazy.xor((shape, shape)) is empty
        assert RecipeLazy.xor((shape, shape, shape)) is shape
        assert RecipeLazy.xor((shape, shape, shape, shape)) is empty


@pytest.mark.order(33)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_invert",
        "test_unite",
        "test_intersect",
        "test_hash",
        "test_xor",
    ]
)
def test_transformation_move():
    square0 = Primitive.square()
    square1 = Primitive.square(center=(1, 2))
    notsquare0 = RecipeLazy.invert(square0)
    notsquare1 = RecipeLazy.invert(square1)
    assert notsquare0.move((1, 2)) == notsquare1

    square = Primitive.square()
    circle = Primitive.circle()
    lazyNot = LazyNot(square)
    lazyNot.move((3, -4))
    lazyOr = LazyOr((square, circle))
    lazyOr.move((3, -4))
    lazyAnd = LazyAnd((square, circle))
    lazyAnd.move((3, -4))


@pytest.mark.order(33)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_invert",
        "test_unite",
        "test_intersect",
        "test_hash",
        "test_xor",
    ]
)
def test_transformation_scale():
    square0 = Primitive.square(side=1)
    square1 = Primitive.square(side=2)
    notsquare0 = RecipeLazy.invert(square0)
    notsquare1 = RecipeLazy.invert(square1)
    assert notsquare0.scale(2) == notsquare1

    square = Primitive.square()
    circle = Primitive.circle()
    lazyNot = LazyNot(square)
    lazyNot.scale(2)
    lazyOr = LazyOr((square, circle))
    lazyOr.scale(3)
    lazyAnd = LazyAnd((square, circle))
    lazyAnd.scale(2)


@pytest.mark.order(33)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_invert",
        "test_unite",
        "test_intersect",
        "test_hash",
        "test_xor",
    ]
)
def test_transformation_rotate():
    square0 = Primitive.square()
    square1 = Primitive.square()
    notsquare0 = RecipeLazy.invert(square0)
    notsquare1 = RecipeLazy.invert(square1)
    assert notsquare0.rotate(degrees(90)) == notsquare1

    square = Primitive.square()
    circle = Primitive.circle()
    lazyNot = LazyNot(square)
    lazyNot.rotate(degrees(60))
    lazyOr = LazyOr((square, circle))
    lazyOr.rotate(degrees(45))
    lazyAnd = LazyAnd((square, circle))
    lazyAnd.rotate(degrees(30))


@pytest.mark.order(33)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_invert",
        "test_unite",
        "test_intersect",
        "test_hash",
        "test_xor",
        "test_transformation_move",
        "test_transformation_scale",
        "test_transformation_rotate",
    ]
)
def test_printing():
    square = Primitive.square()
    circle = Primitive.circle()

    lazyNot = LazyNot(square)
    str(lazyNot)
    repr(lazyNot)

    lazyOr = LazyOr((square, circle))
    str(lazyOr)
    repr(lazyOr)

    lazyAnd = LazyAnd((square, circle))
    str(lazyAnd)
    repr(lazyAnd)


@pytest.mark.order(33)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_invert",
        "test_unite",
        "test_intersect",
        "test_hash",
        "test_xor",
        "test_transformation_move",
        "test_transformation_scale",
        "test_transformation_rotate",
        "test_printing",
    ]
)
def test_copy():
    square = Primitive.square()
    circle = Primitive.circle()

    lazyNot = LazyNot(square)
    copyLazyNot = copy(lazyNot)
    assert copyLazyNot == lazyNot
    assert id(copyLazyNot) != id(lazyNot)
    assert id(~copyLazyNot) == id(~lazyNot)
    deepLazyNot = deepcopy(lazyNot)
    assert deepLazyNot == lazyNot
    assert id(deepLazyNot) != id(lazyNot)
    assert ~deepLazyNot == ~lazyNot
    assert id(~deepLazyNot) != id(~lazyNot)

    lazyOr = LazyOr((square, circle))
    copyLazyOr = copy(lazyOr)
    assert copyLazyOr == lazyOr
    assert id(copyLazyOr) != id(lazyOr)
    deepLazyOr = deepcopy(lazyOr)
    assert deepLazyOr == lazyOr
    assert id(deepLazyOr) != id(lazyOr)

    lazyAnd = LazyAnd((square, circle))
    copyLazyAnd = copy(lazyAnd)
    assert copyLazyAnd == lazyAnd
    assert id(copyLazyAnd) != id(lazyAnd)
    deepLazyAnd = deepcopy(lazyAnd)
    assert deepLazyAnd == lazyAnd
    assert id(deepLazyAnd) != id(lazyAnd)


@pytest.mark.order(33)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_invert",
        "test_unite",
        "test_intersect",
        "test_hash",
        "test_xor",
        "test_transformation_move",
        "test_transformation_scale",
        "test_transformation_rotate",
        "test_printing",
    ]
)
def test_clean():
    square = Primitive.square(center=(-3, 0))
    circle = Primitive.circle(center=(3, 0))

    lazyNot = LazyNot(square)
    assert lazyNot.clean() == (-square).clean()

    lazyOr = LazyOr((square, circle))
    assert lazyOr.clean() == square + circle

    lazyAnd = LazyOr((square, circle))
    assert lazyAnd.clean() == square * circle


@pytest.mark.order(33)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_invert",
        "test_unite",
        "test_intersect",
        "test_xor",
        "test_transformation_move",
        "test_transformation_scale",
        "test_transformation_rotate",
        "test_printing",
        "test_hash",
        "test_copy",
    ]
)
def test_all():
    pass
