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
from fractions import Fraction
from typing import Any, Iterable, Optional, Tuple, Union

import numpy as np
from rbool import Empty

from shapepy.geometry.box import Box
from shapepy.geometry.jordancurve import JordanCurve
from shapepy.geometry.point import Point2D

from ..geometry.integral import IntegrateJordan
from ..geometry.intersection import GeometricIntersectionCurves
from ..tools import Is, To


class SuperclassMeta(type):
    """
    This class is the parent of other classes such
    still gets the docstrings of their parent
    """

    def __new__(mcs, classname, bases, cls_dict):
        cls = super().__new__(mcs, classname, bases, cls_dict)
        for name, member in cls_dict.items():
            if not getattr(member, "__doc__"):
                try:
                    member.__doc__ = getattr(bases[-1], name).__doc__
                except AttributeError:
                    pass
        return cls


class FollowPath:
    """
    Class responsible to compute the final jordan curve
    result from boolean operation between two simple shapes

    """

    @staticmethod
    def split_on_intersection(
        all_group_jordans: Iterable[Iterable[JordanCurve]],
    ):
        """
        Find the intersections between two jordan curves and call split on the
        nodes which intersects
        """
        intersection = GeometricIntersectionCurves([])
        all_group_jordans = tuple(map(tuple, all_group_jordans))
        for i, jordansi in enumerate(all_group_jordans):
            for j in range(i + 1, len(all_group_jordans)):
                jordansj = all_group_jordans[j]
                for jordana in jordansi:
                    for jordanb in jordansj:
                        intersection |= jordana & jordanb
        intersection.evaluate()
        for jordans in all_group_jordans:
            for jordan in jordans:
                piece = jordan.piecewise
                piece.snap(intersection.all_knots[id(piece)])

    @staticmethod
    def pursue_path(
        index_jordan: int, index_segment: int, jordans: Tuple[JordanCurve]
    ) -> Tuple[Tuple[int]]:
        """
        Given a list of jordans, it returns a matrix of integers like
        [(a1, b1), (a2, b2), (a3, b3), ..., (an, bn)] such
            End point of jordans[a_{i}].segments[b_{i}]
            Start point of jordans[a_{i+1}].segments[b_{i+1}]
        are equal

        The first point (a1, b1) = (index_jordan, index_segment)

        The end point of jordans[an].segments[bn] is equal to
        the start point of jordans[a1].segments[b1]

        We suppose there's no triple intersection
        """
        matrix = []
        all_segments = [jordan.segments for jordan in jordans]
        while True:
            index_segment %= len(all_segments[index_jordan])
            segment = all_segments[index_jordan][index_segment]
            if (index_jordan, index_segment) in matrix:
                break
            matrix.append((index_jordan, index_segment))
            last_point = segment.ctrlpoints[-1]
            possibles = []
            for i, jordan in enumerate(jordans):
                if i == index_jordan:
                    continue
                if last_point in jordan:
                    possibles.append(i)
            if len(possibles) == 0:
                index_segment += 1
                continue
            index_jordan = possibles[0]
            for j, segj in enumerate(all_segments[index_jordan]):
                if segj.ctrlpoints[0] == last_point:
                    index_segment = j
                    break
        return tuple(matrix)

    @staticmethod
    def is_rotation(oneobj: Tuple[Any], other: Tuple[Any]) -> bool:
        """
        Tells if a list is equal to another
        """
        assert Is.iterable(oneobj)
        assert Is.iterable(other)
        oneobj = tuple(oneobj)
        other = tuple(other)
        if len(oneobj) != len(other):
            return False
        rotation = 0
        for elem in oneobj:
            if elem == other[0]:
                break
            rotation += 1
        else:
            return False
        nelems = len(other)
        for i, elem in enumerate(other):
            j = (i + rotation) % nelems
            if elem != oneobj[j]:
                return False
        return True

    @staticmethod
    def filter_rotations(matrix: Tuple[Tuple[Any]]):
        """
        Remove repeted elements in matrix such they are only rotations

        Example:
        filter_tuples([[A, B, C], [B, C, A]]) -> [[A, B, C]]
        filter_tuples([[A, B, C], [C, B, A]]) -> [[A, B, C], [C, B, A]]
        """
        filtered = []
        for line in matrix:
            for fline in filtered:
                if FollowPath.is_rotation(line, fline):
                    break
            else:
                filtered.append(line)
        return tuple(filtered)

    @staticmethod
    def indexs_to_jordan(
        jordans: Tuple[JordanCurve], matrix_indexs: Tuple[Tuple[int, int]]
    ) -> JordanCurve:
        """
        Given 'n' jordan curves, and a matrix of integers
        [(a0, b0), (a1, b1), ..., (am, bm)]
        Returns a myjordan (JordanCurve instance) such
        len(myjordan.segments) = matrix_indexs.shape[0]
        myjordan.segments[i] = jordans[ai].segments[bi]
        """
        beziers = []
        for index_jordan, index_segment in matrix_indexs:
            new_bezier = jordans[index_jordan].segments[index_segment]
            new_bezier = copy(new_bezier)
            beziers.append(new_bezier)
        new_jordan = JordanCurve(beziers)
        return new_jordan

    @staticmethod
    def follow_path(
        jordans: Tuple[JordanCurve], start_indexs: Tuple[Tuple[int]]
    ) -> Tuple[JordanCurve]:
        """
        Returns a list of jordan curves which is the result
        of the intersection between 'jordansa' and 'jordansb'
        """
        assert all(map(Is.jordan, jordans))
        bez_indexs = []
        for ind_jord, ind_seg in start_indexs:
            indices_matrix = FollowPath.pursue_path(ind_jord, ind_seg, jordans)
            bez_indexs.append(indices_matrix)
        bez_indexs = FollowPath.filter_rotations(bez_indexs)
        new_jordans = []
        for indices_matrix in bez_indexs:
            jordan = FollowPath.indexs_to_jordan(jordans, indices_matrix)
            new_jordans.append(jordan)
        return tuple(new_jordans)

    @staticmethod
    def midpoints_one_shape(
        shapea: BaseShape, shapeb: BaseShape, closed: bool, inside: bool
    ) -> Tuple[Tuple[int]]:
        """
        Returns a matrix [(a0, b0), (a1, b1), ...]
        such the middle point of
            shapea.jordans[a0].segments[b0]
        is inside/outside the shapeb

        If parameter ``closed`` is True, consider a
        point in boundary is inside.
        If ``closed=False``, a boundary point is outside

        """

        insiders = []
        outsiders = []
        for i, jordan in enumerate(shapea.jordans):
            for j, segment in enumerate(jordan.segments):
                mid_point = segment(Fraction(1, 2))
                if shapeb.contains_point(mid_point, closed):
                    insiders.append((i, j))
                else:
                    outsiders.append((i, j))
        return tuple(insiders) if inside else tuple(outsiders)

    @staticmethod
    def midpoints_shapes(
        shapea: BaseShape, shapeb: BaseShape, closed: bool, inside: bool
    ) -> Tuple[Tuple[int]]:
        """
        This function computes the indexes of the midpoints from
        both shapes, shifting the indexs of shapeb.jordans
        """
        indexsa = FollowPath.midpoints_one_shape(
            shapea, shapeb, closed, inside
        )
        indexsb = FollowPath.midpoints_one_shape(  # pylint: disable=W1114
            shapeb, shapea, closed, inside
        )
        indexsa = list(indexsa)
        njordansa = len(shapea.jordans)
        for indjorb, indsegb in indexsb:
            indexsa.append((njordansa + indjorb, indsegb))
        return tuple(indexsa)

    @staticmethod
    def or_shapes(shapea: BaseShape, shapeb: BaseShape) -> Tuple[JordanCurve]:
        """
        Computes the set of jordan curves that defines the boundary of
        the union between the two base shapes
        """
        assert Is.instance(shapea, BaseShape)
        assert Is.instance(shapeb, BaseShape)
        FollowPath.split_on_intersection([shapea.jordans, shapeb.jordans])
        indexs = FollowPath.midpoints_shapes(
            shapea, shapeb, closed=True, inside=False
        )
        all_jordans = tuple(shapea.jordans) + tuple(shapeb.jordans)
        new_jordans = FollowPath.follow_path(all_jordans, indexs)
        return new_jordans

    @staticmethod
    def and_shapes(shapea: BaseShape, shapeb: BaseShape) -> Tuple[JordanCurve]:
        """
        Computes the set of jordan curves that defines the boundary of
        the intersection between the two base shapes
        """
        assert Is.instance(shapea, BaseShape)
        assert Is.instance(shapeb, BaseShape)
        FollowPath.split_on_intersection([shapea.jordans, shapeb.jordans])
        indexs = FollowPath.midpoints_shapes(
            shapea, shapeb, closed=False, inside=True
        )
        all_jordans = tuple(shapea.jordans) + tuple(shapeb.jordans)
        new_jordans = FollowPath.follow_path(all_jordans, indexs)
        return new_jordans


# Inherit from object is needed
# pylint: disable=useless-object-inheritance
class BaseShape(object, metaclass=SuperclassMeta):
    """
    Class which allows operations like:
     - move
     - scale
     - rotation
     - invert
     - union
     - intersection
     - XOR
    """

    def __init__(self):
        pass

    @abc.abstractmethod
    def __invert__(self) -> BaseShape:
        """Invert shape"""

    @abc.abstractmethod
    def __or__(self, other: BaseShape) -> BaseShape:
        """Union shapes"""

    @abc.abstractmethod
    def __and__(self, other: BaseShape) -> BaseShape:
        """Intersection shapes"""

    def __neg__(self) -> BaseShape:
        """Invert the BaseShape"""
        return ~self

    def __add__(self, other: BaseShape):
        """Union of BaseShape"""
        return self | other

    def __mul__(self, value: BaseShape):
        """Intersection of BaseShape"""
        return self & value

    def __sub__(self, value: BaseShape):
        """Subtraction of BaseShape"""
        return self & (~value)

    def __xor__(self, other: BaseShape):
        """XOR of BaseShape"""
        return (self - other) | (other - self)

    def __bool__(self) -> bool:
        """Are is positive ?"""
        return float(self) > 0


# pylint: disable=abstract-method
class SingletonShape(BaseShape):
    """SingletonShape"""

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(SingletonShape, cls).__new__(cls)
        return cls.__instance

    def __copy__(self) -> SingletonShape:
        return self

    def __deepcopy__(self, memo) -> SingletonShape:
        return self


class EmptyShape(SingletonShape):
    """EmptyShape is a singleton class to represent an empty shape

    Example use
    -----------
    >>> from shapepy import EmptyShape
    >>> empty = EmptyShape()
    >>> print(empty)
    EmptyShape
    >>> print(float(empty))  # Area
    0.0
    >>> (0, 0) in empty
    False
    """

    def __or__(self, other: BaseShape) -> BaseShape:
        return copy(other)

    def __and__(self, other: BaseShape) -> BaseShape:
        return self

    def __sub__(self, other: BaseShape) -> BaseShape:
        return self

    def __float__(self) -> float:
        return float(0)

    def __invert__(self) -> BaseShape:
        return WholeShape()

    def __contains__(self, other: BaseShape) -> bool:
        return self is other

    def __str__(self) -> str:
        return "EmptyShape"

    def __repr__(self) -> str:
        return self.__str__()


class WholeShape(SingletonShape):
    """WholeShape is a singleton class to represent all plane

    Example use
    -----------
    >>> from shapepy import WholeShape
    >>> whole = WholeShape()
    >>> print(whole)
    WholeShape
    >>> print(float(whole))  # Area
    inf
    >>> (0, 0) in whole
    True
    """

    def __or__(self, other: BaseShape) -> WholeShape:
        return self

    def __and__(self, other: BaseShape) -> BaseShape:
        return copy(other)

    def __float__(self) -> float:
        return float("inf")

    def __invert__(self) -> BaseShape:
        return EmptyShape()

    def __contains__(self, other: BaseShape) -> bool:
        return True

    def __str__(self) -> str:
        return "WholeShape"

    def __repr__(self) -> str:
        return self.__str__()

    def __sub__(self, other: BaseShape) -> BaseShape:
        return ~other


# pylint: disable=no-member
class DefinedShape(BaseShape):
    """
    DefinedShape is the base class for SimpleShape,
    ConnectedShape and DisjointShape

    """

    def __init__(self, *args, **kwargs):
        pass

    def __copy__(self) -> DefinedShape:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> DefinedShape:
        jordans = tuple(copy(jordan) for jordan in self.jordans)
        return shape_from_jordans(jordans)

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

    def __invert__(self) -> BaseShape:
        return shape_from_jordans(tuple(~jordan for jordan in self.jordans))

    def __or__(self, other: BaseShape) -> BaseShape:
        assert Is.instance(other, BaseShape)
        if Is.instance(other, WholeShape):
            return WholeShape()
        if Is.instance(other, EmptyShape):
            return copy(self)
        if other in self:
            return copy(self)
        if self in other:
            return copy(other)
        new_jordans = FollowPath.or_shapes(self, other)
        if len(new_jordans) == 0:
            return WholeShape()
        return shape_from_jordans(new_jordans)

    def __and__(self, other: BaseShape) -> BaseShape:
        assert Is.instance(other, BaseShape)
        if Is.instance(other, WholeShape):
            return copy(self)
        if Is.instance(other, EmptyShape):
            return EmptyShape()
        if other in self:
            return copy(other)
        if self in other:
            return copy(self)
        new_jordans = FollowPath.and_shapes(self, other)
        if len(new_jordans) == 0:
            return EmptyShape()
        return shape_from_jordans(new_jordans)

    def __contains__(
        self, other: Union[Point2D, JordanCurve, BaseShape]
    ) -> bool:
        if Is.instance(other, BaseShape):
            return self.contains_shape(other)
        if Is.instance(other, JordanCurve):
            return self.contains_jordan(other)
        point = To.point(other)
        return self.contains_point(point)

    def __float__(self) -> float:
        return float(sum(jordan.area for jordan in self.jordans))

    def move(self, point: Point2D) -> BaseShape:
        """
        Moves/translate entire shape by an amount

        Parameters
        ----------

        point : Point2D
            The amount to move

        :return: The same instance
        :rtype: BaseShape

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

    def scale(self, xscale: float, yscale: float) -> BaseShape:
        """
        Scales entire shape by an amount

        Parameters
        ----------

        xscale : float
            The amount to scale in horizontal direction
        yscale : float
            The amount to scale in vertical direction

        :return: The same instance
        :rtype: BaseShape

        Example use
        -----------
        >>> from shapepy import Primitive
        >>> circle = Primitive.circle()
        >>> circle.scale(2, 3)

        """
        for jordan in self.jordans:
            jordan.scale(xscale, yscale)
        return self

    def rotate(self, angle: float, degrees: bool = False) -> BaseShape:
        """
        Rotates entire shape around the origin by an amount

        Parameters
        ----------

        angle : float
            The amount to rotate around origin
        degrees : bool, default = False
            Flag to indicate if ``angle`` is in radians or degrees

        :return: The same instance
        :rtype: BaseShape

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

    def contains_shape(self, other: BaseShape) -> bool:
        """
        Checks if the all points of given shape are inside the shape

        Mathematically speaking, checks if ``other`` is a subset of ``self``

        Parameters
        ----------

        other : BaseShape
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
        assert Is.instance(other, BaseShape)
        if Is.instance(other, EmptyShape):
            return True
        if Is.instance(other, WholeShape):
            return False
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
    def _contains_shape(self, other: BaseShape):
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
        super().__init__()
        self.__set_jordancurve(jordancurve)

    def __str__(self) -> str:
        area = float(self)
        vertices = self.jordans[0].vertices
        vertices = tuple(tuple(vertex) for vertex in vertices)
        msg = f"Simple Shape of area {area:.2f} with vertices:\n"
        msg += str(np.array(vertices, dtype="float64"))
        return msg

    def __repr__(self) -> str:
        area, vertices = float(self), self.jordans[0].vertices
        msg = f"Simple shape of area {area:.2f} with {len(vertices)} vertices"
        return msg

    def __eq__(self, other: BaseShape) -> bool:
        """Compare two shapes

        Parameters
        ----------
        other: BaseShape
            The shape to compare

        :raises ValueError: If ``other`` is not a BaseShape instance
        """
        if not Is.instance(other, BaseShape):
            raise ValueError
        if not Is.instance(other, SimpleShape):
            return False
        if float(self) != float(other):
            return False
        return self.jordans[0] == other.jordans[0]

    def __invert__(self) -> SimpleShape:
        return self.__class__(~self.jordans[0])

    @property
    def jordans(self) -> Tuple[JordanCurve]:
        """
        The jordans curve that define the SimpleShape

        It has only one jordan curve inside it
        """
        return (self.__jordancurve,)

    def __set_jordancurve(self, other: JordanCurve):
        assert Is.jordan(other)
        self.__jordancurve = copy(other)

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
        if float(jordan) > 0:
            return wind > 0 if boundary else wind == 1
        return wind > -1 if boundary else wind == 0

    def _contains_jordan(
        self, jordan: JordanCurve, boundary: Optional[bool] = True
    ) -> bool:
        piecewise = jordan.piecewise
        vertices = map(piecewise, piecewise.knots)
        if not all(map(self.contains_point, vertices)):
            return False
        inters = jordan & self.jordans[0]
        inters.evaluate()
        if inters.all_subsets[id(piecewise)] is not Empty():
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
        areaa = float(other)
        areab = float(self)
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
        super().__init__()
        self.subshapes = subshapes

    def __float__(self) -> float:
        return sum(map(float, self.subshapes))

    def __str__(self) -> str:
        msg = f"Connected shape total area {float(self)}"
        return msg

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: BaseShape) -> bool:
        assert Is.instance(other, BaseShape)
        if not Is.instance(other, ConnectedShape):
            return False
        if abs(float(self) - float(other)) > 1e-6:
            return False
        return True

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
    def subshapes(self, values: Tuple[SimpleShape]):
        for value in values:
            assert Is.instance(value, SimpleShape)
        areas = map(float, values)

        def algori(pair):
            return pair[0]

        values = sorted(zip(areas, values), key=algori, reverse=True)
        values = tuple(val[1] for val in values)
        self.__subshapes = tuple(values)

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
        super().__init__()

    def __float__(self) -> float:
        total = 0
        for subshape in self.subshapes:
            total += float(subshape)
        return float(total)

    def __eq__(self, other: BaseShape):
        assert Is.instance(other, BaseShape)
        if not Is.instance(other, DisjointShape):
            return False
        if float(self) != float(other):
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
        msg = f"Disjoint shape with total area {float(self)} and "
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
    def subshapes(self, values: Tuple[BaseShape]):
        for value in values:
            assert Is.instance(value, (SimpleShape, ConnectedShape))
        areas = map(float, values)
        lenghts = map(float, [val.jordans[0] for val in values])

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
        areas = map(float, simples)
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


def shape_from_jordans(jordans: Tuple[JordanCurve]) -> BaseShape:
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
