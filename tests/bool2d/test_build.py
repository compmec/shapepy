import pytest

from shapepy.bool2d.base import EmptyR2, SubSetR2, WholeR2
from shapepy.bool2d.singles import PointR2


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_empty():
    empty = EmptyR2()
    assert isinstance(empty, SubSetR2)


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_whole():
    whole = WholeR2()
    assert isinstance(whole, SubSetR2)


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["tests/geometry/test_point.py::test_all"],
    scope="session",
)
def test_point():
    point = PointR2((10, 1))
    assert isinstance(point, SubSetR2)


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["tests/geometry/test_curve.py::test_all"],
    scope="session",
)
def test_curve():
    pass


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["tests/geometry/test_curve.py::test_all"],
    scope="session",
)
def test_shape():
    pass


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_empty",
        "test_whole",
        "test_point",
        "test_curve",
        "test_shape",
    ]
)
def test_container_not():
    pass


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_empty",
        "test_whole",
        "test_point",
        "test_curve",
        "test_shape",
    ]
)
def test_container_and():
    pass


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_empty",
        "test_whole",
        "test_point",
        "test_curve",
        "test_shape",
    ]
)
def test_container_or():
    pass


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_empty",
        "test_whole",
        "test_point",
        "test_curve",
        "test_shape",
        "test_container_not",
        "test_container_and",
        "test_container_or",
    ]
)
def test_hash():
    assert hash(EmptyR2()) == 0
    assert hash(WholeR2()) == 1
    hash(PointR2)


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_empty",
        "test_whole",
        "test_point",
        "test_curve",
        "test_shape",
        "test_container_not",
        "test_container_and",
        "test_container_or",
        "test_hash",
    ]
)
def test_all():
    pass
