import pytest

from shapepy.bool1d import (
    EmptyR1,
    IntervalR1,
    SingleValueR1,
    WholeR1,
    subsetR1,
)


@pytest.mark.order(13)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/bool1d/test_build.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


class TestFromString:

    @pytest.mark.order(13)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_empty(self):
        assert subsetR1("{}") == EmptyR1()

    @pytest.mark.order(13)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_whole(self):
        assert subsetR1("(-inf, inf)") == WholeR1()

    @pytest.mark.order(13)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_single(self):
        assert subsetR1(r"{-10}") == SingleValueR1(-10)
        assert subsetR1(r"{0}") == SingleValueR1(0)
        assert subsetR1(r"{10}") == SingleValueR1(10)
        assert subsetR1(r"{+10}") == SingleValueR1(10)

    @pytest.mark.order(13)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_interval(self):
        assert subsetR1(r"[-10, 10]") == IntervalR1(-10, 10, True, True)
        assert subsetR1(r"[-10, 10)") == IntervalR1(-10, 10, True, False)
        assert subsetR1(r"(-10, 10]") == IntervalR1(-10, 10, False, True)
        assert subsetR1(r"(-10, 10)") == IntervalR1(-10, 10, False, False)

        assert subsetR1(r"(-inf, 10]") == IntervalR1.lower(10, True)
        assert subsetR1(r"(-inf, 10)") == IntervalR1.lower(10, False)
        assert subsetR1(r"[-10, inf)") == IntervalR1.bigger(-10, True)
        assert subsetR1(r"(-10, inf)") == IntervalR1.bigger(-10, False)

    @pytest.mark.order(13)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_disjoint(self):
        pass

    @pytest.mark.order(13)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestFromString::test_empty",
            "TestFromString::test_whole",
            "TestFromString::test_single",
            "TestFromString::test_interval",
            "TestFromString::test_disjoint",
        ]
    )
    def test_all(self):
        pass


@pytest.mark.order(13)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "TestFromString::test_all",
    ]
)
def test_all():
    pass
