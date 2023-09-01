"""
This file contains the code to test the relative position of an object with respect
to another
"""

import pytest

from compmec.shape.jordancurve import JordanCurve
from compmec.shape.primitive import Primitive
from compmec.shape.shape import (
    ConnectedShape,
    DisjointShape,
    EmptyShape,
    SimpleShape,
    WholeShape,
)


@pytest.mark.order(7)
@pytest.mark.dependency(
    depends=[
        # "tests/test_polygon.py::test_end",
        # "tests/test_jordan_polygon.py::test_end",
        # "tests/test_jordan_curve.py::test_end",
        # "tests/test_primitive.py::test_end",
        # "tests/test_calculus.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestObjectsInEmptyWhole:
    """
    Test relative to special cases, a empty shape and whole domain
    """

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestObjectsInEmptyWhole::test_begin"])
    def test_empty(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert empty in empty
        assert empty in whole

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestObjectsInEmptyWhole::test_begin"])
    def test_whole(self):
        empty = EmptyShape()
        whole = WholeShape()
        assert whole not in empty
        assert whole in whole

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestObjectsInEmptyWhole::test_begin"])
    def test_point(self):
        empty = EmptyShape()
        whole = WholeShape()
        for point in [(0, 0), (1, 1), (0, -1)]:
            assert point not in empty
            assert point in whole

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestObjectsInEmptyWhole::test_begin"])
    def test_jordan(self):
        empty = EmptyShape()
        whole = WholeShape()

        vertices = [(0, 0), (1, 0), (0, 1)]
        jordan = JordanCurve.from_vertices(vertices)
        assert jordan not in empty
        assert jordan in whole

        vertices = [(0, 0), (0, 1), (1, 0)]
        jordan = JordanCurve.from_vertices(vertices)
        assert jordan not in empty
        assert jordan in whole

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestObjectsInEmptyWhole::test_begin"])
    def test_simple_shape(self):
        empty = EmptyShape()
        whole = WholeShape()

        vertices = [(0, 0), (1, 0), (0, 1)]
        jordan = JordanCurve.from_vertices(vertices)
        shape = SimpleShape(jordan)
        assert shape not in empty
        assert shape in whole

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestObjectsInEmptyWhole::test_begin"])
    def test_connected_shape(self):
        empty = EmptyShape()
        whole = WholeShape()

        vertices = [(0, 0), (1, 0), (0, 1)]
        jordan = JordanCurve.from_vertices(vertices)
        simple = SimpleShape(jordan)
        shape = ConnectedShape(whole, [simple])
        assert shape not in empty
        assert shape in whole

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestObjectsInEmptyWhole::test_begin"])
    def test_disjoint_shape(self):
        empty = EmptyShape()
        whole = WholeShape()

        square0 = Primitive.square(center=(-3, 0))
        square1 = Primitive.square(center=(3, 0))
        shape = DisjointShape([square0, square1])
        assert shape not in empty
        assert shape in whole

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInEmptyWhole::test_begin",
            "TestObjectsInEmptyWhole::test_empty",
            "TestObjectsInEmptyWhole::test_whole",
            "TestObjectsInEmptyWhole::test_point",
            "TestObjectsInEmptyWhole::test_jordan",
            "TestObjectsInEmptyWhole::test_simple_shape",
            "TestObjectsInEmptyWhole::test_connected_shape",
            "TestObjectsInEmptyWhole::test_disjoint_shape",
        ]
    )
    def test_end(self):
        pass


class TestObjectsInJordan:
    """
    Tests the respective position
    """

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["test_begin", "TestObjectsInEmptyWhole::test_end"])
    def test_begin(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInJordan::test_begin",
        ]
    )
    def test_boundary_point(self):
        # Test if the points are in boundary
        vertices = [(0, 0), (1, 0), (0, 1)]
        triangle = JordanCurve.from_vertices(vertices)
        assert (0, 0) in triangle
        assert (1, 0) in triangle
        assert (0, 1) in triangle
        assert (0.5, 0) in triangle
        assert (0.5, 0.5) in triangle
        assert (0, 0.5) in triangle

        vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        square = JordanCurve.from_vertices(vertices)
        assert (0, 0) in square
        assert (1, 0) in square
        assert (1, 1) in square
        assert (0, 1) in square
        assert (0.5, 0) in square
        assert (1, 0.5) in square
        assert (0.5, 1) in square
        assert (0, 0.5) in square

    @pytest.mark.order(7)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInJordan::test_begin",
        ]
    )
    def test_interior_point(self):
        # Test if the points are in boundary
        vertices = [(0, 0), (3, 0), (0, 3)]
        triangle = JordanCurve.from_vertices(vertices)
        assert (1, 1) not in triangle

        vertices = [(0, 0), (2, 0), (2, 2), (0, 2)]
        square = JordanCurve.from_vertices(vertices)
        assert (1, 1) not in square

    @pytest.mark.order(7)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInJordan::test_begin",
        ]
    )
    def test_exterior_point(self):
        triangle = JordanCurve.from_vertices([(0, 0), (1, 0), (0, 1)])
        assert (-1, -1) not in triangle
        assert (1, 1) not in triangle

        square = JordanCurve.from_vertices([(0, 0), (1, 0), (1, 1), (0, 1)])
        assert (-1, -1) not in square
        assert (2, 2) not in square

    @pytest.mark.order(7)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInJordan::test_begin",
            "TestObjectsInJordan::test_boundary_point",
            "TestObjectsInJordan::test_interior_point",
            "TestObjectsInJordan::test_exterior_point",
        ]
    )
    def test_end(self):
        pass


class TestObjectsInSimple:
    """
    Tests the respective position
    """

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestObjectsInEmptyWhole::test_end",
            "TestObjectsInJordan::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestObjectsInSimple::test_begin"])
    def test_empty(self):
        empty = EmptyShape()
        square = Primitive.square()
        assert empty in square
        assert square not in empty

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestObjectsInSimple::test_begin"])
    def test_whole(self):
        whole = WholeShape()
        square = Primitive.square()
        assert whole not in square
        assert square in whole

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInSimple::test_begin",
            "TestObjectsInSimple::test_empty",
            "TestObjectsInSimple::test_whole",
        ]
    )
    def test_point(self):
        square = Primitive.square(side=4)

        # Interior points
        assert (0, 0) in square
        assert (-1, -1) in square
        assert (-1, 1) in square
        assert (1, -1) in square
        assert (1, 1) in square

        # Boundary points
        assert (-2, -2) in square
        assert (0, -2) in square
        assert (2, -2) in square
        assert (2, 0) in square
        assert (2, 2) in square
        assert (0, 2) in square
        assert (-2, 2) in square
        assert (-2, 0) in square

        # Exterior points
        assert (3, 3) not in square
        assert (-3, -3) not in square

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInSimple::test_begin",
            "TestObjectsInSimple::test_empty",
            "TestObjectsInSimple::test_whole",
            "TestObjectsInSimple::test_point",
        ]
    )
    def test_jordan(self):
        small_square = Primitive.square(side=2)
        big_square = Primitive.square(side=4)
        assert small_square.jordancurve in small_square
        assert small_square.jordancurve in big_square
        assert big_square.jordancurve not in small_square
        assert big_square.jordancurve in big_square

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInSimple::test_begin",
            "TestObjectsInSimple::test_empty",
            "TestObjectsInSimple::test_whole",
            "TestObjectsInSimple::test_point",
            "TestObjectsInSimple::test_jordan",
        ]
    )
    def test_simple(self):
        big_square = Primitive.square(side=4)
        small_square = Primitive.square(side=2)
        assert small_square in big_square
        assert big_square not in small_square

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInSimple::test_begin",
            "TestObjectsInSimple::test_empty",
            "TestObjectsInSimple::test_whole",
            "TestObjectsInSimple::test_point",
            "TestObjectsInSimple::test_jordan",
            "TestObjectsInSimple::test_simple",
        ]
    )
    def test_connected(self):
        square = Primitive.square(side=4)
        inv_square = ~square
        assert inv_square not in square
        # assert square not in inv_square

        big_square = Primitive.square(side=4)
        small_square = Primitive.square(side=2)
        invsmall_square = ~small_square
        assert invsmall_square not in big_square
        # assert big_square not in invsmall_square

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInSimple::test_begin",
            "TestObjectsInSimple::test_empty",
            "TestObjectsInSimple::test_whole",
            "TestObjectsInSimple::test_point",
            "TestObjectsInSimple::test_jordan",
            "TestObjectsInSimple::test_simple",
            "TestObjectsInSimple::test_connected",
        ]
    )
    def test_disjoint(self):
        square_left = Primitive.square(side=2, center=(-3, 0))
        square_right = Primitive.square(side=2, center=(3, 0))
        disj_shape = DisjointShape([square_left, square_right])

        square = Primitive.square(side=1, center=(-3, 0))
        assert square in square_left
        assert square not in square_right
        # assert square in disj_shape
        assert disj_shape not in square

        square = Primitive.square(side=1, center=(3, 0))
        assert square not in square_left
        assert square in square_right
        # assert square in disj_shape
        assert disj_shape not in square

        square = Primitive.square(side=9, center=(0, 0))
        assert disj_shape in square
        square = Primitive.square(side=8, center=(0, 0))
        assert disj_shape in square  # touchs boundary
        square = Primitive.square(side=7, center=(0, 0))
        assert disj_shape not in square

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInSimple::test_begin",
            "TestObjectsInSimple::test_empty",
            "TestObjectsInSimple::test_whole",
            "TestObjectsInSimple::test_point",
            "TestObjectsInSimple::test_jordan",
            "TestObjectsInSimple::test_simple",
            "TestObjectsInSimple::test_connected",
            "TestObjectsInSimple::test_disjoint",
        ]
    )
    def test_end(self):
        pass


class TestObjectsInConnected:
    """
    Tests the respective position
    """

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestObjectsInEmptyWhole::test_end",
            "TestObjectsInJordan::test_end",
            "TestObjectsInSimple::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestObjectsInConnected::test_begin"])
    def test_empty(self):
        empty = EmptyShape()
        square = ~Primitive.square()
        assert empty in square
        assert square not in empty

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestObjectsInConnected::test_begin"])
    def test_whole(self):
        whole = WholeShape()
        square = ~Primitive.square()
        assert whole not in square
        assert square in whole

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInConnected::test_begin",
            "TestObjectsInConnected::test_empty",
            "TestObjectsInConnected::test_whole",
        ]
    )
    def test_point(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInConnected::test_begin",
            "TestObjectsInConnected::test_empty",
            "TestObjectsInConnected::test_whole",
            "TestObjectsInConnected::test_point",
        ]
    )
    def test_jordan(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInConnected::test_begin",
            "TestObjectsInConnected::test_empty",
            "TestObjectsInConnected::test_whole",
            "TestObjectsInConnected::test_point",
            "TestObjectsInConnected::test_jordan",
        ]
    )
    def test_simple(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInConnected::test_begin",
            "TestObjectsInConnected::test_empty",
            "TestObjectsInConnected::test_whole",
            "TestObjectsInConnected::test_point",
            "TestObjectsInConnected::test_jordan",
            "TestObjectsInConnected::test_simple",
        ]
    )
    def test_connected(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInConnected::test_begin",
            "TestObjectsInConnected::test_empty",
            "TestObjectsInConnected::test_whole",
            "TestObjectsInConnected::test_point",
            "TestObjectsInConnected::test_jordan",
            "TestObjectsInConnected::test_simple",
            "TestObjectsInConnected::test_connected",
        ]
    )
    def test_disjoint(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInConnected::test_begin",
            "TestObjectsInConnected::test_empty",
            "TestObjectsInConnected::test_whole",
            "TestObjectsInConnected::test_point",
            "TestObjectsInConnected::test_jordan",
            "TestObjectsInConnected::test_simple",
            "TestObjectsInConnected::test_connected",
            "TestObjectsInConnected::test_disjoint",
        ]
    )
    def test_end(self):
        pass


class TestObjectsInDisjoint:
    """
    Tests the respective position
    """

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestObjectsInEmptyWhole::test_end",
            "TestObjectsInJordan::test_end",
            "TestObjectsInSimple::test_end",
            "TestObjectsInConnected::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestObjectsInDisjoint::test_begin"])
    def test_empty(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(depends=["TestObjectsInDisjoint::test_begin"])
    def test_whole(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInDisjoint::test_begin",
            "TestObjectsInDisjoint::test_empty",
            "TestObjectsInDisjoint::test_whole",
        ]
    )
    def test_point(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInDisjoint::test_begin",
            "TestObjectsInDisjoint::test_empty",
            "TestObjectsInDisjoint::test_whole",
            "TestObjectsInDisjoint::test_point",
        ]
    )
    def test_jordan(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInDisjoint::test_begin",
            "TestObjectsInDisjoint::test_empty",
            "TestObjectsInDisjoint::test_whole",
            "TestObjectsInDisjoint::test_point",
            "TestObjectsInDisjoint::test_jordan",
        ]
    )
    def test_simple(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInDisjoint::test_begin",
            "TestObjectsInDisjoint::test_empty",
            "TestObjectsInDisjoint::test_whole",
            "TestObjectsInDisjoint::test_point",
            "TestObjectsInDisjoint::test_jordan",
            "TestObjectsInDisjoint::test_simple",
        ]
    )
    def test_connected(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInDisjoint::test_begin",
            "TestObjectsInDisjoint::test_empty",
            "TestObjectsInDisjoint::test_whole",
            "TestObjectsInDisjoint::test_point",
            "TestObjectsInDisjoint::test_jordan",
            "TestObjectsInDisjoint::test_simple",
            "TestObjectsInDisjoint::test_connected",
        ]
    )
    def test_disjoint(self):
        pass

    @pytest.mark.order(7)
    @pytest.mark.dependency(
        depends=[
            "TestObjectsInDisjoint::test_begin",
            "TestObjectsInDisjoint::test_empty",
            "TestObjectsInDisjoint::test_whole",
            "TestObjectsInDisjoint::test_point",
            "TestObjectsInDisjoint::test_jordan",
            "TestObjectsInDisjoint::test_simple",
            "TestObjectsInDisjoint::test_connected",
            "TestObjectsInDisjoint::test_disjoint",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(7)
@pytest.mark.dependency(
    depends=[
        "TestObjectsInEmptyWhole::test_end",
        "TestObjectsInJordan::test_end",
        "TestObjectsInSimple::test_end",
        "TestObjectsInConnected::test_end",
        "TestObjectsInDisjoint::test_end",
    ]
)
def test_end():
    pass
