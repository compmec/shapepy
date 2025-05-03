import pytest

from shapepy import default
from shapepy.bool1d import infimum, maximum, minimum, supremum


@pytest.mark.order(17)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "tests/bool1d/test_build.py::test_all",
        "tests/bool1d/test_convert.py::test_all",
    ],
    scope="session",
)
def test_inf_min_max_sup():
    subset = r"{}"
    assert infimum(subset) is None
    assert minimum(subset) is None
    assert maximum(subset) is None
    assert supremum(subset) is None

    subset = r"(-inf, +inf)"
    assert infimum(subset) == default.NEGINF
    assert minimum(subset) is None
    assert maximum(subset) is None
    assert supremum(subset) == default.POSINF

    subset = r"{1}"
    assert infimum(subset) == 1
    assert minimum(subset) == 1
    assert maximum(subset) == 1
    assert supremum(subset) == 1

    subset = r"{1, 3}"
    assert infimum(subset) == 1
    assert minimum(subset) == 1
    assert maximum(subset) == 3
    assert supremum(subset) == 3

    subset = r"[-10, 10]"
    assert infimum(subset) == -10
    assert minimum(subset) == -10
    assert maximum(subset) == 10
    assert supremum(subset) == 10

    subset = r"(-10, 10]"
    assert infimum(subset) == -10
    assert minimum(subset) is None
    assert maximum(subset) == 10
    assert supremum(subset) == 10

    subset = r"[-10, 10)"
    assert infimum(subset) == -10
    assert minimum(subset) == -10
    assert maximum(subset) is None
    assert supremum(subset) == 10

    subset = r"(-10, 10)"
    assert infimum(subset) == -10
    assert minimum(subset) is None
    assert maximum(subset) is None
    assert supremum(subset) == 10
