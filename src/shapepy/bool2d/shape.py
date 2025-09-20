"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""

from __future__ import annotations

from copy import copy
from typing import Iterable, Iterator, Set, Tuple, Union

from ..geometry.box import Box
from ..geometry.jordancurve import JordanCurve
from ..geometry.point import Point2D
from ..loggers import debug
from ..scalar.angle import Angle
from ..scalar.reals import Real
from ..tools import Is, To
from .base import Future, SubSetR2
from .curve import SingleCurve
from .density import (
    Density,
    intersect_densities,
    lebesgue_density_jordan,
    unite_densities,
)
from .point import SinglePoint


class SimpleShape(SubSetR2):
    """
    SimpleShape class

    Is a shape which is defined by only one jordan curve.
    It represents the interior/exterior region of the jordan curve
    if the jordan curve is counter-clockwise/clockwise

    """

    def __init__(self, jordancurve: JordanCurve, boundary: bool = True):
        assert Is.jordan(jordancurve)
        self.__jordancurve = jordancurve
        self.boundary = boundary

    def __copy__(self) -> SimpleShape:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> SimpleShape:
        return SimpleShape(copy(self.__jordancurve))

    def __str__(self) -> str:  # pragma: no cover  # For debug
        area = float(self.area)
        vertices = tuple(map(tuple, self.jordan.vertices()))
        return f"SimpleShape[{area:.2f}]:[{vertices}]"

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
            and self.jordan == other.jordan
        )

    @property
    def boundary(self) -> bool:
        """The flag that informs if the boundary is inside the Shape"""
        return self.__boundary

    @boundary.setter
    def boundary(self, value: bool):
        self.__boundary = bool(value)

    @property
    def jordan(self) -> JordanCurve:
        """Gives the jordan curve that defines the boundary"""
        return self.__jordancurve

    @property
    def jordans(self) -> Tuple[JordanCurve]:
        """Gives the jordan curve that defines the boundary"""
        return (self.__jordancurve,)

    @property
    def area(self) -> Real:
        """The internal area that is enclosed by the shape"""
        return self.__jordancurve.area

    @debug("shapepy.bool2d.shape")
    def __hash__(self):
        return hash(self.area)

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

    @debug("shapepy.bool2d.shape")
    def __contains__(self, other: SubSetR2) -> bool:
        if Is.instance(other, SinglePoint):
            return self.__contains_point(other)
        if Is.instance(other, SingleCurve):
            return self.__contains_curve(other)
        if Is.instance(other, SimpleShape):
            return self.__contains_simple(other)
        return super().__contains__(other)

    def __contains_point(self, point: SinglePoint) -> bool:
        point = Future.convert(point)
        density = float(self.density(point.internal))
        return density > 0 if self.boundary else density == 1

    def __contains_curve(self, curve: SingleCurve) -> bool:
        piecewise = curve.internal.parametrize()
        vertices = map(piecewise, piecewise.knots[:-1])
        if not all(map(self.__contains_point, vertices)):
            return False
        inters = piecewise & self.jordan
        if not inters:
            return True
        knots = sorted(inters.all_knots[id(piecewise)])
        midknots = ((k0 + k1) / 2 for k0, k1 in zip(knots, knots[1:]))
        midpoints = map(piecewise, midknots)
        return all(map(self.__contains_point, midpoints))

    # pylint: disable=chained-comparison
    def __contains_simple(self, other: SimpleShape) -> bool:
        assert Is.instance(other, SimpleShape)
        areaa = other.area
        areab = self.area
        jordana = other.jordan
        jordanb = self.jordan
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

    def move(self, vector: Point2D) -> JordanCurve:
        self.__jordancurve = self.__jordancurve.move(vector)
        return self

    def scale(self, amount: Union[Real, Tuple[Real, Real]]) -> JordanCurve:
        self.__jordancurve = self.__jordancurve.scale(amount)
        return self

    def rotate(self, angle: Angle) -> JordanCurve:
        self.__jordancurve = self.__jordancurve.rotate(angle)
        return self

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
        return self.jordan.box()

    def density(self, center: Point2D) -> Density:
        return lebesgue_density_jordan(self.jordan, center)


class ConnectedShape(SubSetR2):
    """
    ConnectedShape Class

    A shape defined by intersection of two or more SimpleShapes

    """

    def __init__(self, subshapes: Iterable[SimpleShape]):
        self.subshapes = subshapes

    def __copy__(self) -> ConnectedShape:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> ConnectedShape:
        simples = tuple(map(copy, self.subshapes))
        return ConnectedShape(simples)

    @property
    def area(self) -> Real:
        """The internal area that is enclosed by the shape"""
        return sum(simple.area for simple in self.subshapes)

    def __str__(self) -> str:  # pragma: no cover  # For debug
        return f"Connected shape total area {self.area}"

    def __eq__(self, other: SubSetR2) -> bool:
        assert Is.instance(other, SubSetR2)
        return (
            Is.instance(other, ConnectedShape)
            and hash(self) == hash(other)
            and self.area == other.area
            and self.subshapes == other.subshapes
        )

    @debug("shapepy.bool2d.shape")
    def __hash__(self):
        return hash(self.area)

    def __iter__(self) -> Iterator[SimpleShape]:
        yield from self.subshapes

    @property
    def jordans(self) -> Tuple[JordanCurve, ...]:
        """Jordan curves that defines the shape

        :getter: Returns a set of jordan curves
        :type: tuple[JordanCurve]
        """
        return tuple(shape.jordan for shape in self.subshapes)

    @property
    def subshapes(self) -> Set[SimpleShape]:
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
    def subshapes(self, simples: Iterable[SimpleShape]):
        simples = frozenset(simples)
        if not all(Is.instance(simple, SimpleShape) for simple in simples):
            raise TypeError
        self.__subshapes = simples

    def move(self, vector: Point2D) -> JordanCurve:
        vector = To.point(vector)
        for subshape in self.subshapes:
            subshape.move(vector)
        return self

    def scale(self, amount: Union[Real, Tuple[Real, Real]]) -> JordanCurve:
        for subshape in self.subshapes:
            subshape.scale(amount)
        return self

    def rotate(self, angle: Angle) -> JordanCurve:
        angle = To.angle(angle)
        for subshape in self.subshapes:
            subshape.rotate(angle)
        return self

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
        for sub in self.subshapes:
            box |= sub.jordan.box()
        return box

    def density(self, center: Point2D) -> Density:
        center = To.point(center)
        densities = (sub.density(center) for sub in self.subshapes)
        return intersect_densities(densities)


class DisjointShape(SubSetR2):
    """
    DisjointShape Class

    A shape defined by the union of some SimpleShape instances and
    ConnectedShape instances
    """

    def __init__(
        self, subshapes: Iterable[Union[SimpleShape, ConnectedShape]]
    ):
        self.subshapes = subshapes

    def __copy__(self) -> ConnectedShape:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo):
        subshapes = tuple(map(copy, self.subshapes))
        return DisjointShape(subshapes)

    def __iter__(self) -> Iterator[Union[SimpleShape, ConnectedShape]]:
        yield from self.subshapes

    @property
    def area(self) -> Real:
        """The internal area that is enclosed by the shape"""
        return sum(sub.area for sub in self.subshapes)

    @property
    def jordans(self) -> Tuple[JordanCurve, ...]:
        """Jordan curves that defines the shape

        :getter: Returns a set of jordan curves
        :type: tuple[JordanCurve]
        """
        jordans = []
        for subshape in self.subshapes:
            jordans += list(subshape.jordans)
        return tuple(jordans)

    def __eq__(self, other: SubSetR2):
        assert Is.instance(other, SubSetR2)
        return (
            Is.instance(other, DisjointShape)
            and hash(self) == hash(other)
            and self.area == other.area
            and self.subshapes == other.subshapes
        )

    def __str__(self) -> str:  # pragma: no cover  # For debug
        msg = f"Disjoint shape with total area {self.area} and "
        msg += f"{len(self.subshapes)} subshapes"
        return msg

    @debug("shapepy.bool2d.shape")
    def __hash__(self):
        return hash(self.area)

    @property
    def subshapes(self) -> Set[Union[SimpleShape, ConnectedShape]]:
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
    def subshapes(self, values: Iterable[SubSetR2]):
        values = frozenset(values)
        if not all(
            Is.instance(sub, (SimpleShape, ConnectedShape)) for sub in values
        ):
            raise ValueError
        self.__subshapes = values

    def move(self, vector: Point2D) -> JordanCurve:
        vector = To.point(vector)
        for subshape in self.subshapes:
            subshape.move(vector)
        return self

    def scale(self, amount: Union[Real, Tuple[Real, Real]]) -> JordanCurve:
        for subshape in self.subshapes:
            subshape.scale(amount)
        return self

    def rotate(self, angle: Angle) -> JordanCurve:
        angle = To.angle(angle)
        for subshape in self.subshapes:
            subshape.rotate(angle)
        return self

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
        for sub in self.subshapes:
            box |= sub.box()
        return box

    def density(self, center: Point2D) -> Real:
        center = To.point(center)
        densities = (sub.density(center) for sub in self.subshapes)
        return unite_densities(densities)


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
            jordan = simple.jordan
            for subsimple in connected:
                subjordan = subsimple.jordan
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
