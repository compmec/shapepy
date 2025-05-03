import pytest

from shapepy.angle import Angle
from shapepy.bool2d.base import EmptyR2, WholeR2
from shapepy.bool2d.transform import move, rotate, scale


class TestEmpty:

    @pytest.mark.order(20)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_empty_whole.py::test_all",
        ],
        scope="session",
    )
    def test_begin(self):
        pass

    @pytest.mark.order(20)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestEmpty::test_begin"])
    def test_move(self):
        empty = EmptyR2()

        for vector in [(0, 0), (10, 0), (3, -5)]:
            assert empty.move(vector) == empty
            assert move(empty, vector) == empty

    @pytest.mark.order(20)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestEmpty::test_begin"])
    def test_scale(self):
        empty = EmptyR2()

        for amount in [1, 2, 3, (1, 1), (10, 3), (3, 5)]:
            assert empty.scale(amount) == empty
            assert scale(empty, amount) == empty

    @pytest.mark.order(20)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestEmpty::test_begin"])
    def test_rotate(self):
        empty = EmptyR2()

        angles = [Angle.degrees(0), Angle.degrees(45), Angle.degrees(90)]
        for angle in angles:
            assert empty.rotate(angle) == empty
            assert rotate(empty, angle) == empty


class TestWhole:

    @pytest.mark.order(20)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "tests/bool2d/test_empty_whole.py::test_all",
        ],
        scope="session",
    )
    def test_begin(self):
        pass

    @pytest.mark.order(20)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestWhole::test_begin"])
    def test_move(self):
        whole = WholeR2()

        for vector in [(0, 0), (10, 0), (3, -5)]:
            assert whole.move(vector) == whole
            assert move(whole, vector) == whole

    @pytest.mark.order(20)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestWhole::test_begin"])
    def test_scale(self):
        whole = WholeR2()

        for amount in [1, 2, 3, (1, 1), (10, 3), (3, 5)]:
            assert whole.scale(amount) == whole
            assert scale(whole, amount) == whole

    @pytest.mark.order(20)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestWhole::test_begin"])
    def test_rotate(self):
        whole = WholeR2()

        angles = [Angle.degrees(0), Angle.degrees(45), Angle.degrees(90)]
        for angle in angles:
            assert whole.rotate(angle) == whole
            assert rotate(whole, angle) == whole


@pytest.mark.order(20)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["TestEmpty::test_move", "TestWhole::test_move"]
)
def test_move():
    pass


@pytest.mark.order(20)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["TestEmpty::test_scale", "TestWhole::test_scale"]
)
def test_scale():
    pass


@pytest.mark.order(20)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=["TestEmpty::test_rotate", "TestWhole::test_rotate"]
)
def test_rotate():
    pass


@pytest.mark.order(20)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_move", "test_scale", "test_rotate"])
def test_all():
    pass
