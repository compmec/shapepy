"""
Tests related to 'EmptyShape' and 'WholeShape' which describes a empty set
and the whole domain
"""

from copy import copy

import pytest

from shapepy.bool2d.base import EmptyShape, WholeShape
from shapepy.bool2d.primitive import Primitive


@pytest.mark.order(24)
@pytest.mark.dependency(
    depends=[
        "tests/bool2d/test_primitive.py::test_end",
        "tests/bool2d/test_contains.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestBoolean:
    """
    Test boolean with special cases, a empty shape and whole domain
    """

    @pytest.mark.order(24)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(24)
    @pytest.mark.dependency(depends=["TestBoolean::test_begin"])
    def test_or(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty | empty is empty
        assert empty | whole is whole
        assert whole | empty is whole
        assert whole | whole is whole

        assert empty + empty is empty
        assert empty + whole is whole
        assert whole + empty is whole
        assert whole + whole is whole

    @pytest.mark.order(24)
    @pytest.mark.dependency(depends=["TestBoolean::test_begin"])
    def test_and(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty & empty is empty
        assert empty & whole is empty
        assert whole & empty is empty
        assert whole & whole is whole

        assert empty * empty is empty
        assert empty * whole is empty
        assert whole * empty is empty
        assert whole * whole is whole

    @pytest.mark.order(24)
    @pytest.mark.dependency(depends=["TestBoolean::test_begin"])
    def test_xor(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty ^ empty is empty
        assert empty ^ whole is whole
        assert whole ^ empty is whole
        assert whole ^ whole is empty

    @pytest.mark.order(24)
    @pytest.mark.dependency(depends=["TestBoolean::test_begin"])
    def test_sub(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty - empty is empty
        assert empty - whole is empty
        assert whole - empty is whole
        assert whole - whole is empty

    @pytest.mark.order(24)
    @pytest.mark.dependency(depends=["TestBoolean::test_begin"])
    def test_bool(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert bool(empty) is False
        assert bool(whole) is True

    @pytest.mark.order(24)
    @pytest.mark.dependency(depends=["TestBoolean::test_begin"])
    def test_float(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert float(empty) == float(0)
        assert float(whole) == float("inf")

    @pytest.mark.order(24)
    @pytest.mark.dependency(depends=["TestBoolean::test_begin"])
    def test_invert(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert ~empty is whole
        assert ~whole is empty
        assert ~(~empty) is empty
        assert ~(~whole) is whole

    @pytest.mark.order(24)
    @pytest.mark.dependency(depends=["TestBoolean::test_begin"])
    def test_copy(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert copy(empty) is empty
        assert copy(whole) is whole

    @pytest.mark.order(24)
    @pytest.mark.dependency(
        depends=[
            "TestBoolean::test_begin",
            "TestBoolean::test_or",
            "TestBoolean::test_and",
            "TestBoolean::test_xor",
            "TestBoolean::test_sub",
            "TestBoolean::test_bool",
            "TestBoolean::test_float",
            "TestBoolean::test_invert",
            "TestBoolean::test_copy",
        ]
    )
    def test_end(self):
        pass


class TestBoolShape:
    @pytest.mark.order(24)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestBoolean::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(24)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestBoolShape::test_begin"])
    def test_simple(self):
        empty = EmptyShape()
        whole = WholeShape()
        vertices = [(0, 0), (1, 0), (0, 1)]
        shape = Primitive.polygon(vertices)
        assert float(shape) > 0

        # OR
        assert shape | empty == shape
        assert shape | whole is whole
        assert empty | shape == shape
        assert whole | shape is whole

        # AND
        assert shape & empty is empty
        assert shape & whole == shape
        assert empty & shape is empty
        assert whole & shape == shape

        # XOR
        assert shape ^ empty == shape
        assert shape ^ whole == ~shape
        assert empty ^ shape == shape
        assert whole ^ shape == ~shape

        # SUB
        assert shape - empty == shape
        assert shape - whole is empty
        assert empty - shape is empty
        assert whole - shape == ~shape

    @pytest.mark.order(24)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestBoolShape::test_begin"])
    def test_connected(self):
        empty = EmptyShape()
        whole = WholeShape()
        vertices = [(0, 0), (0, 1), (1, 0)]
        shape = Primitive.polygon(vertices)
        assert float(shape) < 0
        assert shape | empty == shape
        assert shape | whole is whole

        # OR
        assert shape | empty == shape
        assert shape | whole is whole
        assert empty | shape == shape
        assert whole | shape is whole

        # AND
        assert shape & empty is empty
        assert shape & whole == shape
        assert empty & shape is empty
        assert whole & shape == shape

        # XOR
        assert shape ^ empty == shape
        assert shape ^ whole == ~shape
        assert empty ^ shape == shape
        assert whole ^ shape == ~shape

        # SUB
        assert shape - empty == shape
        assert shape - whole is empty
        assert empty - shape is empty
        assert whole - shape == ~shape

    @pytest.mark.order(24)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestBoolShape::test_begin"])
    def test_disjoint(self):
        pass

    @pytest.mark.order(24)
    @pytest.mark.dependency(
        depends=[
            "TestBoolShape::test_begin",
            "TestBoolShape::test_simple",
            "TestBoolShape::test_connected",
            "TestBoolShape::test_disjoint",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(24)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "TestBoolean::test_end",
        "TestBoolShape::test_end",
    ]
)
def test_end():
    pass
