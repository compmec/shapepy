"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""

from __future__ import annotations

import abc
from copy import copy
from typing import Optional, Tuple, Union

import numpy as np
import rbool

from ..geometry.box import Box
from ..geometry.integral import IntegrateJordan
from ..geometry.jordancurve import JordanCurve
from ..geometry.point import Point2D
from ..scalar.reals import Real
from ..tools import Is, To
from .base import EmptyShape, SubSetR2


# pylint: disable=no-member
class DefinedShape(SubSetR2):
    """
    DefinedShape is the base class for SimpleShape,
    ConnectedShape and DisjointShape

    """

    def __copy__(self) -> DefinedShape:
        return self.__deepcopy__(None)

    def box(self) -> Box:
        """
        Box that encloses all jordan curves

        Parameters
        ----------

        :return: The box that encloses all
        :rtype: Box


        Example use
        -----------
        >>> from shapepy import Primitive, IntegrateShape
        >>> circle = Primitive.circle(radius = 1)
        >>> circle.box()
        Box with vertices (-1.0, -1.0) and (1., 1.0)

        """
        box = None
        for jordan in self.jordans:
            box |= jordan.box()
        return box

    def __contains__(
        self, other: Union[Point2D, JordanCurve, SubSetR2]
    ) -> bool:
        if Is.instance(other, DefinedShape):
            return self.contains_shape(other)
        if Is.instance(other, SubSetR2):
            return Is.instance(other, EmptyShape)
        if Is.instance(other, JordanCurve):
            return self.contains_jordan(other)
        point = To.point(other)
        return self.contains_point(point)

    def move(self, point: Point2D) -> SubSetR2:
        """
        Moves/translate entire shape by an amount

        Parameters
        ----------

        point : Point2D
            The amount to move

        :return: The same instance
        :rtype: SubSetR2

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()
        >>> circle.move(1, 2)

        """
        point = To.point(point)
        for jordan in self.jordans:
            jordan.move(point)
        return self

    def scale(self, xscale: float, yscale: float) -> SubSetR2:
        """
        Scales entire shape by an amount

        Parameters
        ----------

        xscale : float
            The amount to scale in horizontal direction
        yscale : float
            The amount to scale in vertical direction

        :return: The same instance
        :rtype: SubSetR2

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()
        >>> circle.scale(2, 3)

        """
        for jordan in self.jordans:
            jordan.scale(xscale, yscale)
        return self

    def rotate(self, angle: float, degrees: bool = False) -> SubSetR2:
        """
        Rotates entire shape around the origin by an amount

        Parameters
        ----------

        angle : float
            The amount to rotate around origin
        degrees : bool, default = False
            Flag to indicate if ``angle`` is in radians or degrees

        :return: The same instance
        :rtype: SubSetR2

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()
        >>> circle.rotate(angle = 90, degrees = True)

        """
        for jordan in self.jordans:
            jordan.rotate(angle, degrees)
        return self

    def contains_point(
        self, point: Point2D, boundary: Optional[bool] = True
    ) -> bool:
        """
        Checks if given point is inside the shape

        Parameters
        ----------

        point : Point2D
            The point to verify if is inside
        boundary : bool, default = True
            The flag to decide if a boundary point is considered
            inside or outside.
            If ``True``, then a boundary point is considered inside.

        :return: Whether the point is inside or not
        :rtype: bool


        Example use
        -----------
        >>> from shapepy import Primitive
        >>> square = Primitive.square()
        >>> square.contains_point((0, 0))
        True
        >>> square.contains_point((0.5, 0), True)
        True
        >>> square.contains_point((0.5, 0), False)
        False

        """
        point = To.point(point)
        assert Is.bool(boundary)
        return self._contains_point(point, boundary)

    def contains_jordan(
        self, jordan: JordanCurve, boundary: Optional[bool] = True
    ) -> bool:
        """
        Checks if the all points of jordan are inside the shape

        Parameters
        ----------

        jordan : JordanCurve
            The jordan curve to verify
        boundary : bool, default = True
            The flag to check if jordan is inside a closed (True)
            or open (False) set

        :return: Whether the jordan is inside or not
        :rtype: bool


        Example use
        -----------
        >>> from shapepy import Primitive
        >>> square = Primitive.square()
        >>> jordan = small_square.jordans[0]
        >>> square.contains_jordan(jordan)
        True

        """
        assert Is.jordan(jordan)
        assert Is.bool(boundary)
        return self._contains_jordan(jordan, boundary)

    def contains_shape(self, other: SubSetR2) -> bool:
        """
        Checks if the all points of given shape are inside the shape

        Mathematically speaking, checks if ``other`` is a subset of ``self``

        Parameters
        ----------

        other : SubSetR2
            The shape to be verified if is inside

        :return: Whether the ``other`` shape is inside or not
        :rtype: bool

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> square = Primitive.regular_polygon(4)
        >>> circle = Primitive.circle()
        >>> circle.contains_shape(square)
        True

        """
        assert Is.instance(other, DefinedShape)
        return self._contains_shape(other)

    @abc.abstractmethod
    def _contains_point(self, point: Point2D, boundary: Optional[bool] = True):
        pass

    @abc.abstractmethod
    def _contains_jordan(
        self, jordan: JordanCurve, boundary: Optional[bool] = True
    ):
        pass

    @abc.abstractmethod
    def _contains_shape(self, other: SubSetR2):
        pass


class SimpleShape(DefinedShape):
    """
    SimpleShape class

    Is a shape which is defined by only one jordan curve.
    It represents the interior/exterior region of the jordan curve
    if the jordan curve is counter-clockwise/clockwise

    """

    def __init__(self, jordancurve: JordanCurve):
        assert Is.jordan(jordancurve)
        self.__jordancurve = jordancurve

    def __deepcopy__(self, memo) -> DefinedShape:
        return SimpleShape(copy(self.__jordancurve))

    def __str__(self) -> str:
        area = float(self.area)
        vertices = tuple(map(tuple, self.jordans[0].vertices))
        vertices = np.array(vertices, dtype="float64")
        return f"Simple Shape of area {area:.2f} with vertices:\n{vertices}"

    def __repr__(self) -> str:
        area, vertices = float(self.area), self.jordans[0].vertices
        msg = f"Simple shape of area {area:.2f} with {len(vertices)} vertices"
        return msg

    def __eq__(self, other: SubSetR2) -> bool:
        """Compare two shapes

        Parameters
        ----------
        other: SubSetR2
            The shape to compare

        :raises ValueError: If ``other`` is not a SubSetR2 instance
        """
        if not Is.instance(other, SubSetR2):
            raise ValueError
        return (
            Is.instance(other, SimpleShape)
            and self.area == other.area
            and self.__jordancurve == other.jordans[0]
        )

    def __invert__(self) -> SimpleShape:
        return self.__class__(~self.__jordancurve)

    @property
    def area(self) -> Real:
        """The internal area that is enclosed by the shape"""
        return self.__jordancurve.area

    @property
    def jordans(self) -> Tuple[JordanCurve]:
        """
        The jordans curve that define the SimpleShape

        It has only one jordan curve inside it
        """
        return (self.__jordancurve,)

    def invert(self) -> SimpleShape:
        """
        Inverts the region of simple shape.

        Parameters
        ----------

        :return: The same instance
        :rtype: SimpleShape

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> square = Primitive.square()
        >>> print(square)
        Simple Shape of area 1.00 with vertices:
        [[ 0.5  0.5]
        [-0.5  0.5]
        [-0.5 -0.5]
        [ 0.5 -0.5]]
        >>> square.invert()
        Simple Shape of area -1.00 with vertices:
        [[ 0.5  0.5]
        [ 0.5 -0.5]
        [-0.5 -0.5]
        [-0.5  0.5]]

        """
        self.__jordancurve.invert()
        return self

    def _contains_point(
        self, point: Point2D, boundary: Optional[bool] = True
    ) -> bool:
        jordan = self.jordans[0]
        wind = IntegrateJordan.winding_number(jordan, center=point)
        return (
            (wind > 0 if boundary else wind == 1)
            if jordan.area > 0
            else wind > -1 if boundary else wind == 0
        )

    def _contains_jordan(
        self, jordan: JordanCurve, boundary: Optional[bool] = True
    ) -> bool:
        piecewise = jordan.piecewise
        vertices = map(piecewise, piecewise.knots)
        if not all(map(self.contains_point, vertices)):
            return False
        inters = piecewise & self.jordans[0]
        inters.evaluate()
        if inters.all_subsets[id(piecewise)] is not rbool.Empty():
            return True
        knots = sorted(inters.all_knots[id(jordan.piecewise)])
        midknots = ((k0 + k1) / 2 for k0, k1 in zip(knots, knots[1:]))
        midpoints = map(piecewise, midknots)
        return all(map(self.contains_point, midpoints))

    def _contains_shape(self, other: DefinedShape) -> bool:
        assert Is.instance(other, DefinedShape)
        if Is.instance(other, SimpleShape):
            return self.__contains_simple(other)
        if Is.instance(other, ConnectedShape):
            # cap S_i in S_j = any_i (bar S_j in bar S_i)
            contains = False
            self.invert()
            for subshape in other.subshapes:
                subshape.invert()
                if self in subshape:
                    contains = True
                subshape.invert()
                if contains:
                    break
            self.invert()
            return contains
        # Disjoint shape
        for subshape in other.subshapes:
            if subshape not in self:
                return False
        return True

    # pylint: disable=chained-comparison
    def __contains_simple(self, other: SimpleShape) -> bool:
        assert Is.instance(other, SimpleShape)
        areaa = other.area
        areab = self.area
        jordana = other.jordans[0]
        jordanb = self.jordans[0]
        if areaa < 0 and areab > 0:
            return False
        if not self.box() & other.box():
            return areaa > 0 and areab < 0
        if areaa > 0 and areab < 0:
            return jordana in self and jordanb not in other
        if areaa > areab or jordana not in self:
            return False
        if areaa > 0:
            return True
        # If simple shape is not a square
        # may happens error here
        return True


class ConnectedShape(DefinedShape):
    """
    ConnectedShape Class

    A shape defined by intersection of two or more SimpleShapes

    """

    def __init__(self, subshapes: Tuple[SimpleShape]):
        self.subshapes = subshapes

    def __deepcopy__(self, memo):
        simples = tuple(map(copy, self.subshapes))
        return ConnectedShape(simples)

    @property
    def area(self) -> Real:
        """The internal area that is enclosed by the shape"""
        return sum(simple.area for simple in self.subshapes)

    def __str__(self) -> str:
        return f"Connected shape total area {self.area}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: SubSetR2) -> bool:
        assert Is.instance(other, SubSetR2)
        return (
            Is.instance(other, ConnectedShape)
            and abs(self.area - other.area) < 1e-6
        )

    def __invert__(self) -> DisjointShape:
        simples = [~simple for simple in self.subshapes]
        return DisjointShape(simples)

    @property
    def jordans(self) -> Tuple[JordanCurve]:
        """Jordan curves that defines the shape

        :getter: Returns a set of jordan curves
        :type: tuple[JordanCurve]
        """
        return tuple(shape.jordans[0] for shape in self.subshapes)

    @property
    def subshapes(self) -> Tuple[SimpleShape]:
        """
        Subshapes that defines the connected shape

        :getter: Subshapes that defines connected shape
        :setter: Subshapes that defines connected shape
        :type: tuple[SimpleShape]

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> big_square = Primitive.square(side = 2)
        >>> small_square = Primitive.square(side = 1)
        >>> shape = big_square - small_square
        >>> for subshape in shape.subshapes:
                print(subshape)
        Simple Shape of area 4.00 with vertices:
        [[ 1.  1.]
        [-1.  1.]
        [-1. -1.]
        [ 1. -1.]]
        Simple Shape of area -1.00 with vertices:
        [[ 0.5  0.5]
        [ 0.5 -0.5]
        [-0.5 -0.5]
        [-0.5  0.5]]

        """
        return self.__subshapes

    @subshapes.setter
    def subshapes(self, simples: Tuple[SimpleShape]):
        if not all(Is.instance(simple, SimpleShape) for simple in simples):
            raise TypeError
        areas = (simple.area for simple in simples)

        def algori(pair):
            return pair[0]

        simples = sorted(zip(areas, simples), key=algori, reverse=True)
        simples = tuple(val[1] for val in simples)
        self.__subshapes = tuple(simples)

    def _contains_point(
        self, point: Point2D, boundary: Optional[bool] = True
    ) -> bool:
        for subshape in self.subshapes:
            if not subshape.contains_point(point, boundary):
                return False
        return True

    def _contains_jordan(
        self, jordan: JordanCurve, boundary: Optional[bool] = True
    ) -> bool:
        for subshape in self.subshapes:
            if not subshape.contains_jordan(jordan, boundary):
                return False
        return True

    def _contains_shape(self, other: DefinedShape) -> bool:
        for subshape in self.subshapes:
            if not subshape.contains_shape(other):
                return False
        return True


class DisjointShape(DefinedShape):
    """
    DisjointShape Class

    A shape defined by the union of some SimpleShape instances and
    ConnectedShape instances
    """

    def __new__(cls, subshapes: Tuple[ConnectedShape]):
        subshapes = list(subshapes)
        while EmptyShape() in subshapes:
            subshapes.remove(EmptyShape())
        if len(subshapes) == 0:
            return EmptyShape()
        for subshape in subshapes:
            assert Is.instance(subshape, (SimpleShape, ConnectedShape))
        if len(subshapes) == 1:
            return copy(subshapes[0])
        instance = super(DisjointShape, cls).__new__(cls)
        instance.subshapes = subshapes
        return instance

    def __init__(self, _: Tuple[ConnectedShape]):
        pass

    def __deepcopy__(self, memo):
        subshapes = tuple(map(copy, self.subshapes))
        return DisjointShape(subshapes)

    def __invert__(self):
        new_jordans = tuple(~jordan for jordan in self.jordans)
        return shape_from_jordans(new_jordans)

    @property
    def area(self) -> Real:
        """The internal area that is enclosed by the shape"""
        return sum(sub.area for sub in self.subshapes)

    def __eq__(self, other: SubSetR2):
        assert Is.instance(other, SubSetR2)
        if not Is.instance(other, DisjointShape):
            return False
        if self.area != other.area:
            return False
        self_subshapes = list(self.subshapes)
        othe_subshapes = list(other.subshapes)
        # Compare if a curve is inside another
        while len(self_subshapes) != 0 and len(othe_subshapes) != 0:
            for j, osbshape in enumerate(othe_subshapes):
                if osbshape == self_subshapes[0]:
                    self_subshapes.pop(0)
                    othe_subshapes.pop(j)
                    break
            else:
                return False
        return not (len(self_subshapes) or len(othe_subshapes))

    def __str__(self) -> str:
        msg = f"Disjoint shape with total area {self.area} and "
        msg += f"{len(self.subshapes)} subshapes"
        return msg

    def __repr__(self) -> str:
        return self.__str__()

    def _contains_point(
        self, point: Point2D, boundary: Optional[bool] = True
    ) -> bool:
        for subshape in self.subshapes:
            if subshape.contains_point(point, boundary):
                return True
        return False

    def _contains_jordan(
        self, jordan: JordanCurve, boundary: Optional[bool] = True
    ) -> bool:
        for subshape in self.subshapes:
            if subshape.contains_jordan(jordan, boundary):
                return True
        return False

    def _contains_shape(self, other: DefinedShape) -> bool:
        assert Is.instance(other, DefinedShape)
        if Is.instance(other, (SimpleShape, ConnectedShape)):
            for subshape in self.subshapes:
                if other in subshape:
                    return True
            return False
        if Is.instance(other, DisjointShape):
            for subshape in other.subshapes:
                if subshape not in self:
                    return False
            return True
        raise NotImplementedError

    @property
    def jordans(self) -> Tuple[JordanCurve]:
        """Jordan curves that defines the shape

        :getter: Returns a set of jordan curves
        :type: tuple[JordanCurve]
        """
        lista = []
        for subshape in self.subshapes:
            lista += list(subshape.jordans)
        return tuple(lista)

    @property
    def subshapes(self) -> Tuple[Union[SimpleShape, ConnectedShape]]:
        """
        Subshapes that defines the disjoint shape

        :getter: Subshapes that defines disjoint shape
        :setter: Subshapes that defines disjoint shape
        :type: tuple[SimpleShape | ConnectedShape]

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> left = Primitive.square(center=(-2, 0))
        >>> right = Primitive.square(center = (2, 0))
        >>> shape = left | right
        >>> for subshape in shape.subshapes:
                print(subshape)
        Simple Shape of area 1.00 with vertices:
        [[-1.5  0.5]
        [-2.5  0.5]
        [-2.5 -0.5]
        [-1.5 -0.5]]
        Simple Shape of area 1.00 with vertices:
        [[ 2.5  0.5]
        [ 1.5  0.5]
        [ 1.5 -0.5]
        [ 2.5 -0.5]]

        """
        return self.__subshapes

    @subshapes.setter
    def subshapes(self, values: Tuple[SubSetR2]):
        if not all(
            Is.instance(sub, (SimpleShape, ConnectedShape)) for sub in values
        ):
            raise ValueError
        areas = tuple(sub.area for sub in values)
        lenghts = tuple(sub.jordans[0].length for sub in values)

        def algori(triple):
            return triple[:2]

        values = sorted(zip(areas, lenghts, values), key=algori, reverse=True)
        values = tuple(val[2] for val in values)
        self.__subshapes = tuple(values)


def divide_connecteds(
    simples: Tuple[SimpleShape],
) -> Tuple[Union[SimpleShape, ConnectedShape]]:
    """
    Divides the simples in groups of connected shapes

    The idea is get the simple shape with maximum abs area,
    this is the biggest shape of all we start from it.

    We them separate all shapes in inside and outside
    """
    if len(simples) == 0:
        return tuple()
    externals = []
    connected = []
    simples = list(simples)
    while len(simples) != 0:
        areas = (s.area for s in simples)
        absareas = tuple(map(abs, areas))
        index = absareas.index(max(absareas))
        connected.append(simples.pop(index))
        internal = []
        while len(simples) != 0:  # Divide in two groups
            simple = simples.pop(0)
            jordan = simple.jordans[0]
            for subsimple in connected:
                subjordan = subsimple.jordans[0]
                if jordan not in subsimple or subjordan not in simple:
                    externals.append(simple)
                    break
            else:
                internal.append(simple)
        simples = internal
    if len(connected) == 1:
        connected = connected[0]
    else:
        connected = ConnectedShape(connected)
    return (connected,) + divide_connecteds(externals)


def shape_from_jordans(jordans: Tuple[JordanCurve]) -> SubSetR2:
    """Returns the correspondent shape

    This function don't do entry validation
    as verify if one shape is inside other

    Example
    ----------
    >>> shape_from_jordans([])
    EmptyShape
    """
    assert len(jordans) != 0
    simples = tuple(map(SimpleShape, jordans))
    if len(simples) == 1:
        return simples[0]
    connecteds = divide_connecteds(simples)
    if len(connecteds) == 1:
        return connecteds[0]
    return DisjointShape(connecteds)
