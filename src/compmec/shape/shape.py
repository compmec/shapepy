"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, List, Tuple, Union

import numpy as np

from compmec import nurbs
from compmec.shape.calculus import JordanCurveIntegral
from compmec.shape.jordancurve import JordanCurve
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
        return winding == 1 if jordan.lenght > 0 else winding == 0

    @staticmethod
    def winding_number(jordan: JordanCurve, point: Point2D) -> int:
        """
        Computes the winding number of a point,
        It can be -1, 0 or 1
        """
        jordan.move(-point)
        wind = JordanCurveIntegral.winding_number(jordan.segments)
        jordan.move(point)
        return wind

    @staticmethod
    def point_inside(point: Point2D, limiters: Tuple[JordanCurve]) -> bool:
        contains = FollowPath.interior_jordan_contains_point
        for limit in limiters:
            if not contains(limit, point):
                return False
        return True

    @staticmethod
    def midpoints_inclosed(
        jordan: JordanCurve, limiters: Tuple[JordanCurve]
    ) -> Tuple[bool]:
        """
        Given two list of jordan curves, named as As and Bs, this function returns a
        matrix of booleans which tells if the midpoint of each bezier is inside a region
        defined by Bs

        len(matrix) = len(As)
        len(matrix[i]) = len(As[i].segments)
        """
        assert isinstance(jordan, JordanCurve)
        assert isinstance(limiters, (tuple, list))
        for limit in limiters:
            assert isinstance(limit, JordanCurve)
        boolvector = []
        for bezier in jordan.segments:
            umin, umax = bezier.knotvector.limits
            mid_node = (umin + umax) / 2
            mid_point = bezier.eval(mid_node)
            inside = Contains.point_in_closed_jordan(mid_point, limiters)
            boolvector.append(inside)
        return tuple(boolvector)

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
    def switch_boolean(boolvector: Tuple[bool]) -> Tuple[int]:
        """
        Given an array of booleans, it returns the index such
        boolvectors switch from False to True
        It counts as a Deck, if it switch from last element to first

        Example:
        [F, F] -> []
        [T, T] -> []
        [F, T] -> [1]
        [F, T, F] -> [1]
        [F, T, F, F] -> [1]
        [T, F] -> [0]
        [T, T, F] -> [0]
        [T, F, T, F] -> [0, 2]
        """
        nvals = len(boolvector)
        results = []
        for i in range(nvals):
            if (not boolvector[i - 1]) and boolvector[i]:
                results.append(i)
        return tuple(results)

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
    def split_jordans(jordansa: Tuple[JordanCurve], jordansb: Tuple[JordanCurve]):
        for jordans in (jordansa, jordansb):
            assert isinstance(jordans, (tuple, list))
            for jordan in jordans:
                assert isinstance(jordan, JordanCurve)
        for jordana in jordansa:
            for jordanb in jordansb:
                FollowPath.split_at_intersections((jordana, jordanb))

    @staticmethod
    def union_indexs(
        jordansa: Tuple[JordanCurve], jordansb: Tuple[JordanCurve]
    ) -> Tuple[Tuple[Tuple[int]]]:
        """
        Function to find indexs for union_path
        """
        FollowPath.split_jordans(jordansa, jordansb)
        final_index_matrix = []
        all_jordans = jordansa + jordansb
        for k in range(2):
            jordans0 = jordansa if k == 0 else jordansb
            jordans1 = jordansb if k == 0 else jordansa
            for local_index_jordan, jordan in enumerate(jordans0):
                insiders = FollowPath.midpoints_inclosed(jordan, jordans1)
                outsiders = [not inside for inside in insiders]
                start_indexs = FollowPath.switch_boolean(outsiders)
                global_index_jordan = k * len(jordansa) + local_index_jordan
                for index_segment in start_indexs:
                    bezindexs = FollowPath.pursue_path(
                        global_index_jordan, index_segment, all_jordans
                    )
                    final_index_matrix.append(bezindexs)
        final_index_matrix = FollowPath.filter_rotations(final_index_matrix)
        return tuple(final_index_matrix)

    @staticmethod
    def intersection_indexs(
        jordansa: Tuple[JordanCurve], jordansb: Tuple[JordanCurve]
    ) -> Tuple[Tuple[Tuple[int]]]:
        """
        Function to find indexs for intersection_path
        """
        assert isinstance(jordansa, (tuple, list))
        assert isinstance(jordansb, (tuple, list))
        FollowPath.split_jordans(jordansa, jordansb)
        final_index_matrix = []
        all_jordans = jordansa + jordansb
        for k in range(2):
            jordans0 = jordansa if k == 0 else jordansb
            jordans1 = jordansb if k == 0 else jordansa
            for local_index_jordan, jordan in enumerate(jordans0):
                insiders = FollowPath.midpoints_inclosed(jordan, jordans1)
                start_indexs = FollowPath.switch_boolean(insiders)
                global_index_jordan = k * len(jordansa) + local_index_jordan
                for index_segment in start_indexs:
                    bezindexs = FollowPath.pursue_path(
                        global_index_jordan, index_segment, all_jordans
                    )
                    final_index_matrix.append(bezindexs)
        final_index_matrix = FollowPath.filter_rotations(final_index_matrix)
        return tuple(final_index_matrix)

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
            new_bezier = new_bezier.deepcopy()
            beziers.append(new_bezier)
        new_jordan = JordanCurve.from_segments(beziers)
        return new_jordan

    @staticmethod
    def union_path(
        jordansa: Tuple[JordanCurve], jordansb: Tuple[JordanCurve]
    ) -> Tuple[JordanCurve]:
        """
        Returns a list of jordan curves which is the result
        of the union between 'jordansa' and 'jordansb'
        """
        assert isinstance(jordansa, (tuple, list))
        assert isinstance(jordansb, (tuple, list))
        for jordan in jordansa:
            assert isinstance(jordan, JordanCurve)
        for jordan in jordansb:
            assert isinstance(jordan, JordanCurve)
        all_matrices_indexs = FollowPath.union_indexs(jordansa, jordansb)
        all_jordans = jordansa + jordansb
        new_jordans = []
        for matrix_indexs in all_matrices_indexs:
            jordan = FollowPath.indexs_to_jordan(all_jordans, matrix_indexs)
            new_jordans.append(jordan)
        return tuple(new_jordans)

    @staticmethod
    def intersection_path(
        jordansa: Tuple[JordanCurve], jordansb: Tuple[JordanCurve]
    ) -> Tuple[JordanCurve]:
        """
        Returns a list of jordan curves which is the result
        of the intersection between 'jordansa' and 'jordansb'
        """
        assert isinstance(jordansa, (tuple, list))
        assert isinstance(jordansb, (tuple, list))
        for jordan in jordansa:
            assert isinstance(jordan, JordanCurve)
        for jordan in jordansb:
            assert isinstance(jordan, JordanCurve)
        all_matrices_indexs = FollowPath.intersection_indexs(jordansa, jordansb)
        all_jordans = jordansa + jordansb
        new_jordans = []
        for matrix_indexs in all_matrices_indexs:
            jordan = FollowPath.indexs_to_jordan(all_jordans, matrix_indexs)
            new_jordans.append(jordan)
        return tuple(new_jordans)


class Contains:
    @staticmethod
    def point_at_jordan(point: Point2D, jordans: Tuple[JordanCurve]) -> bool:
        assert isinstance(point, Point2D)
        assert isinstance(jordans, (list, tuple))
        for jordan in jordans:
            assert isinstance(jordan, JordanCurve)
        for jordan in jordans:
            if point in jordan:
                return True
        return False

    @staticmethod
    def point_in_open_jordan(point: Point2D, jordans: Tuple[JordanCurve]) -> bool:
        assert isinstance(point, Point2D)
        assert isinstance(jordans, (list, tuple))
        for jordan in jordans:
            assert isinstance(jordan, JordanCurve)
        for jordan in jordans:
            wind = FollowPath.winding_number(jordan, point)
            if float(jordan) > 0 and wind != 1:
                return False
            if float(jordan) < 0 and wind != 0:
                return False
        return True

    @staticmethod
    def point_in_closed_jordan(point: Point2D, jordan: JordanCurve) -> bool:
        return Contains.point_at_jordan(point, jordan) or Contains.point_in_open_jordan(
            point, jordan
        )

    @staticmethod
    def point_in_shape(point: Point2D, shape: BaseShape) -> bool:
        assert isinstance(point, Point2D)
        assert isinstance(shape, BaseShape)
        if isinstance(shape, EmptyShape):
            return False
        if isinstance(shape, WholeShape):
            return True
        for jordan in shape.jordans:
            if point in jordan:  # Point in boundary
                return True
        if isinstance(shape, SimpleShape):
            return Contains.point_interior_jordan(point, shape.jordancurve)
        if isinstance(shape, ConnectedShape):
            for jordan in shape.jordans:
                if not Contains.point_interior_jordan(point, jordan):
                    return False
            return True
        if isinstance(shape, DisjointShape):
            for subshape in shape.subshapes:
                if Contains.point_in_shape(point, subshape):
                    return True
            return False
        raise NotImplementedError


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
        new_jordans = FollowPath.union_path([self.jordancurve], [other.jordancurve])
        simple_shapes = [SimpleShape(jordan) for jordan in new_jordans]
        return DisjointShape(simple_shapes)

    def __and__(self, other: BaseShape) -> BaseShape:
        assert isinstance(other, BaseShape)
        if not isinstance(other, SimpleShape):
            return other & self
        if self in other:
            return self.copy()
        if other in self:
            return other.copy()
        intersect = self.jordancurve.intersection(other.jordancurve, end_points=True)
        if not intersect:
            return EmptyShape()

        new_jordans = FollowPath.intersection_path(
            [self.jordancurve], [other.jordancurve]
        )
        simple_shapes = [SimpleShape(jordan) for jordan in new_jordans]
        assert len(simple_shapes) == 1
        return simple_shapes[0]

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
        if not intersect:
            return EmptyShape()
        new_jordans = FollowPath.intersection_path(
            [self.jordancurve], [~other.jordancurve]
        )
        simple_shapes = [SimpleShape(jordan) for jordan in new_jordans]
        assert len(simple_shapes) == 1
        return simple_shapes[0]

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
        if other.lenght < 0:
            raise ValueError("Simple Shape area must be always positive!")
        self.__jordancurve = other.copy()
        self.__area = JordanCurveIntegral.area(other.segments)

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
