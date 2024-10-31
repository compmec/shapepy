import pytest

from shapepy.curve.polygon import JordanPolygon


@pytest.mark.order(21)
@pytest.mark.dependency(
    depends=[
        "tests/test_empty_whole.py::test_end",
        "tests/test_point.py::test_end",
        "tests/test_primitive.py::test_end",
        "tests/test_shape.py::test_end",
        "tests/contains/test_empty_whole.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(21)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "test_begin",
    ]
)
def test_boundary_point():
    # Test if the points are in boundary
    vertices = [(0, 0), (1, 0), (0, 1)]
    triangle = JordanPolygon(vertices)
    assert (0, 0) in triangle
    assert (1, 0) in triangle
    assert (0, 1) in triangle
    assert (0.5, 0) in triangle
    assert (0.5, 0.5) in triangle
    assert (0, 0.5) in triangle

    vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
    square = JordanPolygon(vertices)
    assert (0, 0) in square
    assert (1, 0) in square
    assert (1, 1) in square
    assert (0, 1) in square
    assert (0.5, 0) in square
    assert (1, 0.5) in square
    assert (0.5, 1) in square
    assert (0, 0.5) in square


@pytest.mark.order(21)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "test_begin",
    ]
)
def test_interior_point():
    # Test if the interior points are not in boundary
    vertices = [(0, 0), (3, 0), (0, 3)]
    triangle = JordanPolygon(vertices)
    assert (1, 1) not in triangle

    vertices = [(0, 0), (2, 0), (2, 2), (0, 2)]
    square = JordanPolygon(vertices)
    assert (1, 1) not in square


@pytest.mark.order(21)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "test_begin",
    ]
)
def test_exterior_point():
    # Test if the exterior points are not in boundary
    triangle = JordanPolygon([(0, 0), (1, 0), (0, 1)])
    assert (-1, -1) not in triangle
    assert (1, 1) not in triangle

    square = JordanPolygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert (-1, -1) not in square
    assert (2, 2) not in square


@pytest.mark.order(21)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_boundary_point",
        "test_interior_point",
        "test_exterior_point",
    ]
)
def test_end():
    pass
