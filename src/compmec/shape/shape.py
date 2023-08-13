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

from compmec.shape.jordancurve import JordanCurve
from compmec.shape.polygon import Point2D


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
        return self & (~value)

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

    def __abs__(self) -> BaseShape:
        """
        Returns the same curve, but in positive direction
        """
        return self.copy() if self else (~self)

    def copy(self) -> BaseShape:
        return deepcopy(self)


class EmptyShape(BaseShape):
    """
    A class to represent a empty shape, the zero element
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is not None:
            return cls.__instance
        return super(EmptyShape, cls).__new__(cls)

    def __or__(self, other: BaseShape) -> BaseShape:
        return other.copy()

    def __and__(self, other: BaseShape) -> BaseShape:
        return self

    def __float__(self) -> float:
        return 0

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
        if cls.__instance is not None:
            return cls.__instance
        return super(WholeShape, cls).__new__(cls)

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
    def __invert__(self) -> BaseShape:
        raise NotImplementedError

    def __float__(self) -> float:
        return sum([float(shape) for shape in self.subshapes])

    def move(self, point: Point2D) -> BaseShape:
        self.subshapes = [shape.move(point) for shape in self.subshapes]
        return self

    def scale(self, xscale: float, yscale: float) -> BaseShape:
        self.subshapes = [shape.scale(xscale, yscale) for shape in self.subshapes]
        return self

    def rotate(self, angle: float, degrees: bool = False) -> BaseShape:
        self.subshapes = [shape.rotate(angle, degrees) for shape in self.subshapes]
        return self

    def invert(self) -> BaseShape:
        self.subshapes = [shape.invert() for shape in self.subshapes]
        return self


class SimpleShape(BaseShape):
    """
    Connected shape with no holes
    """

    def __init__(self, jordancurve: JordanCurve):
        self.subshapes = [jordancurve]

    def __union_simple_shapes(self, other: SimpleShape):
        assert isinstance(other, SimpleShape)
        if self in other:
            return other.copy()
        if other in self:
            return self.copy()
        if other in (~self):
            lista = [self.subshapes[0], other.subshapes[0]]
            return DisconnectedShape(lista)

    def __or__(self, other: BaseShape):
        raise NotImplementedError


class ConnectedShape(BaseShape):
    """
    A connected shape with holes
    """

    def __init__(self):
        pass


class DisconnectedShape(BaseShape):
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
        self.curves = curves

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
