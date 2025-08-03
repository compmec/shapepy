"""
This file contains tests functions to test the module polygon.py
"""

import pytest


@pytest.mark.order(12)
@pytest.mark.dependency(
    depends=[
        "tests/scalar/test_reals.py::test_all",
        "tests/analytic/test_polynomial.py::test_all",
        "tests/analytic/test_bezier.py::test_all",
        "tests/geometry/test_point.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(12)
@pytest.mark.dependency(
    depends=[
        "test_begin",
    ]
)
def test_all():
    pass
