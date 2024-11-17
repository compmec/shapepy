"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""

from __future__ import annotations

from typing import Tuple

from ..core import Empty, IBoolean2D, ICurve, IObject2D, IShape, Scalar, Whole
from ..curve.abc import IJordanCurve
from ..point import GeneralPoint, Point2D


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

    def move(self, point: GeneralPoint) -> SimpleShape:
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
        self.__jordan = self.jordan.move(point)
        return self

    def scale(self, xscale: float, yscale: float) -> IShape:
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
        self.__jordan = self.jordan.scale(xscale, yscale)
        return self

    def rotate(self, angle: float, degrees: bool = False) -> IShape:
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
        self.__jordan = self.jordan.rotate(angle, degrees)
        return self

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
        return self.jordan == other.jordan and self.boundary == other.boundary

    def __invert__(self) -> SimpleShape:
        return self.__class__(~self.jordan, not self.boundary)

    def __contains__(self, other: object) -> bool:
        if isinstance(other, Point2D) or not isinstance(other, IObject2D):
            wind = self.jordan.winding(other)
            return wind == 1 or (0 < wind and self.boundary)
        if isinstance(other, Empty):
            return True
        if isinstance(other, Whole):
            return False
        if isinstance(other, ICurve):
            return self.__contains_curve(other)
        if isinstance(other, SimpleShape):
            return self.__contains_simple(other)
        if isinstance(other, IShape):
            return (~self) in (~other)
        raise NotImplementedError

    def __ror__(self, other: IBoolean2D) -> IBoolean2D:
        raise NotImplementedError

    def __rand__(self, other: IBoolean2D) -> IBoolean2D:
        raise NotImplementedError

    def __contains_curve(self, other: ICurve) -> bool:
        if not isinstance(other, ICurve):
            raise NotImplementedError
        if not all(vertex in self for vertex in other.vertices):
            return False
        nnodes = 64
        unodes = tuple(i / nnodes for i in range(1, nnodes))
        param_curve = other.param_curve
        for ka, kb in zip(param_curve.knots, param_curve.knots[1:]):
            for unode in unodes:
                tnode = (1 - unode) * ka + unode * kb
                if param_curve.eval(tnode, 0) not in self:
                    return False
        return True

    def __contains_simple(self, other: SimpleShape) -> bool:
        if not isinstance(other, SimpleShape):
            raise TypeError
        spos = self.area > 0
        opos = other.area > 0
        if spos ^ opos:
            if spos and not opos:
                return False
        elif self.area < other.area:
            return False
        elif spos and opos:
            return other.jordan in self
        elif self == other:
            return True
        if self.boundary or other.boundary:
            return other.jordan in self and self.jordan not in other
        self.__boundary = True
        try:
            return other.jordan in self and self.jordan not in other
        finally:
            self.__boundary = False
