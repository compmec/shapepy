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
from compmec.nurbs import Curve

from compmec import nurbs
from compmec.shape.jordancurve import JordanCurve
from compmec.shape.polygon import Point2D


class NumIntegration:
    @staticmethod
    def area(ctrlpoints: Tuple[Point2D]) -> float:
        """
        Computes the area equivalent from a bezier curve
        """
        degree = len(ctrlpoints) - 1
        knotvector = (degree + 1) * [0] + (degree + 1) * [1]
        px = nurbs.Curve(knotvector)
        px.ctrlpoints = [pt[0] for pt in ctrlpoints]
        py = nurbs.Curve(knotvector)
        py.ctrlpoints = [pt[1] for pt in ctrlpoints]
        dpy = nurbs.calculus.Derivate.bezier(py)
        pxdpy = px * dpy
        return sum(pxdpy.ctrlpoints) / (pxdpy.degree + 1)

    @staticmethod
    def winding_number_bezier(ctrlpoints: Tuple[Point2D]) -> float:
        """
        Computes the integral for a bezier curve of given control points
        """
        degree = len(ctrlpoints) - 1
        knotvector = [0] * (degree + 1) + [1] * (degree + 1)
        px = nurbs.Curve(knotvector, [pt[0] for pt in ctrlpoints])
        py = nurbs.Curve(knotvector, [pt[1] for pt in ctrlpoints])
        dpx = nurbs.calculus.Derivate.bezier(px)
        dpy = nurbs.calculus.Derivate.bezier(py)

        numer = px * dpy - py * dpx
        denom = px * px + py * py

        nintervals = 4 * (degree + 1)
        nptintegra = 4  # 3/8 simpson
        weights = np.array([1, 3, 3, 1], dtype="float64") / 8
        usample = np.linspace(0, 1, nintervals * (nptintegra - 1) + 1)
        numvals = np.array(numer(usample))
        denvals = denom(usample)
        funcvals = numvals / denvals
        integral = 0
        for i in range(nintervals):
            umin, umax = (
                usample[(nptintegra - 1) * i],
                usample[(nptintegra - 1) * (i + 1)],
            )
            # uvals = usample[(nptintegra-1)*i:(nptintegra-1)*(i+1)+1]
            fvals = funcvals[(nptintegra - 1) * i : (nptintegra - 1) * (i + 1) + 1]
            integral += np.dot(weights, fvals) * (umax - umin)
        return integral / (2 * np.pi)


class FollowPath:
    """
    Class responsible to compute the final jordan curve
    result from boolean operation between two simple shapes

    """

    @staticmethod
    def split_at_intersections(
        jordana: JordanCurve, jordanb: JordanCurve
    ) -> Tuple[JordanCurve]:
        inters = jordana & jordanb
        if len(inters) == 0:
            return jordana, jordanb
        nodes_self = set()
        nodes_other = set()
        for ui, vj in inters:
            nodes_self.add(ui)
            nodes_other.add(vj)
        nodes_self = tuple(sorted(nodes_self))
        nodes_other = tuple(sorted(nodes_other))
        jordana.split(nodes_self)
        jordanb.split(nodes_other)
        return jordana, jordanb

    @staticmethod
    def interior_jordan_contains_point(jordan: JordanCurve, point: Point2D) -> bool:
        winding = FollowPath.winding_number(jordan, point)
        area = FollowPath.area_inside_jordan(jordan)
        print("area = ", area)
        return winding == 1 if area > 0 else winding == 0

    @staticmethod
    def area_inside_jordan(jordan: JordanCurve) -> float:
        """
        Returns the area of the region defined by jordan
        If the jordan is negative, it returns the negative
        of the area
        """
        area = 0
        for segment in jordan.segments:
            area += NumIntegration.area(segment.ctrlpoints)
        return area

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
            total += NumIntegration.winding_number_bezier(ctrlpoints)
        return round(total)

    @staticmethod
    def unite_beziers(beziers: Tuple[nurbs.Curve]) -> nurbs.Curve:
        """
        Given a tuple of bezier curves, it returns a unique closed curve
        The final knotvector is not predictible
        """
        nbeziers = len(beziers)
        final_curve = beziers[0]
        for i in range(nbeziers - 1):
            umax_prev = final_curve.knotvector[-1]
            bezier1 = beziers[i + 1]
            knotvector1 = bezier1.knotvector
            umin_next = knotvector1[0]
            if umax_prev != umin_next:
                knotvector1.shift(umax_prev - umin_next)
                ctrlpoints = bezier1.ctrlpoints
                weights = bezier1.weights
                bezier1.ctrlpoints = None
                bezier1.weights = None
                bezier1.knotvector = knotvector1
                bezier1.ctrlpoints = ctrlpoints
                bezier1.weights = weights
            final_curve |= bezier1
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
    def continue_path(
        jordana: JordanCurve, jordanb: JordanCurve, index: int
    ) -> Tuple[nurbs.Curve]:
        """
        Given a two simple shapes, and a start path (given by index)
        it returns a list of segments that follows the 'flux'
        """
        final_beziers = []
        segmentsa = jordana.segments
        segmentsb = jordanb.segments
        while True:
            index %= len(segmentsa)
            segmenta = segmentsa[index]
            if segmenta in final_beziers:
                break
            final_beziers.append(segmenta)
            last_point = segmenta.ctrlpoints[-1]
            if last_point not in jordanb:
                index += 1
                continue
            for j, segj in enumerate(segmentsb):
                if segj.ctrlpoints[0] == last_point:
                    index = j
                    break
            jordana, jordanb = jordanb, jordana
            segmentsa, segmentsb = segmentsb, segmentsa
        return tuple(final_beziers)

    @staticmethod
    def outside_path(jordana: JordanCurve, jordanb: JordanCurve) -> JordanCurve:
        """
        Returns the union of two simple positive shapes
        """
        assert isinstance(jordana, JordanCurve)
        assert isinstance(jordanb, JordanCurve)
        jordana, jordanb = FollowPath.split_at_intersections(jordana, jordanb)
        index = FollowPath.index_segment_outside_other(jordana, jordanb)
        final_beziers = FollowPath.continue_path(jordana, jordanb, index)
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
        jordana, jordanb = FollowPath.split_at_intersections(jordana, jordanb)
        index = FollowPath.index_segment_inside_other(jordana, jordanb)
        final_beziers = FollowPath.continue_path(jordana, jordanb, index)
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
        print("XOR: ")
        print("self = ", self)
        print("other = ", other)
        return (self - other) | (other - self)

    def __bool__(self) -> bool:
        """
        Returns True if the curve's is positive
        Else if curve's area is negative
        """
        return float(self) > 0


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

    def __sub__(self, other: BaseShape) -> BaseShape:
        return ~other

    def __float__(self) -> float:
        return float("inf")

    def __invert__(self) -> BaseShape:
        return EmptyShape()

    def __contains__(self, other: BaseShape) -> bool:
        return True

    def copy(self) -> BaseShape:
        return self


class FiniteShape(BaseShape):
    def __abs__(self) -> BaseShape:
        """
        Returns the same curve, but in positive direction
        """
        return self.copy() if self else (~self)

    def copy(self) -> BaseShape:
        return deepcopy(self)


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
        if self.__area is None:
            self.__area = FollowPath.area_inside_jordan(self.jordancurve)
        return self.__area

    def __eq__(self, other: SimpleShape) -> bool:
        if not isinstance(other, SimpleShape):
            raise ValueError
        # if abs(float(self) - float(other)) > 1e-6:
        #     return False
        return self.jordancurve == other.jordancurve

    def __invert__(self) -> BaseShape:
        return ConnectedShape(WholeShape(), [self])

    def __or__(self, other: BaseShape) -> BaseShape:
        assert isinstance(other, BaseShape)
        if isinstance(other, (EmptyShape, WholeShape)):
            return other | self
        if isinstance(other, (ConnectedShape, DisjointShape)):
            return other | self
        assert isinstance(other, SimpleShape)
        assert float(other) > 0
        assert float(self) > 0
        if self in other:
            return other.copy()
        if other in self:
            return self.copy()
        intersect = self.jordancurve.intersect(other.jordancurve)
        if intersect:
            newjordan = FollowPath.outside_path(self.jordancurve, other.jordancurve)
            return SimpleShape(newjordan)
        # Disconnected shape
        raise NotImplementedError

    def __and__(self, other: BaseShape) -> BaseShape:
        assert isinstance(other, BaseShape)
        if isinstance(other, (EmptyShape, WholeShape)):
            return other & self
        if isinstance(other, (ConnectedShape, DisjointShape)):
            return other & self
        assert isinstance(other, SimpleShape)
        if self in other:
            return self.copy()
        if other in self:
            return other.copy()
        if self.jordancurve.intersect(other.jordancurve):
            newjordan = FollowPath.inside_path(self.jordancurve, other.jordancurve)
            return SimpleShape(newjordan)
        return EmptyShape()

    def __sub__(self, other: BaseShape) -> BaseShape:
        assert isinstance(other, BaseShape)
        if isinstance(other, EmptyShape):
            return self.copy()
        if isinstance(other, WholeShape):
            return EmptyShape()
        assert isinstance(other, SimpleShape)
        if self in other:
            raise EmptyShape()
        if other in self:
            return ConnectedShape(self, [other])
        intersect = self.jordancurve.intersect(other.jordancurve)
        if intersect:
            newjordan = FollowPath.inside_path(~other.jordancurve, self.jordancurve)
            return SimpleShape(newjordan)
        raise NotImplementedError

    def __contains__(self, other: Union[Point2D, JordanCurve, SimpleShape]) -> bool:
        if isinstance(other, EmptyShape):
            return True
        if isinstance(other, WholeShape):
            return False
        if isinstance(other, SimpleShape):
            return self.contains_simple_shape(other)
        if isinstance(other, JordanCurve):
            return self.contains_jordan_curve(other)
        return self.contains_point(other)

    @property
    def jordancurve(self) -> JordanCurve:
        return self.__jordancurve

    @jordancurve.setter
    def jordancurve(self, other: JordanCurve):
        assert isinstance(other, JordanCurve)
        self.__area = None
        self.__jordancurve = other.copy()

    def contains_point(self, point: Point2D) -> bool:
        """
        We compute the winding number to determine if
        the point is inside the region.
        Uses numerical integration
        See wikipedia for details.
        """
        assert float(self) > 0
        point = Point2D(point)
        if point in self.jordancurve:  # point in boundary
            return True
        return FollowPath.interior_jordan_contains_point(self.jordancurve, point)

    def contains_jordan_curve(self, other: JordanCurve) -> bool:
        assert isinstance(other, JordanCurve)
        points = other.points(0)
        for point in points:
            if not self.contains_point(point):
                return False
        return True

    def contains_simple_shape(self, other: SimpleShape) -> bool:
        assert isinstance(other, SimpleShape)
        if float(self) == float(other) and self == other:
            return True
        return other.jordancurve in self and self.jordancurve not in other

    def move(self, point: Point2D) -> BaseShape:
        self.jordancurve.move(point)
        return self

    def scale(self, xscale: float, yscale: float) -> BaseShape:
        self.jordancurve = self.jordancurve.scale(xscale, yscale)
        return self

    def rotate(self, angle: float, degrees: bool = False) -> BaseShape:
        self.jordancurve.rotate(angle, degrees)
        return self


class ConnectedShape(FiniteShape):
    """
    Class of connected shape
    This class stores, for example

        circle(radius = 2) - circle(radius = 1)

    Also stores the inversion of a simple shape

    """

    def __new__(cls, positive: SimpleShape, holes: Tuple[SimpleShape] = None):
        assert float(positive) > 0
        if not holes:
            return SimpleShape(positive)
        for hole in holes:
            assert float(hole) > 0
            if hole not in positive:
                raise ValueError
        new_instance = super(ConnectedShape, cls).__new__(cls)
        return new_instance

    def __init__(self, positive: SimpleShape, holes: Tuple[SimpleShape]):
        self.positive = positive
        self.holes = tuple(holes)

    def move(self, point: Point2D) -> BaseShape:
        self.jordancurve.move(point)
        return self

    def scale(self, xscale: float, yscale: float) -> BaseShape:
        self.jordancurve = self.jordancurve.scale(xscale, yscale)
        return self

    def rotate(self, angle: float, degrees: bool = False) -> BaseShape:
        self.jordancurve.rotate(angle, degrees)
        return self

    def invert(self) -> BaseShape:
        self.jordancurve = self.jordancurve.invert()
        return self

    def contains_point(self, point: Point2D) -> bool:
        point = Point2D(point)
        if point not in self.positive:
            return False
        for hole in self.holes:
            if point in hole and point not in hole.jordancurve:
                return False
        return False

    def contains_jordan_curve(self, jordan: JordanCurve) -> bool:
        assert isinstance(jordan, JordanCurve)
        points = jordan.points(0)
        for point in points:
            if not self.contains_point(point):
                return False
        return True

    def contains_simple_shape(self, simple: SimpleShape) -> bool:
        assert isinstance(simple, SimpleShape)
        if float(self) == float(simple) and self == simple:
            return True
        return simple.jordancurve in self and self.jordancurve not in simple

    def __or__possimple_negsimple(self, other: SimpleShape):
        assert isinstance(other, SimpleShape)
        raise NotImplementedError

    def __and__possimple_negsimple(self, other: SimpleShape):
        assert isinstance(other, SimpleShape)
        raise NotImplementedError

    def __or__(self, other: BaseShape):
        if isinstance(other, (EmptyShape, WholeShape)):
            return other | self
        if isinstance(other, DisjointShape):
            return other | self
        assert isinstance(other, (SimpleShape, ConnectedShape))
        if isinstance(other, SimpleShape):
            if self.positive is WholeShape():
                if len(self.holes) == 1:
                    self.__or__possimple_negsimple(self, other)
        raise NotImplementedError

    def __and__(self, other: BaseShape):
        if isinstance(other, (EmptyShape, WholeShape)):
            return other | self
        if isinstance(other, DisjointShape):
            return other | self
        assert isinstance(other, (SimpleShape, ConnectedShape))
        if isinstance(other, SimpleShape):
            if self.positive is WholeShape():
                if len(self.holes) == 1:
                    self.__and__possimple_negsimple(self, other)
        raise NotImplementedError

    def __contains__(self, other: Union[Point2D, JordanCurve, BaseShape]) -> bool:
        if isinstance(other, EmptyShape):
            return True
        if isinstance(other, WholeShape):
            return False
        if isinstance(other, ConnectedShape):
            raise NotImplementedError
        if isinstance(other, (Point2D, JordanCurve, BaseShape)):
            if other not in self.positive:
                return False
            for simple in self.holes:
                if other not in simple:
                    return False
            return True
        raise NotImplementedError


class DisjointShape(FiniteShape):
    def __new__(cls, connected_shapes: Tuple[Union[SimpleShape, ConnectedShape]]):
        for connected in connected_shapes:
            assert float(connected) > 0
        new_instance = super(DisjointShape, cls).__new__(cls)
        return new_instance
