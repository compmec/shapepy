"""
Tests related to 'EmptyShape' and 'WholeShape' which describes a empty set
and the whole domain
"""

from copy import copy, deepcopy

import pytest

from shapepy import lebesgue_density, move, rotate, scale
from shapepy.bool2d.base import EmptyShape, WholeShape
from shapepy.bool2d.primitive import Primitive
from shapepy.geometry.point import polar
from shapepy.scalar.angle import Angle


@pytest.mark.order(21)
@pytest.mark.dependency(
    depends=[
        "tests/geometry/test_integral.py::test_all",
        "tests/geometry/test_jordan_curve.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(21)
@pytest.mark.dependency(depends=["test_begin"])
def test_singleton():
    assert EmptyShape() is EmptyShape()
    assert WholeShape() is WholeShape()


@pytest.mark.order(21)
@pytest.mark.dependency(depends=["test_singleton"])
def test_invert():
    empty = EmptyShape()
    whole = WholeShape()
    assert ~empty is whole
    assert ~whole is empty
    assert ~(~empty) is empty
    assert ~(~whole) is whole


@pytest.mark.order(21)
@pytest.mark.dependency(depends=["test_singleton", "test_invert"])
def test_neg():
    empty = EmptyShape()
    whole = WholeShape()
    assert -empty is whole
    assert -whole is empty
    assert -(-empty) is empty
    assert -(-whole) is whole


@pytest.mark.order(21)
@pytest.mark.dependency(depends=["test_singleton"])
def test_or():
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


@pytest.mark.order(21)
@pytest.mark.dependency(depends=["test_singleton"])
def test_and():
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


@pytest.mark.order(21)
@pytest.mark.dependency(
    depends=["test_singleton", "test_or", "test_and", "test_invert"]
)
def test_xor():
    empty = EmptyShape()
    whole = WholeShape()
    assert empty ^ empty is empty
    assert empty ^ whole is whole
    assert whole ^ empty is whole
    assert whole ^ whole is empty


@pytest.mark.order(21)
@pytest.mark.dependency(
    depends=["test_singleton", "test_or", "test_and", "test_invert"]
)
def test_sub():
    empty = EmptyShape()
    whole = WholeShape()
    assert empty - empty is empty
    assert empty - whole is empty
    assert whole - empty is whole
    assert whole - whole is empty


@pytest.mark.order(21)
@pytest.mark.dependency(depends=["test_singleton"])
def test_bool():
    empty = EmptyShape()
    whole = WholeShape()
    assert bool(empty) is False
    assert bool(whole) is True


@pytest.mark.order(21)
@pytest.mark.dependency(depends=["test_singleton"])
def test_copy():
    empty = EmptyShape()
    whole = WholeShape()
    assert copy(empty) is empty
    assert copy(whole) is whole
    assert deepcopy(empty) is empty
    assert deepcopy(whole) is whole


@pytest.mark.order(21)
@pytest.mark.dependency(depends=["test_singleton"])
def test_move():
    empty = EmptyShape()
    whole = WholeShape()
    assert empty.move((1, 0)) is empty
    assert whole.move((1, 0)) is whole

    assert move(empty, (1, 0)) is empty
    assert move(whole, (1, 0)) is whole


@pytest.mark.order(21)
@pytest.mark.dependency(depends=["test_singleton"])
def test_scale():
    empty = EmptyShape()
    whole = WholeShape()
    assert empty.scale((2, 1)) is empty
    assert whole.scale((3, 2)) is whole

    assert scale(empty, (2, 3)) is empty
    assert scale(whole, (3, 2)) is whole


@pytest.mark.order(21)
@pytest.mark.dependency(depends=["test_singleton"])
def test_rotate():
    empty = EmptyShape()
    whole = WholeShape()
    angle = Angle.degrees(30)
    assert empty.rotate(angle) is empty
    assert whole.rotate(angle) is whole

    assert rotate(empty, angle) is empty
    assert rotate(whole, angle) is whole


@pytest.mark.order(21)
@pytest.mark.dependency(depends=["test_singleton"])
def test_print():
    empty = EmptyShape()
    whole = WholeShape()

    assert str(empty) == "EmptyShape"
    assert str(whole) == "WholeShape"
    assert isinstance(repr(empty), str)
    assert isinstance(repr(whole), str)


@pytest.mark.order(21)
@pytest.mark.dependency(depends=["test_singleton"])
def test_hash():
    assert hash(EmptyShape()) == 0
    assert hash(WholeShape()) == 1


@pytest.mark.order(21)
@pytest.mark.dependency(depends=["test_singleton"])
def test_contains():
    empty = EmptyShape()
    whole = WholeShape()

    assert empty in empty
    assert empty in whole
    assert whole not in empty
    assert whole in whole


@pytest.mark.order(21)
@pytest.mark.dependency(depends=["test_singleton"])
def test_density():
    empty = EmptyShape()
    whole = WholeShape()
    for point in [(0, 0), (1, 0), (0, 1)]:
        assert empty.density(point) == 0
        assert whole.density(point) == 1
        assert lebesgue_density(empty, point) == 0
        assert lebesgue_density(whole, point) == 1

    for deg in range(0, 360, 30):
        angle = Angle.degrees(deg)
        point = polar(float("inf"), angle)
        assert empty.density(point) == 0
        assert whole.density(point) == 1
        assert lebesgue_density(empty, point) == 0
        assert lebesgue_density(whole, point) == 1


class TestBoolShape:
    @pytest.mark.order(21)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "test_singleton",
            "test_invert",
            "test_neg",
            "test_or",
            "test_and",
            "test_xor",
            "test_sub",
            "test_bool",
            "test_copy",
            "test_move",
            "test_scale",
            "test_rotate",
            "test_print",
            "test_hash",
            "test_contains",
            "test_density",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(21)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestBoolShape::test_begin"])
    def test_simple(self):
        empty = EmptyShape()
        whole = WholeShape()
        vertices = [(0, 0), (1, 0), (0, 1)]
        shape = Primitive.polygon(vertices)
        assert shape.area > 0

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

    @pytest.mark.order(21)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestBoolShape::test_begin"])
    def test_connected(self):
        empty = EmptyShape()
        whole = WholeShape()
        vertices = [(0, 0), (0, 1), (1, 0)]
        shape = Primitive.polygon(vertices)
        assert shape.area < 0
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

    @pytest.mark.order(21)
    @pytest.mark.timeout(40)
    @pytest.mark.dependency(depends=["TestBoolShape::test_begin"])
    def test_disjoint(self):
        pass

    @pytest.mark.order(21)
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


@pytest.mark.order(21)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_singleton",
        "test_invert",
        "test_neg",
        "test_or",
        "test_and",
        "test_xor",
        "test_sub",
        "test_bool",
        "test_copy",
        "test_move",
        "test_scale",
        "test_rotate",
        "test_print",
        "test_hash",
        "test_contains",
        "test_density",
        "TestBoolShape::test_end",
    ]
)
def test_end():
    pass
