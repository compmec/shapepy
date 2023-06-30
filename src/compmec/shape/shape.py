"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""
from typing import List, Tuple

import numpy as np
from compmec.nurbs import SplineCurve

from compmec.shape.jordancurve import JordanCurve


class Shape:
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

    def contains(self, other) -> bool:
        """
        Returns if all the positive parts of 'other'
        are inside all the positive parts of 'self'
        Mathematically: A.contains(B) <=> A + B == A
        """
        if not isinstance(other, Shape):
            for curve in self:
                if not curve.contains(other):
                    return False
            return True

        return self.contains(other.curves[0])

    def omits(self, other) -> bool:
        """
        Returns if all the positive parts of 'other'
        are outside all the positive parts of 'self'
        Mathematically: A.omits(B) <=> A * B == None
        """
        if not isinstance(other, Shape):
            for curve in self:
                if not curve.omits(other):
                    return False
            return True
        return self.omits(other.curves[0])

    def intersects(self, other) -> bool:
        """
        Returns if there's at least one intersection
        Mathematically: A.intersects(B) <=> A * B != None
        """
        if not isinstance(other, Shape):
            for curve in self:
                if not curve.intersects(other):
                    return False
            return True
        return self.intersects(other.curves[0])


def intersection(segment0: SplineCurve, segment1: SplineCurve) -> Tuple:
    """
    Verifies if the segmentA touches the segmentB.
        segmentA is parametrized like A(t), 0 <= t <= 1
        segmentB is parametrized like B(u), 0 <= u <= 1
    Returns all the pairs (t, u) such A(t) == B(u)
        ((t0, u0), (t1, u1), ...)
    If there's no intersection, returns an empty Tuple

    This algorithm consider only linear segments.
    If SplineCurve.degree != 1, raises ValueError
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
