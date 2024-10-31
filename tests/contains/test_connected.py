import pytest

from shapepy import ConnectedShape, Empty, Primitive, Whole


@pytest.mark.order(23)
@pytest.mark.dependency(
    depends=[
        "tests/contains/test_simple.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(23)
@pytest.mark.dependency(depends=["test_begin"])
def test_empty():
    empty = Empty()
    square = ~Primitive.square()
    assert empty in square
    assert square not in empty


@pytest.mark.order(23)
@pytest.mark.dependency(depends=["test_begin"])
def test_whole():
    whole = Whole()
    square = ~Primitive.square()
    assert whole not in square
    assert square in whole


@pytest.mark.order(23)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
    ]
)
def test_point():
    big_square = Primitive.square(side=4)
    small_square = Primitive.square(side=2)
    connected = ConnectedShape([big_square, ~small_square])

    # Exterior points
    assert (0, 0) not in connected

    # Boundary points
    assert (-1, -1) not in connected
    assert (-1, 1) not in connected
    assert (1, -1) not in connected
    assert (1, 1) not in connected
    assert (-2, -2) in connected
    assert (0, -2) in connected
    assert (2, -2) in connected
    assert (2, 0) in connected
    assert (2, 2) in connected
    assert (0, 2) in connected
    assert (-2, 2) in connected
    assert (-2, 0) in connected

    # Interior points
    assert (1.5, 1.5) in connected
    assert (1.5, -1.5) in connected


@pytest.mark.order(23)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_empty",
        "test_whole",
        "test_point",
    ]
)
def test_jordan():
    small_square = Primitive.square(side=2)
    small_jordan = small_square.jordan
    big_square = Primitive.square(side=4)
    big_jordan = big_square.jordan
    connected = ConnectedShape([big_square, ~small_square])

    assert small_jordan not in connected
    assert big_jordan in connected

    assert (~small_jordan) not in connected
    assert (~big_jordan) in connected


@pytest.mark.order(23)
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
    small_square = Primitive.square(side=2)
    big_square = Primitive.square(side=4)
    connected = ConnectedShape([big_square, ~small_square])

    assert small_square not in connected
    assert big_square not in connected
    assert (~small_square) not in connected
    assert (~big_square) not in connected


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


@pytest.mark.order(23)
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
    small_square = Primitive.square(side=2)
    big_square = Primitive.square(side=4)
    connected = ConnectedShape([big_square, ~small_square])

    assert (~small_square) in (~small_square)
    assert (~big_square) in (~small_square)
    assert (~small_square) not in (~big_square)
    assert (~big_square) in (~big_square)


@pytest.mark.order(23)
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


@pytest.mark.order(23)
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
