import pytest

from shapepy.analytic.elementar import linear_piecewise
from shapepy.bool2d.base import EmptyR2, WholeR2
from shapepy.bool2d.bool2d import contains, intersect, invert, unite
from shapepy.bool2d.container import expand
from shapepy.bool2d.simplify import simplify
from shapepy.bool2d.singles import PointR2, ShapeR2
from shapepy.geometry import JordanCurve


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/bool2d/test_build.py::test_empty",
        "tests/bool2d/test_build.py::test_whole",
    ],
    scope="session",
)
def test_singleton():
    empty = EmptyR2()
    whole = WholeR2()

    assert empty in empty
    assert empty in whole
    assert whole not in empty
    assert whole in whole

    assert contains(empty, empty)
    assert contains(whole, empty)
    assert not contains(empty, whole)
    assert contains(whole, whole)


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/bool2d/test_build.py::test_point",
        "tests/bool2d/test_contains.py::test_singleton",
    ],
    scope="session",
)
def test_single_point():
    empty = EmptyR2()
    whole = WholeR2()

    for point in [(0, 0), (10, -10), (-7, 3)]:
        singl = PointR2(point)
        inver = ~singl

        assert empty in singl
        assert empty in inver
        assert whole not in singl
        assert whole not in inver

        assert singl not in empty
        assert inver not in empty
        assert point not in empty
        assert singl in whole
        assert inver in whole
        assert point in whole

        assert singl in singl
        assert inver not in singl
        assert point in singl
        assert singl not in inver
        assert inver in inver
        assert point not in inver

        assert contains(singl, empty)
        assert contains(inver, empty)
        assert contains(point, empty)
        assert not contains(singl, whole)
        assert not contains(inver, whole)
        assert not contains(point, whole)

        assert not contains(empty, singl)
        assert not contains(empty, inver)
        assert not contains(empty, point)
        assert contains(whole, singl)
        assert contains(whole, inver)
        assert contains(whole, point)

        assert contains(singl, singl)
        assert not contains(singl, inver)
        assert contains(singl, point)
        assert not contains(inver, singl)
        assert contains(inver, inver)
        assert not contains(inver, point)
        assert contains(point, singl)
        assert not contains(point, inver)
        assert contains(point, point)


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/bool2d/test_build.py::test_point",
        "tests/bool2d/test_contains.py::test_singleton",
    ],
    scope="session",
)
def test_shape():
    empty = EmptyR2()
    whole = WholeR2()

    xanaly = linear_piecewise((-1, 1, 1, -1, -1))
    yanaly = linear_piecewise((-1, -1, 1, 1, -1))
    jordan = JordanCurve(xanaly, yanaly)

    shape = ShapeR2(jordan, True)
    # Singletons
    assert empty in shape
    assert whole not in shape
    assert shape not in empty
    assert shape in whole
    assert contains(shape, empty)
    assert not contains(shape, whole)
    assert not contains(empty, shape)
    assert contains(whole, shape)
    # Interior points
    assert (0, 0) in shape
    assert (0.5, 0.5) in shape
    # Exterior points
    assert (-2, -2) in shape
    assert (2, -2) in shape
    # Corner points
    assert (-1, -1) in shape
    assert (-1, 1) in shape
    assert (1, -1) in shape
    assert (1, 1) in shape
    # Edge points
    assert (0, -1) in shape
    assert (0, 1) in shape
    assert (1, 0) in shape
    assert (-1, 0) in shape

    shape = ShapeR2(jordan, False)
    # Singletons
    assert empty in shape
    assert whole not in shape
    assert shape not in empty
    assert shape in whole
    assert contains(shape, empty)
    assert not contains(shape, whole)
    assert not contains(empty, shape)
    assert contains(whole, shape)
    # Interior points
    assert (0, 0) in shape
    assert (0.5, 0.5) in shape
    # Exterior points
    assert (-2, -2) in shape
    assert (2, -2) in shape
    # Corner points
    assert (-1, -1) not in shape
    assert (-1, 1) not in shape
    assert (1, -1) not in shape
    assert (1, 1) not in shape
    # Edge points
    assert (0, -1) not in shape
    assert (0, 1) not in shape
    assert (1, 0) not in shape
    assert (-1, 0) not in shape


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_singleton",
        "test_single_point",
        "test_shape",
    ]
)
def test_all():
    pass
