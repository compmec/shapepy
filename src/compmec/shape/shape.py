"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""

from typing import List

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
        raise NotImplementedError

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
        for curve in self:
            if not curve.contains(other):
                return False
        return True
