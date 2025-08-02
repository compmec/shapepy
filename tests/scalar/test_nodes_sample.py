from fractions import Fraction as frac
from math import sqrt

import pytest

from shapepy.scalar.nodes_sample import NodeSampleFactory


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "tests/scalar/test_reals.py::test_all",
        "tests/scalar/test_angle.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(4)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_closed_linspace():
    method = NodeSampleFactory.closed_linspace
    assert method(2) == (0, 1)
    assert method(3) == (0, frac(1, 2), 1)
    assert method(4) == (0, frac(1, 3), frac(2, 3), 1)
    assert method(5) == (0, frac(1, 4), frac(2, 4), frac(3, 4), 1)
    assert method(6) == (0, frac(1, 5), frac(2, 5), frac(3, 5), frac(4, 5), 1)


@pytest.mark.order(4)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_closed_newton_cotes():
    method = NodeSampleFactory.closed_newton_cotes
    assert method(2) == (0, 1)
    assert method(3) == (0, frac(1, 2), 1)
    assert method(4) == (0, frac(1, 3), frac(2, 3), 1)
    assert method(5) == (0, frac(1, 4), frac(2, 4), frac(3, 4), 1)
    assert method(6) == (0, frac(1, 5), frac(2, 5), frac(3, 5), frac(4, 5), 1)


@pytest.mark.order(4)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_open_newton_cotes():
    method = NodeSampleFactory.open_newton_cotes
    assert method(1) == (frac(1, 2),)
    assert method(2) == (frac(1, 3), frac(2, 3))
    assert method(3) == (frac(1, 4), frac(2, 4), frac(3, 4))
    assert method(4) == (frac(1, 5), frac(2, 5), frac(3, 5), frac(4, 5))
    assert method(5) == (
        frac(1, 6),
        frac(2, 6),
        frac(3, 6),
        frac(4, 6),
        frac(5, 6),
    )
    assert method(6) == (
        frac(1, 7),
        frac(2, 7),
        frac(3, 7),
        frac(4, 7),
        frac(5, 7),
        frac(6, 7),
    )


@pytest.mark.order(4)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_custom_open_formula():
    method = NodeSampleFactory.custom_open_formula
    assert method(1) == (frac(1, 2),)
    assert method(2) == (frac(1, 4), frac(3, 4))
    assert method(3) == (frac(1, 6), frac(3, 6), frac(5, 6))
    assert method(4) == (frac(1, 8), frac(3, 8), frac(5, 8), frac(7, 8))
    assert method(5) == (
        frac(1, 10),
        frac(3, 10),
        frac(5, 10),
        frac(7, 10),
        frac(9, 10),
    )


@pytest.mark.order(4)
@pytest.mark.timeout(1)
@pytest.mark.dependency(depends=["test_begin"])
def test_chebyshev():
    method = NodeSampleFactory.chebyshev

    results = {
        1: (frac(1, 2),),
        2: (frac(1, 2) - sqrt(2) / 4, frac(1, 2) + sqrt(2) / 4),
        3: (
            frac(1, 2) - sqrt(3) / 4,
            frac(1, 2),
            frac(1, 2) + sqrt(3) / 4,
        ),
        4: (
            frac(1, 2) - sqrt(2 + sqrt(2)) / 4,
            frac(1, 2) - sqrt(2 - sqrt(2)) / 4,
            frac(1, 2) + sqrt(2 - sqrt(2)) / 4,
            frac(1, 2) + sqrt(2 + sqrt(2)) / 4,
        ),
        5: (
            frac(1, 2) - sqrt(10 + 2 * sqrt(5)) / 8,
            frac(1, 2) - sqrt(10 - 2 * sqrt(5)) / 8,
            frac(1, 2),
            frac(1, 2) + sqrt(10 - 2 * sqrt(5)) / 8,
            frac(1, 2) + sqrt(10 + 2 * sqrt(5)) / 8,
        ),
    }

    for npts, good in results.items():
        test = method(npts)
        for ti, gi in zip(test, good):
            assert abs(ti - gi) < 1e-15


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_closed_linspace",
        "test_closed_newton_cotes",
        "test_open_newton_cotes",
        "test_custom_open_formula",
        "test_chebyshev",
    ]
)
def test_all():
    pass
