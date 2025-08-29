import math
import random
from fractions import Fraction

import pytest

from shapepy.analytic.bezier import Bezier
from shapepy.analytic.polynomial import Polynomial
from shapepy.analytic.tools import find_minimum, find_roots, where_minimum
from shapepy.rbool import EmptyR1, WholeR1
from shapepy.scalar.reals import Math


@pytest.mark.order(9)
@pytest.mark.dependency(
    depends=[
        "tests/analytic/test_derivate.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(9)
@pytest.mark.dependency(depends=["test_begin"])
def test_polynomial_roots():
    poly = Polynomial([0])
    assert find_roots(poly) == WholeR1()
    for const in range(-10, 11):
        if const != 0:
            poly = Polynomial([const])
            assert find_roots(poly) == EmptyR1()

    ntests = 100
    x = Polynomial([0, 1])
    # Finds the roots of p(x) = a * x + b
    for _ in range(ntests):
        a = random.randint(1, 10)
        b = random.randint(-10, 10)
        assert find_roots(a * x + b) == {Fraction(-b, a)}

    # Finds the roots of p(x) = (x - x0) * (x - x1)
    for _ in range(ntests):
        x0 = random.randint(-10, 10)
        x1 = random.randint(-10, 10)
        assert find_roots((x - x0) * (x - x1)) == {x0, x1}

    poly = Polynomial([1, 0, 1])  # p(x) = 1 + x^2
    assert find_roots(poly) == EmptyR1()

    # Finds the roots of p(x) = a * x^2 + b * x + c
    for _ in range(ntests):
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        c = random.randint(1, 100)
        poly = a * x * x + b * x + c
        delta = b * b - 4 * a * c
        if delta < 0:
            assert find_roots(poly) == EmptyR1()
        elif delta == 0:
            assert find_roots(poly) == {-b / 2 * a}
        else:
            x0 = (-b - math.sqrt(delta)) / (2 * a)
            x1 = (-b + math.sqrt(delta)) / (2 * a)
            assert find_roots(poly) == {x0, x1}


@pytest.mark.order(9)
@pytest.mark.dependency(depends=["test_begin"])
def test_bezier_roots():
    bezier = Bezier([0])
    assert find_roots(bezier) == WholeR1()
    assert find_roots(bezier, [0, 1]) == [0, 1]

    bezier = Bezier([1, -1])
    assert find_roots(bezier) == {1 / 2}
    assert find_roots(bezier, [0, 1]) == {1 / 2}


@pytest.mark.order(9)
@pytest.mark.dependency(depends=["test_begin"])
def test_where_minimal_polynomial():
    for const in range(-10, 11):
        poly = Polynomial([const])
        assert where_minimum(poly) == WholeR1()

    x = Polynomial([0, 1])
    ntests = 100
    # Finds the minimum of p(x) = a * x + b, which does not exist
    for _ in range(ntests):
        a = random.randint(1, 10)
        b = random.randint(-10, 10)
        assert where_minimum(a * x + b) == EmptyR1()
        assert where_minimum(-a * x + b) == EmptyR1()

    # Finds the minimum of p(x) = a * x + b, in a closed interval
    for _ in range(ntests):
        a = random.randint(-10, 10)
        if a == 0:
            continue
        b = random.randint(-10, 10)
        x0 = random.randint(-10, -1)
        x1 = random.randint(1, 10)
        interval = [x0, x1]
        if a * x0 + b < a * x1 + b:
            assert where_minimum(a * x + b, interval) == {x0}
        elif a * x1 + b < a * x0 + b:
            assert where_minimum(a * x + b, interval) == {x1}

    # Finds minimum of f(x) = (x + 1) * x * (x - 1)
    poly = x * (x - 1) * (x + 1)
    assert where_minimum(poly) == EmptyR1()
    assert where_minimum(-poly) == EmptyR1()

    # Finds minimum of f(x) = (x + 2) * (x + 1) * (x - 1) * (x - 2)
    poly = (x + 2) * (x + 1) * (x - 1) * (x - 2)
    posroot = math.sqrt(5 / 2)
    assert where_minimum(poly) == {-posroot, posroot}
    assert where_minimum(poly, [-1, 10]) == {posroot}


@pytest.mark.order(9)
@pytest.mark.dependency(depends=["test_begin"])
def test_where_minimal_bezier():
    bezier = Bezier([1, -1])
    assert where_minimum(bezier, [0, 1]) == {1}


@pytest.mark.order(9)
@pytest.mark.dependency(depends=["test_begin"])
def test_minimal_value_polynomial():
    for const in range(-10, 11):
        poly = Polynomial([const])
        assert find_minimum(poly) == const

    x = Polynomial([0, 1])
    ntests = 100
    # Finds the minimum of p(x) = a * x + b, which does not exist
    for _ in range(ntests):
        a = random.randint(1, 10)
        b = random.randint(-10, 10)
        assert find_minimum(a * x + b) == Math.NEGINF
        assert find_minimum(-a * x + b) == Math.NEGINF

    # Finds the minimum of p(x) = a * x + b, in a closed interval
    for _ in range(ntests):
        a = random.randint(-10, 10)
        if a == 0:
            continue
        b = random.randint(-10, 10)
        x0 = random.randint(-10, -1)
        x1 = random.randint(1, 10)
        interval = [x0, x1]
        assert find_minimum(a * x + b, interval) == min(a * x0 + b, a * x1 + b)

    # Finds minimum of f(x) = (x + 1) * x * (x - 1)
    poly = x * (x - 1) * (x + 1)
    assert find_minimum(poly) == Math.NEGINF
    assert find_minimum(-poly) == Math.NEGINF

    # Finds minimum of f(x) = (x + 2) * (x + 1) * (x - 1) * (x - 2)
    poly = (x + 2) * (x + 1) * (x - 1) * (x - 2)
    assert abs(find_minimum(poly) + 9 / 4) < 1e-12
    assert abs(find_minimum(poly, [-1, 10]) + 9 / 4) < 1e-12


@pytest.mark.order(9)
@pytest.mark.dependency(depends=["test_begin"])
def test_minimum_value_bezier():
    bezier = Bezier([1, -1])
    assert find_minimum(bezier, [0, 1]) == -1


@pytest.mark.order(9)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_polynomial_roots",
        "test_bezier_roots",
        "test_where_minimal_polynomial",
        "test_where_minimal_bezier",
        "test_minimal_value_polynomial",
    ]
)
def test_all():
    pass
