import pytest

from shapepy import DisjointShape, Empty, Primitive, Whole


@pytest.mark.order(24)
@pytest.mark.dependency(
    depends=[
        "tests/contains/test_disjoint.py::test_end",
    ]
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
