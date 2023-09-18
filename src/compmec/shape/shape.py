"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any, Optional, Tuple, Union

import numpy as np

from compmec.shape.jordancurve import IntegrateJordan, JordanCurve
from compmec.shape.polygon import Box, Point2D


class IntegrateShape:
    @staticmethod
    def polynomial(
        shape: BaseShape, expx: int, expy: int, nnodes: Optional[int] = None
    ) -> float:
        """Computes the integral

        I = int_D x^expx * y^expy * dA

        Which D is the region defined by shape

        We transform this integral into a boundary integral

        I = (1/(1+expx)) * int_C x^(expx + 1) * y^expy * dy

        """
        assert isinstance(shape, BaseShape)
        assert isinstance(expx, int)
        assert isinstance(expy, int)
        assert nnodes is None or isinstance(nnodes, int)
        total = 0
        for jordan in shape.jordans:
            total += IntegrateJordan.vertical(jordan, expx + 1, expy, nnodes)
        return total / (1 + expx)

    @staticmethod
    def area(shape: BaseShape, nnodes: Optional[int] = None) -> float:
        """Computes the internal area of given shape"""
        return IntegrateShape.polynomial(shape, 0, 0, nnodes)


class FollowPath:
    """
    Class responsible to compute the final jordan curve
    result from boolean operation between two simple shapes

    """

    @staticmethod
    def split_two_jordans(jordana: JordanCurve, jordanb: JordanCurve):
        """
        Find the intersections between two jordan curves and call split on the
        nodes which intersects
        """
        assert isinstance(jordana, JordanCurve)
        assert isinstance(jordanb, JordanCurve)
        if jordana.box() & jordanb.box() is None:
            return
        all_positions = (set(), set())
        inters = jordana & jordanb
        for ai, bj, ui, vj in inters:
            all_positions[0].add((ai, ui))
            all_positions[1].add((bj, vj))
        all_positions = [tuple(sorted(nodes)) for nodes in all_positions]
        for positions, jordan in zip(all_positions, (jordana, jordanb)):
            indexs = [position[0] for position in positions]
            nodes = [position[1] for position in positions]
            jordan.split(indexs, nodes)

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

        The first point (a1, b1) = (0, index)

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
            for i, jordan in enumerate(jordans):
                if i == index_jordan:
                    continue
                if last_point in jordan:
                    break
            else:
                index_segment += 1
                continue
            index_jordan = i
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
        assert isinstance(oneobj, (tuple, list))
        assert isinstance(other, (tuple, list))
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
            new_bezier = new_bezier.copy()
            beziers.append(new_bezier)
        new_jordan = JordanCurve.from_segments(beziers)
        return new_jordan

    @staticmethod
    def follow_path(
        jordans: Tuple[JordanCurve], start_indexs: Tuple[Tuple[int]]
    ) -> Tuple[JordanCurve]:
        """
        Returns a list of jordan curves which is the result
        of the intersection between 'jordansa' and 'jordansb'
        """
        for jordan in jordans:
            assert isinstance(jordan, JordanCurve)
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
        indexsa = FollowPath.midpoints_one_shape(shapea, shapeb, closed, inside)
        indexsb = FollowPath.midpoints_one_shape(shapeb, shapea, closed, inside)
        indexsa = list(indexsa)
        njordansa = len(shapea.jordans)
        for indjorb, indsegb in indexsb:
            indexsa.append((njordansa + indjorb, indsegb))
        return tuple(indexsa)

    @staticmethod
    def or_shapes(shapea: BaseShape, shapeb: BaseShape) -> Tuple[JordanCurve]:
        assert isinstance(shapea, BaseShape)
        assert isinstance(shapeb, BaseShape)
        for jordana in shapea.jordans:
            for jordanb in shapeb.jordans:
                FollowPath.split_two_jordans(jordana, jordanb)
        indexs = FollowPath.midpoints_shapes(shapea, shapeb, closed=True, inside=False)
        all_jordans = tuple(shapea.jordans) + tuple(shapeb.jordans)
        new_jordans = FollowPath.follow_path(all_jordans, indexs)
        return new_jordans

    @staticmethod
    def and_shapes(shapea: BaseShape, shapeb: BaseShape) -> Tuple[JordanCurve]:
        assert isinstance(shapea, BaseShape)
        assert isinstance(shapeb, BaseShape)
        for jordana in shapea.jordans:
            for jordanb in shapeb.jordans:
                FollowPath.split_two_jordans(jordana, jordanb)
        indexs = FollowPath.midpoints_shapes(shapea, shapeb, closed=False, inside=True)
        all_jordans = tuple(shapea.jordans) + tuple(shapeb.jordans)
        new_jordans = FollowPath.follow_path(all_jordans, indexs)
        return new_jordans


class BaseShape(object):
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

    def __neg__(self) -> BaseShape:
        return ~self

    def __add__(self, other: BaseShape):
        return self | other

    def __mul__(self, value: BaseShape):
        return self & value

    def __sub__(self, value: BaseShape):
        return self & (~value)

    def __xor__(self, other: BaseShape):
        return (self - other) | (other - self)

    def __bool__(self) -> bool:
        """
        Returns True if the curve's is positive
        Else if curve's area is negative
        """
        return float(self) > 0

    def move(self, point: Point2D) -> BaseShape:
        point = Point2D(point)
        for jordan in self.jordans:
            jordan.move(point)
        return self

    def scale(self, xscale: float, yscale: float) -> BaseShape:
        for jordan in self.jordans:
            jordan.scale(xscale, yscale)
        return self

    def rotate(self, angle: float, degrees: bool = False) -> BaseShape:
        for jordan in self.jordans:
            jordan.rotate(angle, degrees)
        return self


class EmptyShape(BaseShape):
    """
    A class to represent a empty shape, the zero element
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(EmptyShape, cls).__new__(cls)
        return cls.__instance

    def __or__(self, other: BaseShape) -> BaseShape:
        return other.copy()

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

    def copy(self) -> EmptyShape:
        return self


class WholeShape(BaseShape):
    """
    A class to represent a empty shape, the zero element
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(WholeShape, cls).__new__(cls)
        return cls.__instance

    def __or__(self, other: BaseShape) -> BaseShape:
        return self

    def __and__(self, other: BaseShape) -> BaseShape:
        return other.copy()

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

    def copy(self) -> BaseShape:
        return self


class FiniteShape(BaseShape):
    def __init__(self, *args, **kwargs):
        self.__box = None

    def copy(self) -> FiniteShape:
        jordans = tuple(jordan.copy() for jordan in self.jordans)
        return ShapeFromJordans(jordans)

    def box(self) -> Box:
        if self.__box is None:
            box = self.jordans[0].box()
            for jordan in self.jordans[1:]:
                box |= jordan.box()
            self.__box = box
        return self.__box

    def __invert__(self) -> BaseShape:
        return ShapeFromJordans(tuple(~jordan for jordan in self.jordans))

    def __or__(self, other: BaseShape) -> BaseShape:
        assert isinstance(other, BaseShape)
        if isinstance(other, WholeShape):
            return WholeShape()
        if isinstance(other, EmptyShape):
            return self.copy()
        if other in self:
            return self.copy()
        if self in other:
            return other.copy()
        new_jordans = FollowPath.or_shapes(self, other)
        if len(new_jordans) == 0:
            return WholeShape()
        return ShapeFromJordans(new_jordans)

    def __and__(self, other: BaseShape) -> BaseShape:
        assert isinstance(other, BaseShape)
        if isinstance(other, WholeShape):
            return self.copy()
        if isinstance(other, EmptyShape):
            return EmptyShape()
        if other in self:
            return other.copy()
        if self in other:
            return self.copy()
        new_jordans = FollowPath.and_shapes(self, other)
        if len(new_jordans) == 0:
            return EmptyShape()
        return ShapeFromJordans(new_jordans)


class SimpleShape(FiniteShape):
    """Simple shape class

    Defined by only one jordan curve

    Example:
        - Interior of a circle, which jordan is in fact a circle
        - Interior of a polygon, which jordan are the edges
        - Exterior of a circle, when the jordan is a negative circle
    """

    def __init__(self, jordancurve: JordanCurve):
        assert isinstance(jordancurve, JordanCurve)
        super().__init__()
        self.__set_jordancurve(jordancurve)

    def __str__(self) -> str:
        area = float(self)
        vertices = self.jordans[0].vertices
        vertices = tuple([tuple(vertex) for vertex in vertices])
        msg = f"Simple Shape of area {area:.2f} with vertices:\n"
        msg += str(np.array(vertices, dtype="float64"))
        return msg

    def __repr__(self) -> str:
        area, vertices = float(self), self.jordans[0].vertices
        msg = f"Simple shape of area {area:.2f} with {len(vertices)} vertices"
        return msg

    def __float__(self) -> float:
        return float(self.__area)

    def __eq__(self, other: BaseShape) -> bool:
        if not isinstance(other, BaseShape):
            raise ValueError
        if not isinstance(other, SimpleShape):
            return False
        if float(self) != float(other):
            return False
        return self.jordans[0] == other.jordans[0]

    def __contains__(self, other: Union[Point2D, JordanCurve, BaseShape]) -> bool:
        if isinstance(other, BaseShape):
            return self.contains_shape(other)
        if isinstance(other, JordanCurve):
            return self.contains_jordan(other)
        point = Point2D(other)
        return self.contains_point(point)

    def __invert__(self) -> SimpleShape:
        return self.__class__(self.__inversejordan)

    @property
    def jordans(self) -> JordanCurve:
        return (self.__jordancurve,)

    def __set_jordancurve(self, other: JordanCurve):
        assert isinstance(other, JordanCurve)
        self.__jordancurve = other.copy()
        self.__inversejordan = ~other
        self.__area = IntegrateShape.area(self)

    def invert(self) -> SimpleShape:
        jordan = self.__jordancurve
        self.__jordancurve = self.__inversejordan
        self.__inversejordan = jordan
        return self

    def contains_point(
        self, point: Point2D, bound_point: Optional[bool] = True
    ) -> bool:
        """
        We compute the winding number to determine if
        the point is inside the region.
        Uses numerical integration
        See wikipedia for details.
        """
        point = Point2D(point)
        jordan = self.jordans[0]
        if float(jordan) > 0 and point not in self.box():
            return False
        if point in jordan:
            return bound_point
        wind = IntegrateJordan.winding_number(jordan, center=point)
        return wind == 1 if float(jordan) > 0 else wind == 0

    def contains_jordan(self, other: JordanCurve) -> bool:
        assert isinstance(other, JordanCurve)
        for point in other.points(1):
            if not self.contains_point(point):
                return False
        return True

    def contains_shape(self, other: BaseShape) -> bool:
        assert isinstance(other, BaseShape)
        if isinstance(other, EmptyShape):
            return True
        if isinstance(other, WholeShape):
            return False
        if isinstance(other, SimpleShape):
            return self.__contains_simple(other)
        if isinstance(other, ConnectedShape):
            # cap S_i in S_j = any_i (bar S_j in bar S_i)
            contains = False
            self.invert()
            for subshape in other.subshapes:
                subshape.invert()
                if subshape in self:
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

    def __contains_simple(self, other: SimpleShape) -> bool:
        assert isinstance(other, SimpleShape)
        areaA = float(other)
        areaB = float(self)
        jordana = other.jordans[0]
        jordanb = self.jordans[0]
        if areaA < 0 and areaB > 0:
            return False
        if not (self.box() & other.box()):
            return areaA > 0 and areaB < 0
        if areaA > 0 and areaB < 0:
            return jordana in self and jordanb not in other
        if areaA > areaB or jordana not in self:
            return False
        if areaA > 0:
            return True
        # If simple shape is not a square
        # may happens error here
        return True


class ConnectedShape(FiniteShape):
    """
    Class of connected shape
    This class stores, for example

        circle(radius = 2) - circle(radius = 1)

    Also stores the inversion of a simple shape

    This class can be interpreted as the intersection
    of many simple shapes

    """

    def __init__(self, subshapes: Tuple[SimpleShape]):
        super().__init__()
        self.subshapes = subshapes

    def __contains__(self, other: Union[Point2D, JordanCurve, BaseShape]) -> bool:
        for shape in self.subshapes:
            if other not in shape:
                return False
        return True

    def __float__(self) -> float:
        return sum(map(float, self.subshapes))

    def __str__(self) -> str:
        msg = f"Connected shape total area {float(self)}"
        return msg

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: BaseShape) -> bool:
        assert isinstance(other, BaseShape)
        if not isinstance(other, ConnectedShape):
            return False
        if abs(float(self) - float(other)) > 1e-6:
            return False
        return True

    def __invert__(self) -> DisjointShape:
        simples = [~simple for simple in self.subshapes]
        return DisjointShape(simples)

    @property
    def jordans(self) -> Tuple[JordanCurve]:
        return tuple(shape.jordans[0] for shape in self.subshapes)

    @property
    def subshapes(self) -> Tuple[SimpleShape]:
        return self.__subshapes

    @subshapes.setter
    def subshapes(self, values: Tuple[SimpleShape]):
        for value in values:
            assert isinstance(value, SimpleShape)
        areas = map(float, values)
        algori = lambda pair: pair[0]
        values = sorted(zip(areas, values), key=algori, reverse=True)
        values = tuple(val[1] for val in values)
        self.__subshapes = tuple(values)

    def contains_point(
        self, point: Point2D, bound_point: Optional[bool] = True
    ) -> bool:
        for subshape in self.subshapes:
            if not subshape.contains_point(point, bound_point):
                return False
        return True


class DisjointShape(FiniteShape):
    def __new__(cls, subshapes: Tuple[ConnectedShape]):
        subshapes = list(subshapes)
        while EmptyShape() in subshapes:
            subshapes.remove(EmptyShape())
        if len(subshapes) == 0:
            return EmptyShape()
        for subshape in subshapes:
            assert isinstance(subshape, (SimpleShape, ConnectedShape))
        if len(subshapes) == 1:
            return subshapes[0].copy()
        instance = super(DisjointShape, cls).__new__(cls)
        instance.subshapes = subshapes
        return instance

    def __init__(self, subshapes: Tuple[ConnectedShape]):
        super().__init__()

    def __float__(self) -> float:
        total = 0
        for subshape in self.subshapes:
            total += float(subshape)
        return float(total)

    def __contains__(self, other: Union[BaseShape, JordanCurve, Point2D]) -> bool:
        if isinstance(other, BaseShape):
            return self.contains_shape(other)
        for subshape in self.subshapes:
            if other in subshape:
                return True
        return False

    def __eq__(self, other: BaseShape):
        assert isinstance(other, BaseShape)
        if not isinstance(other, DisjointShape):
            return False
        if float(self) != float(other):
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
        msg = f"Disjoint shape with total area {float(self)} and "
        msg += f"{len(self.subshapes)} subshapes"
        return msg

    def __repr__(self) -> str:
        return self.__str__()

    def contains_point(
        self, point: Point2D, bound_point: Optional[bool] = True
    ) -> bool:
        for subshape in self.subshapes:
            if subshape.contains_point(point, bound_point):
                return True
        return False

    def contains_shape(self, other: FiniteShape) -> bool:
        """Checks if 'other' is inside the disjoint shape"""
        assert isinstance(other, BaseShape)
        if isinstance(other, EmptyShape):
            return True
        if isinstance(other, WholeShape):
            return False
        if isinstance(other, (SimpleShape, ConnectedShape)):
            for subshape in self.subshapes:
                if other in subshape:
                    return True
            return False
        if isinstance(other, DisjointShape):
            for subshape in other.subshapes:
                if subshape not in self:
                    return False
            return True

    @property
    def jordans(self) -> Tuple[JordanCurve]:
        lista = []
        for subshape in self.subshapes:
            lista += list(subshape.jordans)
        return tuple(lista)

    @property
    def subshapes(self) -> Tuple[BaseShape]:
        return self.__subshapes

    @subshapes.setter
    def subshapes(self, values: Tuple[BaseShape]):
        for value in values:
            assert isinstance(value, (SimpleShape, ConnectedShape))
        areas = map(float, values)
        lenghts = map(float, [val.jordans[0] for val in values])
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
        areas = map(float, simples)
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


def ShapeFromJordans(jordans: Tuple[JordanCurve]) -> BaseShape:
    """Returns the correspondent shape

    This function don't do entry validation
    as verify if one shape is inside other

    Example
    ----------
    >>> ShapeFromJordans([])
    EmptyShape
    """
    assert len(jordans) != 0
    simples = tuple(map(SimpleShape, jordans))
    if len(simples) == 1:
        return simples[0]
    connecteds = DivideConnecteds(simples)
    if len(connecteds) == 1:
        return connecteds[0]
    return DisjointShape(connecteds)
