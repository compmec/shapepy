import pytest

from shapepy.bool2d.base import EmptyR2, WholeR2
from shapepy.bool2d.converter import from_any


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_from_string():
    assert from_any(r"{}") == EmptyR2()


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_from_set():
    assert from_any(set()) == EmptyR2()


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency()
def test_from_dict():
    assert from_any({}) == EmptyR2()


@pytest.mark.order(25)
@pytest.mark.timeout(1)
@pytest.mark.dependency(
    depends=[
        "test_from_string",
        "test_from_set",
        "test_from_dict",
    ]
)
def test_all():
    pass
