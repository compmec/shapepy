import pytest

from shapepy.geometry import BoxCage


@pytest.mark.order(32)
@pytest.mark.timeout(10)
@pytest.mark.dependency(
    depends=[
        "tests/geometry/test_point.py::test_all",
    ],
    scope="session",
)
def test_build():
    BoxCage((0, 0), (1, 1))


@pytest.mark.order(32)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_build"])
def test_winding():
    box = BoxCage((-1, -1), (1, 1))
    # Points at vertex of the box
    for vertex in [(-1, -1), (-1, 1), (1, 1), (1, -1)]:
        assert box.winding(vertex) == 0.25
    # Ponts on the edge of the box
    for point in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        assert box.winding(point) == 0.5
    # Points that are completly inside
    for point in [(0, 0)]:
        assert box.winding(point) == 1
    # Points that are completly outside
    for point in [(2, 2)]:
        assert box.winding(point) == 0


@pytest.mark.order(32)
@pytest.mark.timeout(10)
@pytest.mark.dependency(depends=["test_build", "test_winding"])
def test_contains():
    box = BoxCage((-1, -1), (1, 1))
    # Points at vertex of the box
    for vertex in [(-1, -1), (-1, 1), (1, 1), (1, -1)]:
        assert vertex in box
    # Ponts on the edge of the box
    for point in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        assert point in box
    # Points that are completly inside
    for point in [(0, 0)]:
        assert point in box
    # Points that are completly outside
    for point in [(2, 2)]:
        assert point not in box


@pytest.mark.order(32)
@pytest.mark.dependency(
    depends=[
        "test_build",
        "test_winding",
        "test_contains",
    ]
)
def test_all():
    pass
