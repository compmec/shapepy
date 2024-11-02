"""

"""

import pytest

from shapepy.core import Empty, Whole
from shapepy.primitive import Primitive
from shapepy.shape import ConnectedShape, DisjointShape


@pytest.mark.order(30)
@pytest.mark.dependency(
    depends=[
        "tests/test_empty_whole.py::test_end",
        "tests/test_primitive.py::test_end",
        "tests/test_shape.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestSimple:
    @pytest.mark.order(30)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestSimple::test_begin"])
    def test_or(self):
        empty = Empty()
        whole = Whole()
        shape = Primitive.square(2)

        assert empty | shape == shape
        assert whole | shape is whole
        assert shape | whole is whole
        assert shape | empty == shape

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestSimple::test_begin"])
    def test_and(self):
        empty = Empty()
        whole = Whole()
        shape = Primitive.square(2)

        assert empty & shape is empty
        assert whole & shape == shape
        assert shape & whole == shape
        assert shape & empty is empty

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestSimple::test_begin",
            "TestSimple::test_or",
            "TestSimple::test_and",
        ]
    )
    def test_sub(self):
        empty = Empty()
        whole = Whole()
        shape = Primitive.square(2)

        assert empty - shape is empty
        assert whole - shape == ~shape
        assert shape - whole is empty
        assert shape - empty == shape

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestSimple::test_begin",
            "TestSimple::test_or",
            "TestSimple::test_and",
        ]
    )
    def test_xor(self):
        empty = Empty()
        whole = Whole()
        shape = Primitive.square(2)

        assert empty ^ shape == shape
        assert whole ^ shape == ~shape
        assert shape ^ whole == ~shape
        assert shape ^ empty == shape

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestSimple::test_begin",
            "TestSimple::test_or",
            "TestSimple::test_and",
            "TestSimple::test_sub",
            "TestSimple::test_xor",
        ]
    )
    def test_end(self):
        pass


class TestConnected:
    @pytest.mark.order(30)
    @pytest.mark.dependency(depends=["test_begin", "TestSimple::test_end"])
    def test_begin(self):
        pass

    @staticmethod
    def create_connected():
        bigsquare = Primitive.square(4)
        smasquare = Primitive.square(2)
        shape = ConnectedShape([bigsquare, ~smasquare])
        return shape

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestConnected::test_begin"])
    def test_or(self):
        empty = Empty()
        whole = Whole()
        shape = TestConnected.create_connected()

        assert empty | shape == shape
        assert whole | shape is whole
        assert shape | whole is whole
        assert shape | empty == shape

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestConnected::test_begin"])
    def test_and(self):
        empty = Empty()
        whole = Whole()
        shape = TestConnected.create_connected()

        assert empty & shape is empty
        assert whole & shape == shape
        assert shape & whole == shape
        assert shape & empty is empty

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestConnected::test_begin",
            "TestConnected::test_or",
            "TestConnected::test_and",
        ]
    )
    def test_sub(self):
        empty = Empty()
        whole = Whole()
        shape = TestConnected.create_connected()

        assert empty - shape is empty
        assert whole - shape == ~shape
        assert shape - whole is empty
        assert shape - empty == shape

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestConnected::test_begin",
            "TestConnected::test_or",
            "TestConnected::test_and",
        ]
    )
    def test_xor(self):
        empty = Empty()
        whole = Whole()
        shape = TestConnected.create_connected()

        assert empty ^ shape == shape
        assert whole ^ shape == ~shape
        assert shape ^ whole == ~shape
        assert shape ^ empty == shape

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestConnected::test_begin",
            "TestConnected::test_or",
            "TestConnected::test_and",
            "TestConnected::test_sub",
            "TestConnected::test_xor",
        ]
    )
    def test_end(self):
        pass


class TestDisjoint:
    @pytest.mark.order(30)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestSimple::test_end",
            "TestConnected::test_end",
        ]
    )
    def test_begin(self):
        pass

    @staticmethod
    def create_connected():
        bigsquare = Primitive.square(4)
        smasquare = Primitive.square(2)
        shape = ConnectedShape([bigsquare, ~smasquare])
        return shape

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestDisjoint::test_begin"])
    def test_or(self):
        empty = Empty()
        whole = Whole()
        shape = TestDisjoint.create_connected()

        assert empty | shape == shape
        assert whole | shape is whole
        assert shape | whole is whole
        assert shape | empty == shape

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestDisjoint::test_begin"])
    def test_and(self):
        empty = Empty()
        whole = Whole()
        shape = TestDisjoint.create_connected()

        assert empty & shape is empty
        assert whole & shape == shape
        assert shape & whole == shape
        assert shape & empty is empty

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestDisjoint::test_begin",
            "TestDisjoint::test_or",
            "TestDisjoint::test_and",
        ]
    )
    def test_sub(self):
        empty = Empty()
        whole = Whole()
        shape = TestDisjoint.create_connected()

        assert empty - shape is empty
        assert whole - shape == ~shape
        assert shape - whole is empty
        assert shape - empty == shape

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestDisjoint::test_begin",
            "TestDisjoint::test_or",
            "TestDisjoint::test_and",
        ]
    )
    def test_xor(self):
        empty = Empty()
        whole = Whole()
        shape = TestDisjoint.create_connected()

        assert empty ^ shape == shape
        assert whole ^ shape == ~shape
        assert shape ^ whole == ~shape
        assert shape ^ empty == shape

    @pytest.mark.order(30)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestDisjoint::test_begin",
            "TestDisjoint::test_or",
            "TestDisjoint::test_and",
            "TestDisjoint::test_sub",
            "TestDisjoint::test_xor",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(30)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "TestSimple::test_end",
        "TestConnected::test_end",
        "TestDisjoint::test_end",
    ]
)
def test_end():
    pass
