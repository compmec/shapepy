"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""
from __future__ import annotations

from copy import deepcopy
from typing import List, Tuple, Union

import numpy as np

from compmec import nurbs
from compmec.shape.jordancurve import JordanCurve, NumIntegration
from compmec.shape.polygon import Point2D


class FollowPath:
    """
    Class responsible to compute the final jordan curve
    result from boolean operation between two simple shapes

    """

    @staticmethod
    def split_at_intersections(jordans: Tuple[JordanCurve]) -> Tuple[JordanCurve]:
        assert isinstance(jordans, (tuple, list))
        for jordan in jordans:
            assert isinstance(jordan, JordanCurve)
        ncurves = len(jordans)
        all_positions = [set() for i in range(ncurves)]
        for i in range(ncurves - 1):
            for j in range(i + 1, ncurves):
                inters = jordans[i].intersection(jordans[j], end_points=False)
                for ai, bj, ui, vj in inters:
                    all_positions[i].add((ai, ui))
                    all_positions[j].add((bj, vj))
        all_positions = [tuple(sorted(nodes)) for nodes in all_positions]
        for positions, jordan in zip(all_positions, jordans):
            indexs = [position[0] for position in positions]
            nodes = [position[1] for position in positions]
            jordan.split(indexs, nodes)
        return jordans

    @staticmethod
    def interior_jordan_contains_point(jordan: JordanCurve, point: Point2D) -> bool:
        winding = FollowPath.winding_number(jordan, point)
        area = NumIntegration.area_inside_jordan(jordan)
        return winding == 1 if area > 0 else winding == 0

    @staticmethod
    def winding_number(jordan: JordanCurve, point: Point2D) -> int:
        """
        Computes the winding number of a point,
        It can be -1, 0 or 1
        """
        total = 0
        for bezier in jordan.segments:
            ctrlpoints = list(bezier.ctrlpoints)
            for i, ctrlpt in enumerate(ctrlpoints):
                ctrlpoints[i] = ctrlpt - point
            ctrlpoints = tuple(ctrlpoints)
            partial = NumIntegration.winding_number_bezier(ctrlpoints)
            total += partial
        return round(total)

    @staticmethod
    def unite_beziers(beziers: Tuple[nurbs.Curve]) -> nurbs.Curve:
        """
        Given a tuple of bezier curves, it returns a unique closed curve
        """
        beziers = list(beziers)
        nbeziers = len(beziers)
        for i, bezier in enumerate(beziers):
            degree = bezier.degree
            knotvector = sorted((degree + 1) * (i, i + 1))
            new_bezier = bezier.__class__(knotvector)
            new_bezier.ctrlpoints = bezier.ctrlpoints
            new_bezier.weights = bezier.weights
            beziers[i] = new_bezier
        final_curve = beziers[0]
        for i in range(1, nbeziers):
            final_curve |= beziers[i]
        final_curve.clean()
        return final_curve

    @staticmethod
    def index_segment_inside_other(jordana: JordanCurve, jordanb: JordanCurve) -> int:
        """
        Given two simple shapes, which intersect each other
        and they are already divided in their intersection
        The shape 'self' has at least one segment outside
        the region inside 'other'
        Then, this function returns the index such
            self.jordancurve.segments[index] is outside other
        """
        segments = jordana.segments
        index = 0
        while True:
            bezier = segments[index]
            knotvector = bezier.knotvector
            umin, umax = knotvector.limits
            mid_node = (umin + umax) / 2
            mid_point = segments[index].eval(mid_node)
            if FollowPath.interior_jordan_contains_point(jordanb, mid_point):
                return index
            index += 1

    @staticmethod
    def index_segment_outside_other(jordana: JordanCurve, jordanb: JordanCurve) -> int:
        """
        Given two simple shapes, which intersect each other
        and they are already divided in their intersection
        The shape 'self' has at least one segment outside
        the region inside 'other'
        Then, this function returns the index such
            self.jordancurve.segments[index] is outside other
        """
        segments = jordana.segments
        index = 0
        while True:
            bezier = segments[index]
            knotvector = bezier.knotvector
            umin, umax = knotvector.limits
            mid_node = (umin + umax) / 2
            mid_point = segments[index].eval(mid_node)
            if not FollowPath.interior_jordan_contains_point(jordanb, mid_point):
                return index
            index += 1

    @staticmethod
    def pursue_path(jordans: Tuple[JordanCurve], index: int) -> Tuple[Tuple[int]]:
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
        index_jordan = 0
        index_segment = index
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
    def outside_path(jordana: JordanCurve, jordanb: JordanCurve) -> JordanCurve:
        """
        Returns the union of two simple positive shapes
        """
        assert isinstance(jordana, JordanCurve)
        assert isinstance(jordanb, JordanCurve)
        jordans = [jordana, jordanb]
        jordans = FollowPath.split_at_intersections(jordans)
        jordana, jordanb = jordans
        index = FollowPath.index_segment_outside_other(jordana, jordanb)
        indexs_paths = FollowPath.pursue_path(jordans, index)
        final_beziers = [jordans[a].segments[b] for a, b in indexs_paths]
        final_curve = FollowPath.unite_beziers(final_beziers)
        final_jordan = JordanCurve(final_curve)
        return final_jordan

    @staticmethod
    def inside_path(jordana: JordanCurve, jordanb: JordanCurve) -> JordanCurve:
        """
        Returns the union of two simple positive shapes
        """
        assert isinstance(jordana, JordanCurve)
        assert isinstance(jordanb, JordanCurve)
        jordans = [jordana, jordanb]
        jordans = FollowPath.split_at_intersections(jordans)
        jordana, jordanb = jordans
        index = FollowPath.index_segment_inside_other(jordana, jordanb)
        indexs_paths = FollowPath.pursue_path(jordans, index)
        final_beziers = [jordans[a].segments[b] for a, b in indexs_paths]
        final_curve = FollowPath.unite_beziers(final_beziers)
        final_jordan = JordanCurve(final_curve)
        return final_jordan


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

    def __sub__(self, value: BaseShape):
        return self & (-value)

    def __mul__(self, value: BaseShape):
        return self & value

    def __xor__(self, other: BaseShape):
        return (self - other) | (other - self)

    def __bool__(self) -> bool:
        """
        Returns True if the curve's is positive
        Else if curve's area is negative
        """
        return float(self) > 0

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    def move(self, point: Point2D) -> BaseShape:
        point = Point2D(point)
        for jordan in self:
            jordan.move(point)
        return self

    def scale(self, xscale: float, yscale: float) -> BaseShape:
        for jordan in self:
            jordan.scale(xscale, yscale)
        return self

    def rotate(self, angle: float, degrees: bool = False) -> BaseShape:
        for jordan in self:
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

    def copy(self) -> BaseShape:
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
        if isinstance(other, EmptyShape):
            return self
        if isinstance(other, WholeShape):
            return EmptyShape()
        if isinstance(other, SimpleShape):
            return ConnectedShape(WholeShape(), [other])
        if isinstance(other, ConnectedShape):
            outside = WholeShape() - other.positive
            return DisjointShape([outside] + other.holes)
        raise NotImplementedError

    def copy(self) -> BaseShape:
        return self


class FiniteShape(BaseShape):
    def __init__(self, *args, **kwargs):
        pass

    def copy(self) -> BaseShape:
        return deepcopy(self)

    def __invert__(self) -> BaseShape:
        return WholeShape() - self


class SimpleShape(FiniteShape):
    """
    Simple class shape which is defined by only one jordan curve
    Example:
        - Interior of a circle, which jordan is in fact a circle
        - Interior of a polygon, which jordan are the edges
        - Exterior of a circle, when the jordan is a negative circle
    """

    def __init__(self, jordancurve: JordanCurve):
        assert isinstance(jordancurve, JordanCurve)
        self.jordancurve = jordancurve

    def __str__(self) -> str:
        area = float(self)
        vertices = self.jordancurve.vertices
        vertices = tuple([tuple(vertex) for vertex in vertices])
        msg = f"Simple Shape of area {area:.2f} with vertices:\n"
        msg += str(np.array(vertices, dtype="float64"))
        return msg

    def __repr__(self) -> str:
        area, vertices = float(self), self.jordancurve.vertices
        msg = f"Simple shape of area {area:.2f} with {len(vertices)} vertices"
        return msg

    def __float__(self) -> float:
        return float(self.__area)

    def __eq__(self, other: BaseShape) -> bool:
        if not isinstance(other, BaseShape):
            raise ValueError
        if not isinstance(other, SimpleShape):
            return False
        return self.jordancurve == other.jordancurve

    def __or__(self, other: BaseShape) -> BaseShape:
        assert isinstance(other, BaseShape)
        if not isinstance(other, SimpleShape):
            return other | self
        if self in other:
            return other.copy()
        if other in self:
            return self.copy()
        intersect = self.jordancurve.intersection(other.jordancurve, end_points=True)
        if intersect:
            newjordan = FollowPath.outside_path(self.jordancurve, other.jordancurve)
            return SimpleShape(newjordan)
        return DisjointShape([self.copy(), other.copy()])

    def __and__(self, other: BaseShape) -> BaseShape:
        assert isinstance(other, BaseShape)
        if not isinstance(other, SimpleShape):
            return other & self
        if self in other:
            return self.copy()
        if other in self:
            return other.copy()
        intersect = self.jordancurve.intersection(other.jordancurve, end_points=True)
        if intersect:
            newjordan = FollowPath.inside_path(self.jordancurve, other.jordancurve)
            return SimpleShape(newjordan)
        return EmptyShape()

    def __sub__(self, other: BaseShape) -> BaseShape:
        assert isinstance(other, BaseShape)
        if isinstance(other, EmptyShape):
            return self.copy()
        if isinstance(other, WholeShape):
            return EmptyShape()
        if not isinstance(other, SimpleShape):
            raise NotImplementedError
        if self in other:
            return EmptyShape()
        if other in self:
            return ConnectedShape(self, [other])
        intersect = self.jordancurve.intersection(other.jordancurve)
        if intersect:
            newjordan = FollowPath.inside_path(~other.jordancurve, self.jordancurve)
            return SimpleShape(newjordan)
        return EmptyShape()

    def __contains__(self, other: Union[Point2D, JordanCurve, BaseShape]) -> bool:
        if isinstance(other, EmptyShape):
            return True
        if isinstance(other, WholeShape):
            return False
        if isinstance(other, SimpleShape):
            return self.contains_simple_shape(other)
        if isinstance(other, ConnectedShape):
            return self.contains_connected_shape(other)
        if isinstance(other, DisjointShape):
            return self.contains_disjoint_shape(other)
        if isinstance(other, JordanCurve):
            return self.contains_jordan_curve(other)
        return self.contains_point(other)

    def __iter__(self):
        yield self.jordancurve

    @property
    def jordancurve(self) -> JordanCurve:
        return self.__jordancurve

    @jordancurve.setter
    def jordancurve(self, other: JordanCurve):
        assert isinstance(other, JordanCurve)
        area = NumIntegration.area_inside_jordan(other)
        if area < 0:
            raise ValueError("Simple Shape area must be always positive!")
        self.__jordancurve = other.copy()
        self.__area = area

    def contains_point(self, point: Point2D) -> bool:
        """
        We compute the winding number to determine if
        the point is inside the region.
        Uses numerical integration
        See wikipedia for details.
        """
        point = Point2D(point)
        if point in self.jordancurve:  # point in boundary
            return True
        return FollowPath.interior_jordan_contains_point(self.jordancurve, point)

    def contains_jordan_curve(self, other: JordanCurve) -> bool:
        assert isinstance(other, JordanCurve)
        for point in other.points(0):
            if not self.contains_point(point):
                return False
        return True

    def contains_simple_shape(self, other: SimpleShape) -> bool:
        assert isinstance(other, SimpleShape)
        if float(self) == float(other) and self == other:
            return True
        return other.jordancurve in self and self.jordancurve not in other

    def contains_connected_shape(self, other: ConnectedShape) -> bool:
        assert isinstance(other, ConnectedShape)
        return other.positive in self

    def contains_disjoint_shape(self, other: DisjointShape) -> bool:
        assert isinstance(other, DisjointShape)
        for subshape in other.subshapes:
            if subshape not in self:
                return False
        return True


class ConnectedShape(FiniteShape):
    """
    Class of connected shape
    This class stores, for example

        circle(radius = 2) - circle(radius = 1)

    Also stores the inversion of a simple shape

    """

    def __new__(
        cls, positive: Union[WholeShape, SimpleShape], holes: Tuple[SimpleShape]
    ):
        assert isinstance(positive, (WholeShape, SimpleShape))
        holes = list(holes)
        while EmptyShape() in holes:
            holes.remove(EmptyShape())
        if len(holes) == 0:
            return positive.copy()
        for hole in holes:
            assert isinstance(hole, SimpleShape)
            if hole not in positive:
                raise ValueError
        instance = super(ConnectedShape, cls).__new__(cls)
        instance.positive = positive
        instance.holes = holes
        return instance

    def contains_point(self, point: Point2D) -> bool:
        point = Point2D(point)
        if point not in self.positive:
            return False
        for hole in self.holes:
            if point in hole and point not in hole.jordancurve:
                return False
        return True

    def contains_jordan_curve(self, jordan: JordanCurve) -> bool:
        assert isinstance(jordan, JordanCurve)
        for point in jordan.points(0):
            if not self.contains_point(point):
                return False
        return True

    def contains_simple_shape(self, simple: SimpleShape) -> bool:
        assert isinstance(simple, SimpleShape)
        if simple not in self.positive:
            return False
        for hole in self.holes:
            if (hole in simple) ^ (simple in hole):
                return False
        return True

    def contains_connected_shape(self, connected: ConnectedShape) -> bool:
        assert isinstance(connected, ConnectedShape)
        if connected.positive not in self.positive:
            return False
        for hole in connected.holes:
            if not self.contains_jordan_curve(hole.jordancurve):
                return False
        return True

    def contains_disjoint_shape(self, disjoint: ConnectedShape) -> bool:
        assert isinstance(disjoint, DisjointShape)
        raise NotImplementedError

    def copy(self) -> ConnectedShape:
        holes = [hole.copy() for hole in self.holes]
        return ConnectedShape(self.positive.copy(), holes)

    def __or__simple_shape(self, other: SimpleShape) -> ConnectedShape:
        assert isinstance(other, SimpleShape)
        newpositive = self.positive | other
        newholes = []
        for hole in self.holes:
            newhole = hole - other
            if newhole is not EmptyShape():
                newholes.append(newhole)
        if isinstance(newholes, SimpleShape):
            newholes = tuple([newholes])
        elif isinstance(newholes, DisjointShape):
            newholes = tuple(newholes.subshapes)
        return ConnectedShape(newpositive, newholes)

    def __or__connected_shape(self, other: ConnectedShape) -> ConnectedShape:
        assert isinstance(other, ConnectedShape)
        newpositive = self.positive | other.positive
        if isinstance(newpositive, DisjointShape):
            return DisjointShape([self.copy(), other.copy()])
        newholes = []
        for hole in self.holes:
            newhole = hole - other.positive
            newholes.append(newhole)
        for hole in other.holes:
            newhole = hole - self.positive
            newholes.append(newhole)
        for holea in self.holes:
            for holeb in other.holes:
                newhole = holea & holeb
                newholes.append(newhole)
        return ConnectedShape(newpositive, newholes)

    def __and__simple_shape(self, other: SimpleShape) -> ConnectedShape:
        assert isinstance(other, SimpleShape)
        newshape = self.positive & other
        for hole in self.holes:
            newshape -= hole
        return newshape

    def __and__connected_shape(self, other: ConnectedShape) -> ConnectedShape:
        assert isinstance(other, ConnectedShape)
        newshape = self.positive & other.positive
        for hole in self.holes:
            newshape -= hole
        for hole in other.holes:
            newshape -= hole
        return newshape

    def __sub__simple_shape(self, other: SimpleShape) -> BaseShape:
        assert isinstance(other, SimpleShape)
        newshape = self.positive
        holes = other.copy()
        for hole in self.holes:
            holes |= hole
        return newshape - holes

    def __sub__connected_shape(self, other: ConnectedShape) -> BaseShape:
        assert isinstance(other, ConnectedShape)
        raise NotImplementedError

    def __sub__disjoint_shape(self, other: DisjointShape) -> BaseShape:
        assert isinstance(other, DisjointShape)
        raise NotImplementedError

    def __or__(self, other: BaseShape):
        assert isinstance(other, BaseShape)
        if isinstance(other, (EmptyShape, WholeShape, DisjointShape)):
            return other | self
        if isinstance(other, SimpleShape):
            return self.__or__simple_shape(other)
        if isinstance(other, ConnectedShape):
            return self.__or__connected_shape(other)
        raise NotImplementedError

    def __and__(self, other: BaseShape):
        assert isinstance(other, BaseShape)
        if isinstance(other, (EmptyShape, WholeShape, DisjointShape)):
            return other & self
        if isinstance(other, SimpleShape):
            return self.__and__simple_shape(other)
        if isinstance(other, ConnectedShape):
            return self.__and__connected_shape(other)
        raise NotImplementedError

    def __sub__(self, other: BaseShape):
        assert isinstance(other, BaseShape)
        if isinstance(other, EmptyShape):
            return self.copy()
        if isinstance(other, WholeShape):
            return EmptyShape()
        if isinstance(other, SimpleShape):
            return self.__sub__simple_shape(other)
        if isinstance(other, ConnectedShape):
            return self.__sub__connected_shape(other)
        if isinstance(other, DisjointShape):
            return self.__sub__disjoint_shape(other)

    def __contains__(self, other: Union[Point2D, JordanCurve, BaseShape]) -> bool:
        if isinstance(other, EmptyShape):
            return True
        if isinstance(other, WholeShape):
            return False
        if isinstance(other, SimpleShape):
            return self.contains_simple_shape(other)
        if isinstance(other, ConnectedShape):
            return self.contains_connected_shape(other)
        if isinstance(other, DisjointShape):
            return self.contains_disjoint_shape(other)
        if isinstance(other, JordanCurve):
            return self.contains_jordan_curve(other)
        return self.contains_point(other)

    def __float__(self) -> float:
        soma = 0
        if not isinstance(self.positive, WholeShape):
            soma += float(self.positive)
        for hole in self.holes:
            soma -= float(hole)
        return float(soma)

    def __str__(self) -> str:
        msg = f"Connected shape with {len(self.holes)} holes,"
        msg += f" total area {float(self)}.\n"
        msg += "Positive: " + str(self.positive) + "\n"
        msg += "Negative: " + str(self.holes) + "\n"
        return msg

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: BaseShape) -> bool:
        assert isinstance(other, BaseShape)
        if isinstance(other, (EmptyShape, WholeShape, SimpleShape)):
            return False
        if abs(float(self) - float(other)) > 1e-6:
            return False
        assert isinstance(other, ConnectedShape)
        if self.positive != other.positive:
            return False
        holesa = list(self.holes)
        holesb = list(other.holes)
        if len(holesa) != len(holesb):
            return False
        areasa = [float(hole) for hole in holesa]
        holesa = [hole for _, hole in sorted(zip(areasa, holesa))]
        areasb = [float(hole) for hole in holesb]
        holesb = [hole for _, hole in sorted(zip(areasb, holesb))]
        for holea in holesa:
            if holea not in holesb:
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
        pass

    def __or__(self, other: BaseShape) -> BaseShape:
        assert isinstance(other, BaseShape)
        raise NotImplementedError

    def __and__(self, other: BaseShape) -> BaseShape:
        assert isinstance(other, BaseShape)
        raise NotImplementedError

    def __sub__(self, other: BaseShape) -> BaseShape:
        assert isinstance(other, BaseShape)
        raise NotImplementedError
