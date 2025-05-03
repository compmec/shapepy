import pytest

from shapepy.angle import Angle
from shapepy.bool2d.base import EmptyR2, WholeR2
from shapepy.bool2d.bool2d import intersect, invert, unite
from shapepy.bool2d.singles import SinglePointR2
from shapepy.bool2d.transform import move, rotate, scale


class TestEmpty:

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_empty_whole.py::test_all",
        ],
        scope="session",
    )
    def test_begin(self):
        pass

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestEmpty::test_begin"])
    def test_move(self):
        empty = EmptyR2()

        for vector in [(0, 0), (10, 0), (3, -5)]:
            assert empty.move(vector) == empty
            assert move(empty, vector) == empty

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestEmpty::test_begin"])
    def test_scale(self):
        empty = EmptyR2()

        for amount in [1, 2, 3, (1, 1), (10, 3), (3, 5)]:
            assert empty.scale(amount) == empty
            assert scale(empty, amount) == empty

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestEmpty::test_begin"])
    def test_rotate(self):
        empty = EmptyR2()

        angles = [Angle.degrees(0), Angle.degrees(45), Angle.degrees(90)]
        for angle in angles:
            assert empty.rotate(angle) == empty
            assert rotate(empty, angle) == empty


class TestWhole:

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_empty_whole.py::test_all",
        ],
        scope="session",
    )
    def test_begin(self):
        pass

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestWhole::test_begin"])
    def test_move(self):
        whole = WholeR2()

        for vector in [(0, 0), (10, 0), (3, -5)]:
            assert whole.move(vector) == whole
            assert move(whole, vector) == whole

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestWhole::test_begin"])
    def test_scale(self):
        whole = WholeR2()

        for amount in [1, 2, 3, (1, 1), (10, 3), (3, 5)]:
            assert whole.scale(amount) == whole
            assert scale(whole, amount) == whole

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestWhole::test_begin"])
    def test_rotate(self):
        whole = WholeR2()

        angles = [Angle.degrees(0), Angle.degrees(45), Angle.degrees(90)]
        for angle in angles:
            assert whole.rotate(angle) == whole
            assert rotate(whole, angle) == whole


class TestSinglePointR2:

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_single_point.py::test_all",
        ],
        scope="session",
    )
    def test_begin(self):
        pass

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestSinglePointR2::test_begin"])
    def test_move(self):
        points = [(-10, -10), (5, -3), (-3, 7)]
        vectors = [(30, 2), (4, -2), (0, 0)]
        for point in points:
            single = SinglePointR2(point)
            for vector in vectors:
                good = (point[0] + vector[0], point[1] + vector[1])
                good = SinglePointR2(good)
                assert single.move(vector) == good
                assert move(single, vector) == good

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestSinglePointR2::test_begin"])
    def test_scale(self):
        single = SinglePointR2((3, 4))
        assert single.scale(1) == single
        assert scale(single, 1) == single

        assert single.scale((1, 1)) == single
        assert scale(single, (1, 1)) == single

        assert single.scale(3) == SinglePointR2((9, 12))
        assert scale(single, 3) == SinglePointR2((9, 12))

        assert single.scale((3, 4)) == SinglePointR2((9, 16))
        assert scale(single, (3, 4)) == SinglePointR2((9, 16))

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestSinglePointR2::test_begin"])
    def test_rotate(self):
        point = SinglePointR2((3, 4))

        angle = Angle.degrees(0)
        assert point.rotate(angle) == point
        assert rotate(point, angle) == point

        angle = Angle.degrees(90)
        assert point.rotate(angle) == SinglePointR2((-4, 3))
        assert rotate(point, angle) == SinglePointR2((-4, 3))


class TestNotSinglePointR2:

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_single_point.py::test_all",
        ],
        scope="session",
    )
    def test_begin(self):
        pass

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestNotSinglePointR2::test_begin"])
    def test_move(self):
        points = [(-10, -10), (5, -3), (-3, 7)]
        vectors = [(30, 2), (4, -2), (0, 0)]
        for point in points:
            subset = ~SinglePointR2(point)
            for vector in vectors:
                good = (point[0] + vector[0], point[1] + vector[1])
                good = ~SinglePointR2(good)
                assert subset.move(vector) == good
                assert move(subset, vector) == good

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestNotSinglePointR2::test_begin"])
    def test_scale(self):
        subset = ~SinglePointR2((3, 4))
        assert subset.scale(1) == subset
        assert scale(subset, 1) == subset

        assert subset.scale((1, 1)) == subset
        assert scale(subset, (1, 1)) == subset

        assert subset.scale(3) == ~SinglePointR2((9, 12))
        assert scale(subset, 3) == ~SinglePointR2((9, 12))

        assert subset.scale((3, 4)) == ~SinglePointR2((9, 16))
        assert scale(subset, (3, 4)) == ~SinglePointR2((9, 16))

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestNotSinglePointR2::test_begin"])
    def test_rotate(self):
        subset = ~SinglePointR2((3, 4))

        angle = Angle.degrees(0)
        assert subset.rotate(angle) == subset
        assert rotate(subset, angle) == subset

        angle = Angle.degrees(90)
        assert subset.rotate(angle) == ~SinglePointR2((-4, 3))
        assert rotate(subset, angle) == ~SinglePointR2((-4, 3))


class TestOrSinglePointR2:

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_single_point.py::test_all",
        ],
        scope="session",
    )
    def test_begin(self):
        pass

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOrSinglePointR2::test_begin"])
    def test_move(self):
        points = [(-10, -10), (5, -3), (-3, 7)]
        test = unite(*map(SinglePointR2, points))

        vector = (4, -2)

        goodpts = [(-6, -12), (9, -5), (1, 5)]
        good = unite(*map(SinglePointR2, goodpts))

        assert test.move(vector) == good
        assert move(test, vector) == good

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOrSinglePointR2::test_begin"])
    def test_scale(self):
        points = [(-10, -10), (5, -3), (-3, 7)]
        test = unite(*map(SinglePointR2, points))

        amount = (4, 3)

        goodpts = [(-40, -30), (20, -9), (-12, 21)]
        good = unite(*map(SinglePointR2, goodpts))

        assert test.scale(amount) == good
        assert scale(test, amount) == good

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOrSinglePointR2::test_begin"])
    def test_rotate(self):
        points = [(-10, -10), (5, -3), (-3, 7)]
        test = unite(*map(SinglePointR2, points))

        angle = Angle.degrees(90)

        goodpts = [(10, -10), (3, 5), (-7, -3)]
        good = unite(*map(SinglePointR2, goodpts))

        assert test.rotate(angle) == good
        assert rotate(test, angle) == good


class TestAndNotSinglePointR2:

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_single_point.py::test_all",
        ],
        scope="session",
    )
    def test_begin(self):
        pass

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestAndNotSinglePointR2::test_begin"])
    def test_move(self):
        points = [(-10, -10), (5, -3), (-3, 7)]
        test = intersect(*map(invert, map(SinglePointR2, points)))

        vector = (4, -2)

        goodpts = [(-6, -12), (9, -5), (1, 5)]
        good = intersect(*map(invert, map(SinglePointR2, goodpts)))

        assert test.move(vector) == good
        assert move(test, vector) == good

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestAndNotSinglePointR2::test_begin"])
    def test_scale(self):
        points = [(-10, -10), (5, -3), (-3, 7)]
        test = intersect(*map(invert, map(SinglePointR2, points)))

        amount = (4, 3)

        goodpts = [(-40, -30), (20, -9), (-12, 21)]
        good = intersect(*map(invert, map(SinglePointR2, goodpts)))

        assert test.scale(amount) == good
        assert scale(test, amount) == good

    @pytest.mark.order(50)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestAndNotSinglePointR2::test_begin"])
    def test_rotate(self):
        points = [(-10, -10), (5, -3), (-3, 7)]
        test = intersect(*map(invert, map(SinglePointR2, points)))

        angle = Angle.degrees(90)

        goodpts = [(10, -10), (3, 5), (-7, -3)]
        good = intersect(*map(invert, map(SinglePointR2, goodpts)))

        assert test.rotate(angle) == good
        assert rotate(test, angle) == good


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "TestEmpty::test_move",
        "TestWhole::test_move",
        "TestSinglePointR2::test_move",
        "TestNotSinglePointR2::test_move",
        "TestOrSinglePointR2::test_move",
        "TestAndNotSinglePointR2::test_move",
    ]
)
def test_move():
    pass


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "TestEmpty::test_scale",
        "TestWhole::test_scale",
        "TestSinglePointR2::test_scale",
        "TestNotSinglePointR2::test_scale",
        "TestOrSinglePointR2::test_scale",
        "TestAndNotSinglePointR2::test_scale",
    ]
)
def test_scale():
    pass


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "TestEmpty::test_rotate",
        "TestWhole::test_rotate",
        "TestSinglePointR2::test_rotate",
        "TestNotSinglePointR2::test_rotate",
        "TestOrSinglePointR2::test_rotate",
        "TestAndNotSinglePointR2::test_rotate",
    ]
)
def test_rotate():
    pass


@pytest.mark.order(50)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_move", "test_scale", "test_rotate"])
def test_all():
    pass
