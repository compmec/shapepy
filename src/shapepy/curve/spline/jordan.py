"""
This modules contains a powerful class called JordanCurve which
is in fact, stores a list of spline-curves.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np

from ...core import Scalar
from ...point import GeneralPoint, Point2D
from ..abc import IJordanCurve
from .knotvector import KnotVector
from .spline import SplineClosedCurve


class JordanSpline(IJordanCurve):
    """
    Jordan Curve is an arbitrary closed curve which doesn't intersect itself.
    It stores a list of 'segments', each segment is a bezier curve
    """

    def __init__(
        self,
        knotvector: KnotVector,
        ctrlpoints: Tuple[GeneralPoint],
    ):
        param_curve = SplineClosedCurve(knotvector, ctrlpoints)
        self.__param_curve = param_curve

    @property
    def knotvector(self) -> KnotVector:
        return self.param_curve.knotvector

    @property
    def ctrlpoints(self) -> Tuple[Point2D, ...]:
        return self.param_curve.ctrlpoints

    @property
    def param_curve(self) -> SplineClosedCurve:
        return self.__param_curve

    @property
    def lenght(self) -> Scalar:
        return self.param_curve.lenght

    @property
    def area(self) -> Scalar:
        return self.param_curve.area

    @property
    def vertices(self) -> Tuple[Point2D, ...]:
        raise NotImplementedError

    def move(self, vector: GeneralPoint) -> JordanSpline:
        """Translate the entire curve by ``point``

        :param point: The translation amount
        :type point: Point2D
        :return: The same curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = JordanPolygon(vertices)
        >>> jordan.move((2, 3))
        Jordan Curve of degree 1 and vertices
        ((2, 3), (6, 3), (2, 6))

        """
        if not isinstance(vector, Point2D):
            vector = Point2D(vector)
        ctrlpoints = tuple(point.move(vector) for point in self.ctrlpoints)
        self.__param_curve = SplineClosedCurve(self.knotvector, ctrlpoints)
        return self

    def scale(self, xscale: float, yscale: float) -> JordanSpline:
        """Scale the entire curve in horizontal and vertical direction

        :param xscale: The scale in horizontal direction
        :type xscale: float
        :param yscale: The scale in vertical direction
        :type yscale: float
        :return: The same curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = JordanPolygon(vertices)
        >>> jordan.scale(2, 3)
        Jordan Curve of degree 1 and vertices
        ((0, 0), (8, 0), (0, 9))
        >>> jordan.scale(1/2, 1/3)
        Jordan Curve of degree 1 and vertices
        ((0.0, 0.0), (4.0, 0.0), (0.0, 3.0))

        """
        float(xscale)
        float(yscale)
        ctrlpoints = tuple(
            point.scale(xscale, yscale) for point in self.ctrlpoints
        )
        self.__param_curve = SplineClosedCurve(self.knotvector, ctrlpoints)
        return self

    def rotate(self, angle: float, degrees: bool = False) -> JordanSpline:
        """Rotate the entire curve around the origin

        :param angle: The amount to rotate
        :type angle: float
        :param degrees: If the angle is in radians (``degrees=False``)
        :type degrees: bool(, optional)
        :return: The same curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> import math
        >>> from shapepy import JordanCurve
        >>> vertices = [(0, 0), (4, 0), (0, 3)]
        >>> jordan = JordanPolygon(vertices)
        >>> jordan.rotate(math.pi)
        Jordan Curve of degree 1 and vertices
        ((-0.0, 0.0), (-4.0, 4.899e-16), (-3.674e-16, -3.0))
        >>> jordan.rotate(180, degrees=True)
        Jordan Curve of degree 1 and vertices
        ((0.0, -0.0), (4.0, -9.797e-16), (7.348e-16, 3.0))

        """
        float(angle)
        if degrees:
            angle *= np.pi / 180
        ctrlpoints = tuple(point.rotate(angle) for point in self.ctrlpoints)
        self.__param_curve = SplineClosedCurve(self.knotvector, ctrlpoints)
        return self

    def __str__(self) -> str:
        degree, npts = self.knotvector.degree, self.knotvector.npts
        msg = f"Jordan Spline of degree {degree} and {npts} points\n"
        msg += str(self.vertices)
        return msg

    def __repr__(self) -> str:
        degree, npts = self.knotvector.degree, self.knotvector.npts
        return f"JordanCurve (deg {degree}, {npts})"
