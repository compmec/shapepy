"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""

from __future__ import annotations

from typing import Tuple

from ..core import IObject2D, IShape, Scalar
from ..curve.abc import IJordanCurve


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
        v1 = self.jordan == other.jordan
        v2 = self.boundary == other.boundary
        return v1 and v2

    def __invert__(self) -> SimpleShape:
        return self.__class__(~self.jordan, not self.boundary)
