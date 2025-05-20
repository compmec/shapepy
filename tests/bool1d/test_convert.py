import pytest

from shapepy.bool1d import (
    EmptyR1,
    IntervalR1,
    SingleValueR1,
    WholeR1,
    bigger,
    from_any,
    lower,
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
        assert from_any("{}") == EmptyR1()

    @pytest.mark.order(13)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_whole(self):
        assert from_any("(-inf, inf)") == WholeR1()

    @pytest.mark.order(13)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_single(self):
        assert from_any(r"{-10}") == SingleValueR1(-10)
        assert from_any(r"{0}") == SingleValueR1(0)
        assert from_any(r"{10}") == SingleValueR1(10)
        assert from_any(r"{+10}") == SingleValueR1(10)

    @pytest.mark.order(13)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_interval(self):
        assert from_any(r"[-10, 10]") == IntervalR1(-10, 10, True, True)
        assert from_any(r"[-10, 10)") == IntervalR1(-10, 10, True, False)
        assert from_any(r"(-10, 10]") == IntervalR1(-10, 10, False, True)
        assert from_any(r"(-10, 10)") == IntervalR1(-10, 10, False, False)

        assert from_any(r"(-inf, 10]") == lower(10, True)
        assert from_any(r"(-inf, 10)") == lower(10, False)
        assert from_any(r"[-10, inf)") == bigger(-10, True)
        assert from_any(r"(-10, inf)") == bigger(-10, False)

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
