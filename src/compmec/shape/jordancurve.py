"""
This modules contains a powerful class called JordanCurve which
is in fact, stores a list of spline-curves.
"""

import numpy as np
from compmec.nurbs import GeneratorKnotVector, SplineCurve


class JordanCurve:
    """
    Jordan Curve is an arbitrary closed curve which doesn't intersect itself.
    It stores a list of 'segments': Each 'segment' is a lambda function.
    The standard is to receive a list of points
    """

    def __init__(self, points: np.ndarray):
        self.segments = []
        knotvector = GeneratorKnotVector.bezier(1)
        for ctrlpoints in zip(points[:-1], points[1:]):
            splinecurve = SplineCurve(knotvector, ctrlpoints)
            self.segments.append(splinecurve)

    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        return not self == other

    def __neg__(self):
        raise NotImplementedError

    def __iter__(self):
        for segment in self.segments:
            yield segment

    def move(self, horizontal: float = 0, vertical: float = 0):
        """
        Move all the curve by an amount of (x, y)
        Example: move(1, 2)
            (0, 0) becomes (1, 2)
            (1, 2) becomes (2, 4)
            (1, 0) becomes (2, 2)
        """
        for segment in self:
            segment.ctrlpoints[:, 0] += horizontal
            segment.ctrlpoints[:, 1] += vertical
        return self

    def rotate_radians(self, angle: float):
        """
        Rotates counter-clockwise by an amount of 'angle' in radians
        Example: rotate(pi/2)
            (1, 0) becomes (0, 1)
            (2, 3) becomes (-3, 2)
        """
        cossinus, sinus = np.cos(angle), np.sin(angle)
        rotation_matrix = cossinus * np.eye(2)
        rotation_matrix[0, 1] = sinus
        rotation_matrix[1, 0] = -sinus
        for segment in self:
            for i, point in enumerate(segment.ctrlpoints):
                segment.ctrlpoints[i] = rotation_matrix @ point
        return self

    def rotate_degrees(self, angle: float):
        """
        Rotates counter-clockwise by an amount of 'angle' in degrees
        Example: rotate(90)
            (1, 0) becomes (0, 1)
            (2, 3) becomes (-3, 2)
        """
        return self.rotate_radians(np.pi * angle / 180)

    def scale(self, horizontal: float = 1, vertical: float = 1):
        """
        Scales the current curve by 'x' in x-direction and 'y' in y-direction
        Example: scale(1, 2)
            (1, 0) becomes (1, 0)
            (1, 3) becomes (1, 6)
        """
        for segment in self:
            segment.ctrlpoints[:, 0] *= horizontal
            segment.ctrlpoints[:, 1] *= vertical
        return self

    def invert(self):
        """
        Inverts the orientation of the jordan curve
        """
        self.segments = self.segments[::-1]
        for segment in self:
            segment.ctrlpoints = segment.ctrlpts[::-1]
        return self

    def deepcopy(self):
        """
        Creates a deep copy of all internal objects
        """
        newsegments = []
        for segment in self:
            ctrlpts = np.copy(segment.ctrlpts)
            knotvector = np.copy(segment.knot_vector)
            newsegments.append(SplineCurve(knotvector, ctrlpts))
        return self.__class__(newsegments)
