"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""

from __future__ import annotations

from typing import Iterable, Tuple, Union

from ..core import IObject2D, IShape, Scalar
from ..curve.abc import IJordanCurve
from ..point import GeneralPoint
from ..utils import sorter


class SimpleShape(IShape):
    """
    SimpleShape class

    Is a shape which is defined by only one jordan curve.
    It represents the interior/exterior region of the jordan curve
    if the jordan curve is counter-clockwise/clockwise

    """

    def __init__(self, jordancurve: IJordanCurve, boundary: bool = True):
        if not isinstance(jordancurve, IJordanCurve):
            raise TypeError
        self.__jordan = jordancurve
        self.__boundary = bool(boundary)

    @property
    def jordan(self) -> IJordanCurve:
        return self.__jordan

    @property
    def jordans(self) -> Tuple[IJordanCurve]:
        return (self.jordan,)

    @property
    def area(self) -> Scalar:
        return self.jordan.area

    @property
    def boundary(self) -> bool:
        return self.__boundary

    def __str__(self) -> str:
        msg = f"Simple Shape of area {self.area} with vertices:\n"
        msg += "[" + ",\n ".join(map(str, self.jordan.vertices)) + "]"
        return msg

    def __repr__(self) -> str:
        area, vertices = self.area, self.jordan.vertices
        msg = f"Simple shape of area {area} with {len(vertices)} vertices"
        return msg

    def __eq__(self, other: object) -> bool:
        """Compare two shapes

        Parameters
        ----------
        other: IShape
            The shape to compare

        :raises ValueError: If ``other`` is not a IShape instance
        """
        if not isinstance(other, IObject2D):
            raise ValueError
        if not isinstance(other, SimpleShape):
            return False
        if self.area != other.area:
            return False
        if self.boundary != other.boundary:
            return False
        return self.jordan == other.jordan

    def __invert__(self) -> SimpleShape:
        return self.__class__(~self.jordan, not self.boundary)

    def winding(self, point: GeneralPoint) -> Scalar:
        return self.jordan.winding(point)


class ConnectedShape(IShape):
    """
    ConnectedShape Class

    A shape defined by intersection of two or more SimpleShapes

    """

    def __init__(self, subshapes: Iterable[SimpleShape]):
        subshapes = tuple(subshapes)
        for subshape in subshapes:
            if not isinstance(subshape, SimpleShape):
                raise TypeError
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
        simples = tuple(~simple for simple in self.subshapes)
        return DisjointShape(simples)

    def __iter__(self):
        yield from self.__subshapes

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
        indexs = tuple(sorter(areas))
        if areas[indexs[-1]] > 0:
            indexs = (indexs[-1],) + indexs[:-1]
        values = tuple(values[i] for i in indexs)
        self.__subshapes = tuple(values)

    def winding(self, point: GeneralPoint) -> Scalar:
        for subshape in self.subshapes:
            wind = subshape.winding(point)
            if wind != 1:
                return wind
        return 1


class DisjointShape(IShape):
    """
    DisjointShape Class

    A shape defined by the union of some SimpleShape instances and
    ConnectedShape instances
    """

    def __init__(
        self, subshapes: Iterable[Union[SimpleShape, ConnectedShape]]
    ):
        subshapes = tuple(subshapes)
        for subshape in subshapes:
            if not isinstance(subshape, (SimpleShape, ConnectedShape)):
                raise TypeError
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
                if osbshape.area != self_subshapes[0].area:
                    continue
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

    def __iter__(self):
        yield from self.__subshapes

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
        indexs = tuple(sorter(areas))
        values = tuple(values[i] for i in indexs)
        self.__subshapes = tuple(values)

    def winding(self, point: GeneralPoint) -> Scalar:
        for subshape in self.subshapes:
            wind = subshape.winding(point)
            if wind != 0:
                return wind
        return 0
