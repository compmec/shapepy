import pytest

from shapepy.bool1d import (
    EmptyR1,
    IntervalR1,
    SingleValueR1,
    WholeR1,
    from_any,
)


@pytest.mark.order(17)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/bool1d/test_build.py::test_all",
        "tests/bool1d/test_convert.py::test_all",
        "tests/bool1d/test_compare.py::test_all",
        "tests/bool1d/test_contains.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


class TestShift:

    @pytest.mark.order(17)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_empty(self):
        empty = EmptyR1()
        assert empty.move(-1) == empty
        assert empty.move(0) == empty
        assert empty.move(1) == empty

    @pytest.mark.order(17)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_whole(self):
        whole = WholeR1()
        assert whole.move(-1) == whole
        assert whole.move(0) == whole
        assert whole.move(1) == whole

    @pytest.mark.order(17)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_single(self):
        values = [-10, 0, 1]
        amounts = [-20, -10, 0, 10, 20]

        for value in values:
            single = SingleValueR1(value)
            for amount in amounts:
                test = single.move(amount)
                good = SingleValueR1(value + amount)
                assert test == good

            with pytest.raises(ValueError):
                single.move(float("-inf"))
            with pytest.raises(ValueError):
                single.move(float("inf"))

    @pytest.mark.order(17)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_interval(self):
        base = IntervalR1(-10, 10)
        test = base.move(-5)
        good = IntervalR1(-15, 5)
        assert test == good

    @pytest.mark.order(17)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_disjoint(self):
        base = from_any(r"[-10, -5) U {-4} U (3, 4]")
        test = base.move(-5)
        good = from_any(r"[-15, -10) U {-9} U (-2, -1]")
        assert test == good

    @pytest.mark.order(17)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestShift::test_empty",
            "TestShift::test_whole",
            "TestShift::test_single",
            "TestShift::test_interval",
            "TestShift::test_disjoint",
        ]
    )
    def test_all(self):
        pass


class TestScale:

    @pytest.mark.order(17)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_empty(self):
        empty = EmptyR1()
        assert empty.scale(-1) == empty
        assert empty.scale(1) == empty

    @pytest.mark.order(17)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_whole(self):
        whole = WholeR1()
        assert whole.scale(-1) == whole
        assert whole.scale(1) == whole

    @pytest.mark.order(17)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_single(self):
        values = [-10, 0, 1]
        amounts = [-20, -10, 10, 20]

        for value in values:
            single = SingleValueR1(value)
            for amount in amounts:
                test = single.scale(amount)
                good = SingleValueR1(value * amount)
                assert test == good

            with pytest.raises(ValueError):
                single.scale(0)
            with pytest.raises(ValueError):
                single.scale(float("-inf"))
            with pytest.raises(ValueError):
                single.scale(float("inf"))

    @pytest.mark.order(17)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_interval(self):
        base = IntervalR1(-10, 10)
        assert base.scale(1) == base
        assert base.scale(2) == IntervalR1(-20, 20)
        assert base.scale(-1) == base  # symmetry

        base = IntervalR1(0, 10)
        assert base.scale(1) == base
        assert base.scale(2) == IntervalR1(0, 20)
        assert base.scale(-1) == IntervalR1(-10, 0)

        base = from_any("[-10, 5)")
        assert base.scale(1) == base
        assert base.scale(2) == from_any("[-20, 10)")
        assert base.scale(-1) == from_any("(-5, 10]")

    @pytest.mark.order(17)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_disjoint(self):
        base = from_any(r"[-10, -5) U {-4} U (3, 4]")
        assert base.scale(1) == base

        good = from_any(r"[-20, -10) U {-8} U (6, 8]")
        assert base.scale(2) == good

        good = from_any(r"[-4, -3) U {4} U (5, 10]")
        assert base.scale(-1) == good

    @pytest.mark.order(17)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestScale::test_empty",
            "TestScale::test_whole",
            "TestScale::test_single",
            "TestScale::test_interval",
            "TestScale::test_disjoint",
        ]
    )
    def test_all(self):
        pass


@pytest.mark.order(17)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "TestShift::test_all",
        "TestScale::test_all",
    ]
)
def test_all():
    pass
