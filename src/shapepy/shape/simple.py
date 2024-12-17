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
        self.__subshapes = subshapes

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
        simples = tuple(~simple for simple in self)
        return DisjointShape(simples)

    def __iter__(self):
        yield from self.__subshapes

    @property
    def area(self) -> Scalar:
        return sum(subshape.area for subshape in self)

    def winding(self, point: GeneralPoint) -> Scalar:
        for subshape in self:
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
        self.__subshapes = subshapes

    @property
    def area(self) -> Scalar:
        return sum(subshape.area for subshape in self)

    def __eq__(self, other: IObject2D):
        if not isinstance(other, DisjointShape):
            return False
        if self.area != other.area:
            return False
        self_subshapes = list(self)
        othe_subshapes = list(other)
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
        msg += f"{len(self)} subshapes"
        return msg

    def __repr__(self) -> str:
        return self.__str__()

    def __iter__(self):
        yield from self.__subshapes

    def winding(self, point: GeneralPoint) -> Scalar:
        for subshape in self:
            wind = subshape.winding(point)
            if wind != 0:
                return wind
        return 0
