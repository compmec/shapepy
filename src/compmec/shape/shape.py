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

    def __float__(self) -> float:
        return float(0)

    def __invert__(self) -> BaseShape:
        return WholeShape()

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

    def __invert__(self) -> BaseShape:
        return self.copy().invert()


class SimpleShape(FiniteShape):
    """
    Connected shape with no holes
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
            self.__area = 0
            jordancurve = self.jordancurve
            for segment in jordancurve.segments:
                self.__area += NumIntegration.area(segment.ctrlpoints)
        return self.__area

    def __eq__(self, other: SimpleShape) -> bool:
        if not isinstance(other, SimpleShape):
            raise ValueError
        if abs(float(self) - float(other)) > 1e-6:
            return False
        return self.jordancurve == other.jordancurve

    def __split_at_intersection(self, other: SimpleShape):
        """
        Given two shapes, this function computes the
        intersection between the two jordan curves and split each
        jordan curve at the intersections
        """
        jordan0, jordan1 = self.jordancurve, other.jordancurve
        inters = jordan0 & jordan1
        if len(inters) == 0:
            return
        nodes_self = set()
        nodes_other = set()
        for ui, vj in inters:
            nodes_self.add(ui)
            nodes_other.add(vj)
        nodes_self = tuple(sorted(nodes_self))
        nodes_other = tuple(sorted(nodes_other))
        self.jordancurve.split(nodes_self)
        other.jordancurve.split(nodes_other)

    def __get_segment_outside_other(self, other: SimpleShape) -> int:
        """
        Given two simple shapes, which intersect each other
        and they are already divided in their intersection
        The shape 'self' has at least one segment outside
        the region inside 'other'
        Then, this function returns the index such
            self.jordancurve.segments[index] is outside other
        """
        segments0 = self.jordancurve.segments
        index = 0
        while True:
            knotvector = segments0[index].knotvector
            umin, umax = knotvector.limits
            mid_node = (umin + umax) / 2
            mid_point = segments0[index].eval(mid_node)
            if not other.contains_point(mid_point):
                return index
            index += 1

    def __get_segment_inside_other(self, other: SimpleShape) -> int:
        """
        Given two simple shapes, which intersect each other
        and they are already divided in their intersection
        The shape 'self' has at least one segment outside
        the region inside 'other'
        Then, this function returns the index such
            self.jordancurve.segments[index] is outside other
        """
        segments0 = self.jordancurve.segments
        index = 0
        while True:
            knotvector = segments0[index].knotvector
            umin, umax = knotvector.limits
            mid_node = (umin + umax) / 2
            mid_point = segments0[index].eval(mid_node)
            if other.contains_point(mid_point):
                return index
            index += 1

    def __continue_path(self, other: SimpleShape, index: int) -> Tuple[nurbs.Curve]:
        """
        Given a two simple shapes, and a start path (given by index)
        it returns a list of segments that follows the 'flux'
        """
        shape0, shape1 = self, other
        jordan0, jordan1 = shape0.jordancurve, shape1.jordancurve
        final_beziers = []
        while True:
            segment0 = jordan0.segments[index]
            if segment0 in final_beziers:
                break
            final_beziers.append(segment0)
            last_point = segment0.ctrlpoints[-1]
            if last_point not in jordan1:  # shape1.contains_point(last_point):
                index += 1
                index %= len(jordan0.segments)
                continue
            for j, segj in enumerate(jordan1.segments):
                if segj.ctrlpoints[0] == last_point:
                    index = j
                    break
            shape0, shape1 = shape1, shape0
            jordan0, jordan1 = jordan1, jordan0
        return tuple(final_beziers)

    def __unite_beziers(self, final_beziers: Tuple[nurbs.Curve]):
        nbeziers = len(final_beziers)
        final_curve = final_beziers[0]
        for i in range(nbeziers - 1):
            umax_prev = final_curve.knotvector[-1]
            bezier1 = final_beziers[i + 1]
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

    def __outside_path(self, other: SimpleShape):
        """
        Returns the union of two simple positive shapes
        """
        assert isinstance(other, SimpleShape)
        self.__split_at_intersection(other)
        index = self.__get_segment_outside_other(other)
        final_beziers = self.__continue_path(other, index)
        final_curve = self.__unite_beziers(final_beziers)
        final_jordan = JordanCurve(final_curve)
        return self.__class__(final_jordan)

    def __inside_path(self, other: SimpleShape):
        """
        Returns the union of two simple positive shapes
        """
        assert isinstance(other, SimpleShape)
        self.__split_at_intersection(other)
        index = self.__get_segment_inside_other(other)
        final_beziers = self.__continue_path(other, index)
        final_curve = self.__unite_beziers(final_beziers)
        final_jordan = JordanCurve(final_curve)
        return self.__class__(final_jordan)

    def __or__(self, other: SimpleShape):
        if isinstance(other, (EmptyShape, WholeShape)):
            return other | self
        assert isinstance(other, SimpleShape)
        if self in other:
            return other.copy()
        if other in self:
            return self.copy()
        if other.jordancurve in self and self.jordancurve in other:
            return WholeShape()
        if other in (~self):
            # Disconnected shape
            raise NotImplementedError

        area_self = float(self)
        if area_self > 0:
            return self.__outside_path(other)
        else:  # area_self < 0
            return ~((~self) & (~other))

    def __and__(self, other: SimpleShape):
        if isinstance(other, (EmptyShape, WholeShape)):
            return other & self
        assert isinstance(other, SimpleShape)
        if self in other:
            return self.copy()
        if other in self:
            return other.copy()
        if other in (~self):
            return EmptyShape()
        if self.jordancurve in other and other.jordancurve in self:
            # Connected with holes
            raise NotImplementedError

        area_self = float(self)
        area_other = float(other)
        if area_self > 0:
            if area_other > 0:
                return self.__inside_path(other)
            else:
                return other.__inside_path(self)
        else:
            return ~((~self) | (~other))

    def __contains__(self, other: Union[Point2D, JordanCurve, SimpleShape]) -> bool:
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

    def __winding_number(self, point: Point2D) -> bool:
        """
        Says if the point is in the positive region defined
        """
        total = 0
        for bezier in self.jordancurve.segments:
            ctrlpoints = list(bezier.ctrlpoints)
            for i, ctrlpt in enumerate(ctrlpoints):
                ctrlpoints[i] = ctrlpt - point
            ctrlpoints = tuple(ctrlpoints)
            total += NumIntegration.winding_number_bezier(ctrlpoints)
        return round(total)

    def contains_point(self, point: Point2D) -> bool:
        """
        We compute the winding number to determine if
        the point is inside the region.
        Uses numerical integration
        See wikipedia for details.
        """
        point = Point2D(point)
        if point in self.jordancurve:  # point in boundary:
            return True
        winding = self.__winding_number(point)
        positive = bool(self)
        return winding == 1 if positive else winding == 0

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

    def invert(self) -> BaseShape:
        self.jordancurve = self.jordancurve.invert()
        return self


class ConnectedShape(FiniteShape):
    """
    An arbitrary 2D shape
    Methods:
        C = A + B : union (C = A cup B)
        C = A * B : intersection (C = A cap B)
        C = A - B : C = A - (A*B)
        C = B - A : C = B - (A*B)
        C = A ^ B : C = (A+B) - (A*B)

    Methods:
        move
        rotate
        scale (x or y or both)
    """

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

    def __contains__(self, other: Union[Point2D, JordanCurve, BaseShape]) -> bool:
        if isinstance(other, ConnectedShape):
            raise NotImplementedError
        if isinstance(other, (Point2D, JordanCurve, BaseShape)):
            for simple in self.holes + self.positive:
                if other not in simple:
                    return False
            return True
        raise NotImplementedError
