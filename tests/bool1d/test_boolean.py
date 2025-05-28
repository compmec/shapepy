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


@pytest.mark.order(16)
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


class TestInversion:

    @pytest.mark.order(16)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_singletion(self):
        empty = EmptyR1()
        whole = WholeR1()

        assert ~empty == whole
        assert ~whole == empty

    @pytest.mark.order(16)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_single(self):
        assert ~SingleValueR1(0) == "(-inf, 0) U (0, inf)"
        assert ~SingleValueR1(-10) == "(-inf, -10) U (-10, inf)"
        assert ~SingleValueR1(+10) == "(-inf, 10) U (10, inf)"

    @pytest.mark.order(16)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_interval(self):

        assert ~lower(0, True) == bigger(0, False)
        assert ~lower(0, False) == bigger(0, True)
        assert ~bigger(0, True) == lower(0, False)
        assert ~bigger(0, False) == lower(0, True)

        assert ~from_any("[-10, 10]") == "(-inf, -10) U (10, inf)"

    @pytest.mark.order(16)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_disjoint(self):
        assert ~from_any("(-inf, -10) U (10, inf)") == "[-10, 10]"

        assert ~from_any("(-inf, 0) U (0, inf)") == {0}
        assert ~from_any("(-inf, -10) U (-10, inf)") == {-10}
        assert ~from_any("(-inf, +10) U (+10, inf)") == {10}

        assert ~from_any("(-inf, -10) U (-10, 10) U (10, inf)") == {-10, 10}

    @pytest.mark.order(16)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestInversion::test_singletion",
            "TestInversion::test_single",
            "TestInversion::test_interval",
            "TestInversion::test_disjoint",
        ]
    )
    def test_all(self):
        pass


class TestAndOr:

    @pytest.mark.order(16)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_singleton(self):
        empty = EmptyR1()
        whole = WholeR1()

        assert empty & empty == empty
        assert whole & empty == empty
        assert empty & whole == empty
        assert whole & whole == whole

        assert empty | empty == empty
        assert whole | empty == whole
        assert empty | whole == whole
        assert whole | whole == whole

        assert empty - empty == empty
        assert whole - empty == whole
        assert empty - whole == empty
        assert whole - whole == empty

        assert empty ^ empty == empty
        assert whole ^ empty == whole
        assert empty ^ whole == whole
        assert whole ^ whole == empty

    @pytest.mark.order(16)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_single_singleton(self):
        empty = EmptyR1()
        whole = WholeR1()

        for value in (-10, 0, 10):
            single = SingleValueR1(value)
            assert single & empty == empty
            assert single & whole == single
            assert empty & single == empty
            assert whole & single == single

            assert single | empty == single
            assert single | whole == whole
            assert empty | single == single
            assert whole | single == whole

            assert single - empty == single
            assert single - whole == empty
            assert empty - single == empty
            assert whole - single == ~single

            assert single ^ empty == single
            assert single ^ whole == ~single
            assert empty ^ single == single
            assert whole ^ single == ~single

            single = {10}
            assert single & empty == empty
            assert single & whole == single
            assert empty & single == empty
            assert whole & single == single

            assert single | empty == single
            assert single | whole == whole
            assert empty | single == single
            assert whole | single == whole

    @pytest.mark.order(16)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_single_single(self):
        empty = EmptyR1()

        values = (-10, 0, 10)
        singles = tuple(map(SingleValueR1, values))
        for i, (vali, singi) in enumerate(zip(values, singles)):
            for j, (valj, singj) in enumerate(zip(values, singles)):
                if i == j:
                    assert singi | singj == singi
                    assert singi & singj == singi
                    assert singi - singj == empty
                    assert singi ^ singj == empty

                    assert singi | {valj} == singi
                    assert singi & {valj} == singi
                    assert singi - {valj} == empty
                    assert singi ^ {valj} == empty

                    assert {vali} | singj == singi
                    assert {vali} & singj == singi
                    assert {vali} - singj == empty
                    assert {vali} ^ singj == empty
                else:
                    assert singi | singj == {vali, valj}
                    assert singi & singj == empty
                    assert singi - singj == singi
                    assert singi ^ singj == {vali, valj}

                    assert singi | {valj} == {vali, valj}
                    assert singi & {valj} == empty
                    assert singi - {valj} == singi
                    assert singi ^ {valj} == {vali, valj}

                    assert {vali} | singj == {vali, valj}
                    assert {vali} & singj == empty
                    assert {vali} - singj == singi
                    assert {vali} ^ singj == {vali, valj}

    @pytest.mark.order(16)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_interval_contains_disjoint(self):
        string = "{-30, -25} U [-20, 20] U {25, 30, 40}"
        disjoint = from_any(string)
        assert disjoint in IntervalR1(-50, 50)

    @pytest.mark.order(16)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestAndOr::test_singleton",
            "TestAndOr::test_single_singleton",
            "TestAndOr::test_single_single",
            "TestAndOr::test_interval_contains_disjoint",
        ]
    )
    def test_all(self):
        pass


@pytest.mark.order(16)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "TestInversion::test_all",
        "TestAndOr::test_all",
    ]
)
def test_all():
    pass
