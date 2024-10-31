"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""

from __future__ import annotations

from typing import Tuple, Union

from shapepy.core import Empty, ICurve, IObject2D, IShape, Scalar, Whole
from shapepy.point import GeneralPoint, Point2D

from ..curve.abc import IJordanCurve
from .simple import SimpleShape


class ConnectedShape(IShape):
    """
    ConnectedShape Class

    A shape defined by intersection of two or more SimpleShapes

    """

    def __init__(self, subshapes: Tuple[SimpleShape, ...]):
        self.subshapes = subshapes

    def __str__(self) -> str:
        msg = f"Connected shape total area {self.area}"
        return msg

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: IObject2D) -> bool:
        assert isinstance(other, IObject2D)
        if not isinstance(other, ConnectedShape):
            return False
        if abs(self.area - other.area) > 1e-6:
            return False
        return True

    def __invert__(self) -> DisjointShape:
        simples = [~simple for simple in self.subshapes]
        return DisjointShape(simples)

    def __contains__(self, other: object) -> bool:
        if not isinstance(other, IObject2D):
            other = Point2D(other)
        return all(other in subshape for subshape in self.subshapes)

    @property
    def area(self) -> Scalar:
        return sum(subshape.area for subshape in self.subshapes)

    @property
    def jordans(self) -> Tuple[IJordanCurve]:
        """Jordan curves that defines the shape

        :getter: Returns a set of jordan curves
        :type: tuple[IJordanCurve]
        """
        return tuple(shape.jordan for shape in self.subshapes)

    @property
    def subshapes(self) -> Tuple[SimpleShape, ...]:
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
    def subshapes(self, values: Tuple[SimpleShape, ...]):
        for value in values:
            assert isinstance(value, SimpleShape)
        areas = tuple(value.area for value in values)
        algori = lambda pair: pair[0]
        values = sorted(zip(areas, values), key=algori, reverse=True)
        values = tuple(val[1] for val in values)
        self.__subshapes = tuple(values)

    def move(self, point: GeneralPoint) -> ConnectedShape:
        """
        Moves/translate entire shape by an amount

        Parameters
        ----------

        point : Point2D
            The amount to move

        :return: The same instance
        :rtype: IShape

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()
        >>> circle.move(1, 2)

        """
        if not isinstance(point, Point2D):
            point = Point2D(point)
        for subshape in self.subshapes:
            subshape.move(point)
        return self

    def scale(self, xscale: float, yscale: float) -> ConnectedShape:
        """
        Scales entire shape by an amount

        Parameters
        ----------

        xscale : float
            The amount to scale in horizontal direction
        yscale : float
            The amount to scale in vertical direction

        :return: The same instance
        :rtype: IShape

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()
        >>> circle.scale(2, 3)

        """
        for subshape in self.subshapes:
            subshape.scale(xscale, yscale)
        return self

    def rotate(self, angle: float, degrees: bool = False) -> ConnectedShape:
        """
        Rotates entire shape around the origin by an amount

        Parameters
        ----------

        angle : float
            The amount to rotate around origin
        degrees : bool, default = False
            Flag to indicate if ``angle`` is in radians or degrees

        :return: The same instance
        :rtype: IShape

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()
        >>> circle.rotate(angle = 90, degrees = True)

        """
        for subshape in self.subshapes:
            subshape.rotate(angle, degrees)
        return self


class DisjointShape(IShape):
    """
    DisjointShape Class

    A shape defined by the union of some SimpleShape instances and
    ConnectedShape instances
    """

    def __init__(
        self, subshapes: Tuple[Union[SimpleShape, ConnectedShape], ...]
    ):
        self.subshapes = subshapes

    @property
    def area(self) -> Scalar:
        return sum(subshape.area for subshape in self.subshapes)

    def __eq__(self, other: IObject2D):
        if not isinstance(other, DisjointShape):
            return False
        if self.area != other.area:
            return False
        self_subshapes = list(self.subshapes)
        othe_subshapes = list(other.subshapes)
        # Compare if a curve is inside another
        while len(self_subshapes) and len(othe_subshapes):
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

    def __contains__(self, other: object) -> bool:
        if not isinstance(other, IObject2D):
            other = Point2D(other)
        if isinstance(other, (Point2D, ICurve)):
            return any(other in subshape for subshape in self.subshapes)
        if isinstance(other, Empty):
            return False
        if isinstance(other, Whole):
            return True
        if isinstance(other, DisjointShape):
            return all(
                any(osub in ssub for ssub in self.subshapes)
                for osub in other.subshapes
            )
        if isinstance(other, (SimpleShape, ConnectedShape)):
            return any(other in subshape for subshape in self.subshapes)
        raise NotImplementedError

    @property
    def jordans(self) -> Tuple[IJordanCurve]:
        """Jordan curves that defines the shape

        :getter: Returns a set of jordan curves
        :type: tuple[IJordanCurve]
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
    def subshapes(self, values: Tuple[IShape]):
        for value in values:
            assert isinstance(value, (SimpleShape, ConnectedShape))
        areas = tuple(value.area for value in values)
        lenghts = tuple(val.jordans[0].lenght for val in values)
        algori = lambda triple: triple[:2]
        values = sorted(zip(areas, lenghts, values), key=algori, reverse=True)
        values = tuple(val[2] for val in values)
        self.__subshapes = tuple(values)


def DivideConnecteds(
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
    while len(simples):
        areas = tuple(simple.area for simple in simples)
        absareas = tuple(map(abs, areas))
        index = absareas.index(max(absareas))
        connected.append(simples.pop(index))
        internal = []
        while len(simples):  # Divide in two groups
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
    return (connected,) + DivideConnecteds(externals)


def ShapeFromJordans(jordans: Tuple[IJordanCurve]) -> IShape:
    """Returns the correspondent shape

    This function don't do entry validation
    as verify if one shape is inside other

    Example
    ----------
    >>> ShapeFromJordans([])
    Empty
    """
    assert len(jordans) != 0
    simples = tuple(map(SimpleShape, jordans))
    if len(simples) == 1:
        return simples[0]
    connecteds = DivideConnecteds(simples)
    if len(connecteds) == 1:
        return connecteds[0]
    return DisjointShape(connecteds)
