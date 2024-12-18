import pytest

from shapepy import DisjointShape, Empty, Primitive, Whole


@pytest.mark.order(24)
@pytest.mark.dependency(
    depends=[
        "tests/contains/test_connected.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(24)
@pytest.mark.dependency(depends=["test_begin"])
def test_empty():
    empty = Empty()
    squarea = Primitive.square(center=(-3, 0))
    squareb = Primitive.square(center=(3, 0))
    disj_shape = DisjointShape([squarea, squareb])

    assert empty in disj_shape
    assert disj_shape not in empty


@pytest.mark.order(24)
@pytest.mark.dependency(depends=["test_begin"])
def test_whole():
    whole = Whole()
    squarea = Primitive.square(center=(-3, 0))
    squareb = Primitive.square(center=(3, 0))
    disj_shape = DisjointShape([squarea, squareb])

    assert whole not in disj_shape
    assert disj_shape in whole


@pytest.mark.order(24)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
    ]
)
def test_winding():
    squarea = Primitive.square(side=2, center=(-3, 0))
    squareb = Primitive.square(side=2, center=(3, 0))
    disj_shape = DisjointShape([squarea, squareb])

    assert disj_shape.winding((-3, 0)) == 1
    assert disj_shape.winding((3, 0)) == 1
    midpts = [
        (-4, 0),
        (-2, 0),
        (-3, 1),
        (-3, -1),
        (2, 0),
        (4, 0),
        (3, 1),
        (3, -1),
    ]
    for point in midpts:
        assert disj_shape.winding(point) == 0.5
    corpts = [
        (-4, -1),
        (-4, 1),
        (-2, -1),
        (-2, 1),
        (2, -1),
        (2, 1),
        (4, -1),
        (4, 1),
    ]
    for point in corpts:
        assert disj_shape.winding(point) == 0.25

    squarea = Primitive.square(side=2, center=(-1, -1))
    squareb = Primitive.square(side=2, center=(1, 1))
    disj_shape = DisjointShape([squarea, squareb])
    assert disj_shape.winding((-1, -1)) == 1
    assert disj_shape.winding((1, 1)) == 1
    assert disj_shape.winding((0, 0)) == 0.5


@pytest.mark.order(24)
@pytest.mark.dependency(depends=["test_winding"])
def test_point():
    squarea = Primitive.square(center=(-3, 0))
    squareb = Primitive.square(center=(3, 0))
    disj_shape = DisjointShape([squarea, squareb])

    assert (-3, 0) in squarea
    assert (3, 0) in squareb
    assert (-3, 0) in disj_shape
    assert (3, 0) in disj_shape


@pytest.mark.order(24)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_point",
    ]
)
def test_jordan():
    pass


@pytest.mark.order(24)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_point",
        "test_jordan",
    ]
)
def test_simple():
    square_left = Primitive.square(side=2, center=(-3, 0))
    square_right = Primitive.square(side=2, center=(3, 0))
    disj_shape = DisjointShape([square_left, square_right])

    square = Primitive.square(side=1, center=(-3, 0))
    assert square in square_left
    assert square not in square_right
    assert square in disj_shape
    assert disj_shape not in square

    square = Primitive.square(side=1, center=(3, 0))
    assert square not in square_left
    assert square in square_right
    assert square in disj_shape
    assert disj_shape not in square

    square = Primitive.square(side=9, center=(0, 0))
    assert disj_shape in square
    square = Primitive.square(side=8, center=(0, 0))
    assert disj_shape in square  # touchs boundary
    square = Primitive.square(side=7, center=(0, 0))
    assert disj_shape not in square


@pytest.mark.order(24)
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
    pass


@pytest.mark.order(24)
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
    pass


@pytest.mark.order(24)
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
