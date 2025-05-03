import pytest

from shapepy.bool2d.base import EmptyR2, WholeR2
from shapepy.bool2d.bool2d import intersect, invert, unite
from shapepy.bool2d.singles import PointR2


class TestStr:

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_empty_whole.py::test_all",
        ],
        scope="session",
    )
    def test_empty(self):
        empty = EmptyR2()
        assert str(empty) == "EmptyR2"

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_empty_whole.py::test_all",
        ],
        scope="session",
    )
    def test_whole(self):
        whole = WholeR2()
        assert str(whole) == "WholeR2"

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_single_point.py::test_all",
        ],
        scope="session",
    )
    def test_single_point(self):
        point = PointR2((-1, 1))
        assert str(point) == "{(-1, 1)}"

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_single_point.py::test_all",
        ],
        scope="session",
    )
    def test_not_point(self):
        point = ~PointR2((-1, 1))
        assert str(point) == "NOT[{(-1, 1)}]"

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_single_point.py::test_all",
        ],
        scope="session",
    )
    def test_or_point(self):
        points = [(-1, -1), (1, 1)]
        subset = unite(*map(PointR2, points))
        assert str(subset) == "OR[{(1, 1)}, {(-1, -1)}]"

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_single_point.py::test_all",
        ],
        scope="session",
    )
    def test_and_not_point(self):
        points = [(-1, -1), (1, 1)]
        subset = intersect(*map(invert, map(PointR2, points)))
        assert str(subset) == "AND[NOT[{(-1, -1)}], NOT[{(1, 1)}]]"


class TestRepr:

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_empty_whole.py::test_all",
        ],
        scope="session",
    )
    def test_empty(self):
        empty = EmptyR2()
        assert repr(empty) == "EmptyR2"

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_empty_whole.py::test_all",
        ],
        scope="session",
    )
    def test_whole(self):
        whole = WholeR2()
        assert repr(whole) == "WholeR2"

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_single_point.py::test_all",
        ],
        scope="session",
    )
    def test_single_point(self):
        point = PointR2((-1, 1))
        assert repr(point) == "PointR2((-1, 1))"

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_single_point.py::test_all",
        ],
        scope="session",
    )
    def test_not_point(self):
        point = ~PointR2((-1, 1))
        assert repr(point) == "NOT[PointR2((-1, 1))]"

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_single_point.py::test_all",
        ],
        scope="session",
    )
    def test_or_point(self):
        points = [(-1, -1), (1, 1)]
        subset = unite(*map(PointR2, points))
        good = "OR[PointR2((1, 1)), PointR2((-1, -1))]"
        assert repr(subset) == good

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_single_point.py::test_all",
        ],
        scope="session",
    )
    def test_and_not_point(self):
        points = [(-1, -1), (1, 1)]
        subset = intersect(*map(invert, map(PointR2, points)))
        good = "AND[NOT[PointR2((-1, -1))], NOT[PointR2((1, 1))]]"
        assert repr(subset) == good


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "TestStr::test_empty",
        "TestStr::test_whole",
        "TestStr::test_single_point",
        "TestStr::test_not_point",
        "TestStr::test_or_point",
        "TestStr::test_and_not_point",
        "TestRepr::test_empty",
        "TestRepr::test_whole",
        "TestRepr::test_single_point",
        "TestRepr::test_not_point",
        "TestRepr::test_or_point",
        "TestRepr::test_and_not_point",
    ]
)
def test_all():
    pass
