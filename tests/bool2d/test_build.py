import pytest

from shapepy.analytic.elementar import linear_piecewise
from shapepy.bool2d.base import EmptyR2, SubSetR2, WholeR2
from shapepy.bool2d.container import recipe_and, recipe_not, recipe_or
from shapepy.bool2d.singles import CurveR2, PointR2, ShapeR2
from shapepy.geometry import ContinuousCurve, JordanCurve


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

    PointR2((0, 0))
    PointR2((1, 1))


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["tests/geometry/test_curve.py::test_all"],
    scope="session",
)
def test_curve():
    # Create a square
    xfunc = linear_piecewise((-1, 1, 1, -1, -1))
    yfunc = linear_piecewise((-1, -1, 1, 1, -1))
    curve = ContinuousCurve(xfunc, yfunc)
    CurveR2(curve)
    curve = JordanCurve(xfunc, yfunc)
    CurveR2(curve)


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["tests/geometry/test_curve.py::test_all"],
    scope="session",
)
def test_shape():
    # Create a square
    xfunc = linear_piecewise((-1, 1, 1, -1, -1))
    yfunc = linear_piecewise((-1, -1, 1, 1, -1))
    curve = JordanCurve(xfunc, yfunc)
    ShapeR2(curve, True)
    ShapeR2(curve, False)


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
    point = PointR2((0, 0))
    recipe_not(point)


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
    pointa = PointR2((0, 0))
    pointb = PointR2((10, 10))
    recipe_and((pointa, pointb))


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
    pointa = PointR2((0, 0))
    pointb = PointR2((10, 10))
    recipe_or((pointa, pointb))


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
    hash(PointR2((10, 0)))


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
