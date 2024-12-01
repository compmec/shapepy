"""
This file contains tests functions to test the module polygon.py
"""

import pytest


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=["tests/analytic/test_polynomial.py::test_end"],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "test_begin",
    ]
)
def test_end():
    pass
