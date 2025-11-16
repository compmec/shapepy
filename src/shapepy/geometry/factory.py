"""
Defines the Factory to create Jordan Curves
"""

from __future__ import annotations

import math
from typing import Iterable, Tuple

import numpy as np

from ..analytic import Bezier
from ..loggers import debug
from ..tools import To
from .jordancurve import JordanCurve
from .point import Point2D, cartesian, rotate
from .segment import Segment
from .unparam import USegment


# pylint: disable=too-few-public-methods
class FactorySegment:
    """
    Define functions to create Segments
    """

    @staticmethod
    @debug("shapepy.geometry.factory")
    def bezier(ctrlpoints: Iterable[Point2D]) -> Segment:
        """Initialize a bezier segment from a list of control points

        :param ctrlpoints: The list of control points
        :type ctrlpoints: Iterable[Point2D]
        :return: The created segment
        :rtype: Segment
        """
        ctrlpoints = tuple(map(To.point, ctrlpoints))
        xfunc = Bezier((pt[0] for pt in ctrlpoints))
        yfunc = Bezier((pt[1] for pt in ctrlpoints))
        return Segment(xfunc, yfunc)


class FactoryJordan:
    """
    Define functions to create Jordan Curves
    """

    @staticmethod
    @debug("shapepy.geometry.factory")
    def polygon(vertices: Tuple[Point2D, ...]) -> JordanCurve:
        """Initialize a polygonal JordanCurve from a list of vertices,

        :param vertices: The list vertices
        :type vertices: Tuple[Point2D]
        :return: The created jordan curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> from shapepy import JordanCurve
        >>> all_ctrlpoints = [(0, 0), (4, 0), (0, 3)]
        >>> FactoryJordan.polygon(all_ctrlpoints)
        Jordan Curve of degree 1 and vertices
        ((0, 0), (4, 0), (0, 3))

        """
        vertices = list(map(To.point, vertices))
        nverts = len(vertices)
        vertices.append(vertices[0])
        beziers = [None] * nverts
        for i in range(nverts):
            ctrlpoints = vertices[i : i + 2]
            new_bezier = FactorySegment.bezier(ctrlpoints)
            beziers[i] = USegment(new_bezier)
        return JordanCurve(beziers)

    @staticmethod
    @debug("shapepy.geometry.factory")
    def spline_curve(spline_curve) -> JordanCurve:
        """Initialize a JordanCurve from a spline curve,

        :param spline_curve: The spline curve to split.
                Ideally ``pynurbs.Curve`` instance
        :type spline_curve: SplineCurve
        :return: The created jordan curve
        :rtype: JordanCurve

        Example use
        -----------

        >>> import pynurbs
        >>> from shapepy import Point2D, JordanCurve
        >>> knotvector = (0, 0, 0, 0.5, 1, 1, 1)
        >>> ctrlpoints = [(0, 0), (4, 0), (0, 3), (0, 0)]
        >>> ctrlpoints = [cartesian(point
        ) for point in ctrlpoints]
        >>> curve = pynurbs.Curve(knotvector, ctrlpoints)
        >>> jordan = FactoryJordan.spline_curve(curve)
        >>> print(jordan)
        Jordan Curve of degree 2 and vertices
        ((0.0, 0.0), (4.0, 0.0), (2.0, 1.5), (0.0, 3.0))

        """
        beziers = spline_curve.split(spline_curve.knots)
        segments = (
            FactorySegment.bezier(bezier.ctrlpoints) for bezier in beziers
        )
        return JordanCurve(map(USegment, segments))

    @staticmethod
    @debug("shapepy.geometry.factory")
    def circle(ndivangle: int):
        """Creates a jordan curve that represents a unit circle"""
        angle = math.tau / ndivangle
        height = np.tan(angle / 2)

        start_point = cartesian(1, 0)
        middle_point = cartesian(1, height)
        all_ctrlpoints = []
        for _ in range(ndivangle - 1):
            end_point = rotate(start_point, angle)
            all_ctrlpoints.append([start_point, middle_point, end_point])
            start_point = end_point
            middle_point = rotate(middle_point, angle)
        end_point = all_ctrlpoints[0][0]
        all_ctrlpoints.append([start_point, middle_point, end_point])
        return JordanCurve(
            map(USegment, map(FactorySegment.bezier, all_ctrlpoints))
        )
