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
        soma = 0
        jordancurve = self.jordancurve
        for segment in jordancurve.segments:
            soma += NumIntegration.area(segment.ctrlpoints)
        return soma

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
        if other in (~self):
            lista = [self.jordancurve, other.jordancurve]
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

        area_self = float(self)
        area_other = float(other)
        if area_self > 0:
            if area_other > 0:
                return self.__inside_path(other)
            else:
                return other.__inside_path(self)
        else:
            return ~((~self) | (~other))

    def __contains__(self, other: Union[Point2D, SimpleShape]) -> bool:
        if isinstance(other, SimpleShape):
            return self.contains_simple_shape(other)
        return self.contains_point(other)

    def contains_point(self, point: Point2D) -> bool:
        """
        We compute the winding number to determine if
        the point is inside the region.
        Uses numerical integration
        See wikipedia for details.
        """
        point = Point2D(point)
        jordancurve = self.jordancurve
        if point in jordancurve:  # point in boundary:
            return True
        total = 0
        for bezier in jordancurve.segments:
            ctrlpoints = list(bezier.ctrlpoints)
            for i, ctrlpt in enumerate(ctrlpoints):
                ctrlpoints[i] = ctrlpt - point
            ctrlpoints = tuple(ctrlpoints)
            total += NumIntegration.winding_number_bezier(ctrlpoints)
        return round(total) == 1

    def contains_simple_shape(self, other: SimpleShape) -> bool:
        assert isinstance(other, SimpleShape)
        jordancurve = other.jordancurve
        point = jordancurve.vertices[0]
        if not point in self:
            return False

    def move(self, point: Point2D) -> BaseShape:
        self.jordancurve.move(point)
        return self

    def scale(self, xscale: float, yscale: float) -> BaseShape:
        self.jordancurve.scale(xscale, yscale)
        return self

    def rotate(self, angle: float, degrees: bool = False) -> BaseShape:
        self.jordancurve.rotate(angle, degrees)
        return self

    def invert(self) -> BaseShape:
        self.jordancurve.invert()
        return self

    


class GeneralShape(FiniteShape):
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

    def __init__(self, curves: List[JordanCurve]):
        self.positivescurves = curves

    def move(self, horizontal: float = 0, vertical: float = 0):
        """
        Move all the curve by an amount of (x, y)
        Example: move(1, 2)
            (0, 0) becomes (1, 2)
            (1, 2) becomes (2, 4)
            (1, 0) becomes (2, 2)
        """
        for curve in self:
            curve.move(horizontal, vertical)
        return self

    def rotate_radians(self, angle: float):
        """
        Rotates counter-clockwise by an amount of 'angle' in radians
        Example: rotate(pi/2)
            (1, 0) becomes (0, 1)
            (2, 3) becomes (-3, 2)
        """
        for curve in self:
            curve.rotate_radians(angle)
        return self

    def rotate_degrees(self, angle: float):
        """
        Rotates counter-clockwise by an amount of 'angle' in degrees
        Example: rotate(90)
            (1, 0) becomes (0, 1)
            (2, 3) becomes (-3, 2)
        """
        for curve in self:
            curve.rotate_degrees(angle)
        return self

    def scale(self, horizontal: float = 1, vertical: float = 1):
        """
        Scales the current curve by 'x' in x-direction and 'y' in y-direction
        Example: scale(1, 2)
            (1, 0) becomes (1, 0)
            (1, 3) becomes (1, 6)
        """
        for curve in self:
            curve.scale(horizontal, vertical)
        return self

    def invert(self):
        """
        Inverts the orientation of all the jordan curves inside
        """
        for curve in self:
            curve.invert()

    def deepcopy(self):
        """
        Creates a deep copy of all internal objects
        """
        newcurves = [curve.deepcopy() for curve in self]
        newshape = self.__class__(newcurves)
        return newshape

    def __add__(self, other):
        raise NotImplementedError

    def __sub__(self, other):
        raise NotImplementedError

    def __mul__(self, other):
        raise NotImplementedError

    def __and__(self, other):
        raise NotImplementedError

    def __or__(self, other):
        raise NotImplementedError

    def __xor__(self, other):
        raise NotImplementedError

    def __neg__(self):
        raise NotImplementedError

    def __invert__(self):
        raise NotImplementedError

    def __eq__(self, other):
        """
        For the moment, only valid with one curves
        """
        return self.curves[0] == other.curves[0]

    def __ne__(self, other):
        return not self == other

    def __iter__(self):
        for curve in self.curves:
            yield curve

    def __contains__(self, other: object) -> bool:
        """
        Returns if all the positive parts of 'other'
        are inside all the positive parts of 'self'
        Mathematically: A.contains(B) <=> A + B == A
        """
        if isinstance(other, Shape):
            return other.curves[0] in self.curves[0]

        for curve in self:
            if other not in curve:
                return False
        return True


def add_2_intersect_jordan(curve0: JordanCurve, curve1: JordanCurve) -> Shape:
    """
    Given two jordan curves, and knowing they intersect each other,
    it returns a shape which is the sum of these two curves.
    This function doesn't check if there's intersection, it supposes.
    """
    nseg0 = len(curve0)
    nseg1 = len(curve1)

    matrix_intersection = np.zeros((nseg0, nseg1)).tolist()
    for i, segment_i in enumerate(curve0):
        for j, segment_j in enumerate(curve1):
            matrix_intersection[i][j] = intersection(segment_i, segment_j)


def add_two_jordan(curve0: JordanCurve, curve1: JordanCurve) -> Shape:
    """
    Receiving two jordan curves, we can add them togheter:
    - If A + B == A -> Returns A
    - If A + B == B -> Returns B
    - If A * B == None -> Returns A + B directly
    """
    if curve0.contains(curve1):
        return Shape([curve0.deepcopy()])
    if curve1.contains(curve0):
        return Shape([curve1.deepcopy()])

    return Shape([])


def intersection(segment0: Curve, segment1: Curve) -> Tuple:
    """
    Returns all the pairs (t, u) such A(t) == B(u)
        ((t0, u0), (t1, u1), ...)

        segmentA is parametrized like A(t), 0 <= t <= 1
        segmentB is parametrized like B(u), 0 <= u <= 1

    If there's no intersection, returns an empty Tuple

    This algorithm consider only linear segments.
    If Curve.degree != 1, raises ValueError
    """
    if segment0.degree != 1:
        raise ValueError
    if segment1.degree != 1:
        raise ValueError
    point0init, point0end = segment0.ctrlpoints
    point1init, point1end = segment1.ctrlpoints
    matrix = np.array([point0end - point0init, point1end - point1init]).T
    if np.linalg.det(matrix) < 1e-9:
        return tuple()  # Parallel lines, no solution
    force = point1init - point0init
    param0, param1 = np.linalg.solve(matrix, force)
    if param0 < 0 or 1 < param0:
        return tuple()  # Outside the interval of t
    if param1 < 0 or 1 < param1:
        return tuple()  # Outside the interval of u
    return tuple(((param0, param1),))
