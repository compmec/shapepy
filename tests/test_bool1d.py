import pytest

from shapepy import default
from shapepy.bool1d import (
    DisjointR1,
    EmptyR1,
    IntervalR1,
    SingleValueR1,
    WholeR1,
    subsetR1,
)


class TestBuild:

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_empty(self):
        empty1 = EmptyR1()
        empty2 = EmptyR1()
        assert id(empty1) == id(empty2)
        assert empty1 is empty2

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_whole(self):
        whole1 = WholeR1()
        whole2 = WholeR1()
        assert id(whole1) == id(whole2)
        assert whole1 is whole2

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_single(self):
        SingleValueR1(-10)
        SingleValueR1(0)
        SingleValueR1(10)

        SingleValueR1(-10.0)
        SingleValueR1(0.0)
        SingleValueR1(10.0)

        with pytest.raises(ValueError):
            SingleValueR1(float("-inf"))
        with pytest.raises(ValueError):
            SingleValueR1(float("inf"))

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_interval(self):
        IntervalR1(-10, 10)
        IntervalR1(float("-inf"), 10)
        IntervalR1(-10, float("inf"))
        with pytest.raises(ValueError):
            IntervalR1(float("-inf"), float("inf"))

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_disjoint(self):
        pass


class TestPrinting:

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestBuild::test_empty"])
    def test_empty(self):
        empty = EmptyR1()
        assert str(empty) == r"{}"
        assert repr(empty) == r"EmptyR1"

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestBuild::test_whole"])
    def test_whole(self):
        whole = WholeR1()
        assert str(whole) == r"(-inf, inf)"
        assert repr(whole) == r"WholeR1"

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestBuild::test_single"])
    def test_single(self):
        value = SingleValueR1(-10)
        assert str(value) == r"{-10}"
        assert repr(value) == r"SingleValueR1(-10)"

        value = SingleValueR1(0)
        assert str(value) == r"{0}"
        assert repr(value) == r"SingleValueR1(0)"

        value = SingleValueR1(10)
        assert str(value) == r"{10}"
        assert repr(value) == r"SingleValueR1(10)"

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestBuild::test_interval"])
    def test_interval(self):
        interval = IntervalR1(-10, 10, True, True)
        assert str(interval) == r"[-10, 10]"

        interval = IntervalR1(-10, 10, True, False)
        assert str(interval) == r"[-10, 10)"

        interval = IntervalR1(-10, 10, False, True)
        assert str(interval) == r"(-10, 10]"

        interval = IntervalR1(-10, 10, False, False)
        assert str(interval) == r"(-10, 10)"

        interval = IntervalR1.lower(10, True)
        assert str(interval) == r"(-inf, 10]"

        interval = IntervalR1.lower(10, False)
        assert str(interval) == r"(-inf, 10)"

        interval = IntervalR1.bigger(-10, True)
        assert str(interval) == r"[-10, inf)"

        interval = IntervalR1.bigger(-10, False)
        assert str(interval) == r"(-10, inf)"

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestBuild::test_disjoint"])
    def test_disjoint(self):
        interv0 = IntervalR1.lower(-50)
        interv1 = IntervalR1.bigger(50)
        disjoint = DisjointR1([interv0, interv1])
        assert str(disjoint) == "(-inf, -50] U [50, inf)"
        repr(disjoint)

        interv2 = IntervalR1(-20, 20)
        singles = list(map(SingleValueR1, [-30, -25, 25, 30, 40]))
        disjoint = DisjointR1([interv0, interv1, interv2] + singles)
        assert (
            str(disjoint)
            == "(-inf, -50] U {-30, -25} U [-20, 20] U {25, 30, 40} U [50, inf)"
        )
        repr(disjoint)

        disjoint = DisjointR1([interv0, interv2] + singles)
        assert (
            str(disjoint)
            == "(-inf, -50] U {-30, -25} U [-20, 20] U {25, 30, 40}"
        )
        repr(disjoint)

        disjoint = DisjointR1(singles)
        assert str(disjoint) == "{-30, -25, 25, 30, 40}"
        repr(disjoint)


class TestCompare:

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestBuild::test_empty"])
    def test_empty(self):
        empty = EmptyR1()

        assert empty == empty
        assert empty == {}
        assert empty == r"{}"

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestBuild::test_whole"])
    def test_whole(self):
        whole = WholeR1()
        NEGINF = default.NEGINF
        POSINF = default.POSINF

        assert whole == whole
        assert whole == (float("-inf"), float("inf"))
        assert whole == (float("-inf"), POSINF)
        assert whole == (NEGINF, float("inf"))
        assert whole == (NEGINF, POSINF)
        assert whole == [float("-inf"), float("inf")]
        assert whole == [float("-inf"), POSINF]
        assert whole == [NEGINF, float("inf")]
        assert whole == [NEGINF, POSINF]
        assert whole == r"(-inf, inf)"

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=["TestCompare::test_empty", "TestCompare::test_whole"]
    )
    def test_singletons(self):
        empty = EmptyR1()
        whole = WholeR1()

        assert empty == empty
        assert empty != whole
        assert whole != empty
        assert whole == whole

        assert not empty != empty
        assert not empty == whole
        assert not whole == empty
        assert not whole != whole

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestCompare::test_singletons"])
    def test_singles(self):
        empty = EmptyR1()
        whole = WholeR1()

        for value in (-10, 0, 10):
            single = SingleValueR1(value)
            assert single == single
            assert single == value
            assert single == {value}
            assert single == "{" + str(value) + "}"

            assert single != empty
            assert empty != single
            assert single != whole
            assert whole != single

            assert not single == empty
            assert not empty == single
            assert not single == whole
            assert not whole == single

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_intervals(self):
        empty = EmptyR1()
        whole = WholeR1()

        NEGINF = default.NEGINF
        POSINF = default.POSINF
        aval, bval = -10, 10

        n2a = IntervalR1(NEGINF, aval)
        n2b = IntervalR1(NEGINF, bval)
        a2b = IntervalR1(aval, bval)
        a2p = IntervalR1(aval, POSINF)
        b2p = IntervalR1(bval, POSINF)

        intervals = (n2a, n2b, a2b, a2p, b2p)
        for i, intvi in enumerate(intervals):
            for j, intvj in enumerate(intervals):
                if i == j:
                    assert intvi == intvj
                else:
                    assert intvi != intvj

        for interv in intervals:
            assert empty != interv
            assert whole != interv
            assert interv != empty
            assert interv != whole

            assert not empty == interv
            assert not whole == interv
            assert not interv == empty
            assert not interv == whole

        closed_pairs = [
            (-50, 50),
            (-50, -20),
            (20, 50),
            (NEGINF, -20),
            (NEGINF, 0),
            (NEGINF, 20),
            (-20, POSINF),
            (0, POSINF),
            (20, POSINF),
        ]
        for sta, end in closed_pairs:
            interv = IntervalR1(sta, end, True, True)
            assert interv == [sta, end]
            assert [sta, end] == interv

        open_pairs = [
            (-50, 50),
            (-50, -20),
            (20, 50),
            (NEGINF, -20),
            (NEGINF, 0),
            (NEGINF, 20),
            (-20, POSINF),
            (0, POSINF),
            (20, POSINF),
        ]
        for sta, end in open_pairs:
            interv = IntervalR1(sta, end, False, False)
            assert interv == (sta, end)
            assert (sta, end) == interv


class TestFromString:

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_empty(self):
        assert subsetR1("{}") == EmptyR1()

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_whole(self):
        assert subsetR1("(-inf, inf)") == WholeR1()

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_single(self):
        assert subsetR1(r"{-10}") == SingleValueR1(-10)
        assert subsetR1(r"{0}") == SingleValueR1(0)
        assert subsetR1(r"{10}") == SingleValueR1(10)
        assert subsetR1(r"{+10}") == SingleValueR1(10)

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_interval(self):
        assert subsetR1(r"[-10, 10]") == IntervalR1(-10, 10, True, True)
        assert subsetR1(r"[-10, 10)") == IntervalR1(-10, 10, True, False)
        assert subsetR1(r"(-10, 10]") == IntervalR1(-10, 10, False, True)
        assert subsetR1(r"(-10, 10)") == IntervalR1(-10, 10, False, False)

        assert subsetR1(r"(-inf, 10]") == IntervalR1.lower(10, True)
        assert subsetR1(r"(-inf, 10)") == IntervalR1.lower(10, False)
        assert subsetR1(r"[-10, inf)") == IntervalR1.bigger(-10, True)
        assert subsetR1(r"(-10, inf)") == IntervalR1.bigger(-10, False)


class TestContains:

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_singleton_in_singleton(self):
        empty = EmptyR1()
        whole = WholeR1()

        assert empty in empty
        assert empty in whole

        assert whole not in empty
        assert whole in whole

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_singleton_contains_object(self):
        empty = EmptyR1()
        whole = WholeR1()

        values = (-100, -50, -20, -10, 0, 10, 20, 50, 100)
        singls = tuple(map(SingleValueR1, values))
        for value in values:
            assert value not in empty
            assert value in whole
        for single in singls:
            assert empty in single
            assert whole not in single
            assert single not in empty
            assert single in whole

        NEGINF = default.NEGINF
        POSINF = default.POSINF
        aval, bval = -10, 10

        n2a = IntervalR1(NEGINF, aval)
        n2b = IntervalR1(NEGINF, bval)
        a2b = IntervalR1(aval, bval)
        a2p = IntervalR1(aval, POSINF)
        b2p = IntervalR1(bval, POSINF)
        intervals = (n2a, n2b, a2b, a2p, b2p)
        for interval in intervals:
            assert empty in interval
            assert whole not in interval
            assert interval not in empty
            assert interval in whole

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_interval_contains_interval(self):

        NEGINF = default.NEGINF
        POSINF = default.POSINF
        aval, bval = -10, 10

        n2a = IntervalR1(NEGINF, aval)
        n2b = IntervalR1(NEGINF, bval)
        a2b = IntervalR1(aval, bval)
        a2p = IntervalR1(aval, POSINF)
        b2p = IntervalR1(bval, POSINF)

        assert n2a in n2a
        assert n2a in n2b
        assert n2a not in a2b
        assert n2a not in a2p
        assert n2a not in b2p

        assert n2b not in n2a
        assert n2b in n2b
        assert n2b not in a2b
        assert n2b not in a2p
        assert n2b not in b2p

        assert a2b not in n2a
        assert a2b in n2b
        assert a2b in a2b
        assert a2b in a2p
        assert a2b not in b2p

        assert a2p not in n2a
        assert a2p not in n2b
        assert a2p not in a2b
        assert a2p in a2p
        assert a2p not in b2p

        assert b2p not in n2a
        assert b2p not in n2b
        assert b2p not in a2b
        assert b2p in a2p
        assert b2p in b2p

        assert IntervalR1(-50, -20) not in IntervalR1(0, 20)
        assert IntervalR1(10, 50) not in IntervalR1(0, 20)
        assert IntervalR1(-10, 10) in IntervalR1(-20, 20)
        assert IntervalR1(-10, 10, True, True) not in IntervalR1(
            -20, 10, True, False
        )
        assert IntervalR1(-10, 10, True, True) not in IntervalR1(
            -10, 20, False, True
        )

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_disjoint_contains_object(self):
        string = r"(-inf, -20) U [-10, -5] U [0, 5) U (10, 15] U (20, 25) U {30, 31, 33}"
        disjoint = subsetR1(string)
        assert isinstance(disjoint, DisjointR1)

        inside = {-25, -10, -7, -5, 0, 2, 12, 15, 22, 30, 31, 33}
        outside = {-20, -15, -2, 5, 7, 10, 17, 20, 25, 28, 32}
        for value in inside:
            assert value in disjoint
        for value in outside:
            assert value not in disjoint

        assert disjoint == string
        assert disjoint != {30, 31}
        assert disjoint != [-10, -5]
        assert disjoint != {30}
        assert disjoint != EmptyR1()
        assert disjoint != WholeR1()

        assert {30, 31} in disjoint
        assert [-10, -5] in disjoint
        assert {30} in disjoint
        assert EmptyR1() in disjoint
        assert WholeR1() not in disjoint


class TestInversion:

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_singletion(self):
        empty = EmptyR1()
        whole = WholeR1()

        assert ~empty == whole
        assert ~whole == empty

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_single(self):
        assert ~SingleValueR1(0) == "(-inf, 0) U (0, inf)"
        assert ~SingleValueR1(-10) == "(-inf, -10) U (-10, inf)"
        assert ~SingleValueR1(+10) == "(-inf, 10) U (10, inf)"

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_interval(self):

        assert ~IntervalR1.lower(0, True) == IntervalR1.bigger(0, False)
        assert ~IntervalR1.lower(0, False) == IntervalR1.bigger(0, True)
        assert ~IntervalR1.bigger(0, True) == IntervalR1.lower(0, False)
        assert ~IntervalR1.bigger(0, False) == IntervalR1.lower(0, True)

        assert ~subsetR1("[-10, 10]") == "(-inf, -10) U (10, inf)"

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_disjoint(self):
        assert ~subsetR1("(-inf, -10) U (10, inf)") == "[-10, 10]"

        assert ~subsetR1("(-inf, 0) U (0, inf)") == {0}
        assert ~subsetR1("(-inf, -10) U (-10, inf)") == {-10}
        assert ~subsetR1("(-inf, +10) U (+10, inf)") == {10}

        assert ~subsetR1("(-inf, -10) U (-10, 10) U (10, inf)") == {-10, 10}


class TestAndOr:

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
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

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
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

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
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

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_interval_contains_disjoint(self):
        string = "{-30, -25} U [-20, 20] U {25, 30, 40}"
        disjoint = subsetR1(string)
        assert disjoint in IntervalR1(-50, 50)


class TestShift:

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_empty(self):
        empty = EmptyR1()
        assert empty.shift(-1) == empty
        assert empty.shift(0) == empty
        assert empty.shift(1) == empty

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_whole(self):
        whole = WholeR1()
        assert whole.shift(-1) == whole
        assert whole.shift(0) == whole
        assert whole.shift(1) == whole

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_single(self):
        values = [-10, 0, 1]
        amounts = [-20, -10, 0, 10, 20]

        for value in values:
            single = SingleValueR1(value)
            for amount in amounts:
                test = single.shift(amount)
                good = SingleValueR1(value + amount)
                assert test == good

            with pytest.raises(ValueError):
                single.shift(float("-inf"))
            with pytest.raises(ValueError):
                single.shift(float("inf"))

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_interval(self):
        base = IntervalR1(-10, 10)
        test = base.shift(-5)
        good = IntervalR1(-15, 5)
        assert test == good

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_disjoint(self):
        base = subsetR1(r"[-10, -5) U {-4} U (3, 4]")
        test = base.shift(-5)
        good = subsetR1(r"[-15, -10) U {-9} U (-2, -1]")
        assert test == good


class TestScale:

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_empty(self):
        empty = EmptyR1()
        assert empty.scale(-1) == empty
        assert empty.scale(1) == empty

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_whole(self):
        whole = WholeR1()
        assert whole.scale(-1) == whole
        assert whole.scale(1) == whole

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
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

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_interval(self):
        base = IntervalR1(-10, 10)
        assert base.scale(1) == base
        assert base.scale(2) == IntervalR1(-20, 20)
        assert base.scale(-1) == base  # symmetry

        base = IntervalR1(0, 10)
        assert base.scale(1) == base
        assert base.scale(2) == IntervalR1(0, 20)
        assert base.scale(-1) == IntervalR1(-10, 0)

        base = subsetR1("[-10, 5)")
        assert base.scale(1) == base
        assert base.scale(2) == subsetR1("[-20, 10)")
        assert base.scale(-1) == subsetR1("(-5, 10]")

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency()
    def test_disjoint(self):
        base = subsetR1(r"[-10, -5) U {-4} U (3, 4]")
        assert base.scale(1) == base

        good = subsetR1(r"[-20, -10) U {-8} U (6, 8]")
        assert base.scale(2) == good

        good = subsetR1(r"[-4, -3) U {4} U (5, 10]")
        assert base.scale(-1) == good
