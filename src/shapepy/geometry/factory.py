"""
Defines the Factory to create Jordan Curves
"""

from __future__ import annotations

import math
from typing import Iterable, Union

import numpy as np

from ..analytic import Bezier
from ..loggers import debug
from ..rbool import IntervalR1, from_any
from ..tools import To, pairs
from .jordancurve import JordanCurve
from .piecewise import PiecewiseCurve
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
    def bezier(
        ctrlpoints: Iterable[Point2D], domain: Union[None, IntervalR1] = None
    ) -> Segment:
        """Initialize a bezier segment from a list of control points

        :param ctrlpoints: The list of control points
        :type ctrlpoints: Iterable[Point2D]
        :return: The created segment
        :rtype: Segment
        """
        domain = IntervalR1(0, 1) if domain is None else from_any(domain)
        left = To.finite(domain[0])
        right = To.finite(domain[1])
        denom = right - left
        ctrlpoints = tuple(map(To.point, ctrlpoints))
        xfunc = (
            Bezier((pt[0] for pt in ctrlpoints))
            .clean()
            .scale(denom)
            .shift(left)
        )
        yfunc = (
            Bezier((pt[1] for pt in ctrlpoints))
            .clean()
            .scale(denom)
            .shift(left)
        )
        return Segment(xfunc, yfunc, domain)


# pylint: disable=too-few-public-methods
class FactoryPiecewise:
    """
    Define functions to create Segments
    """

    @staticmethod
    @debug("shapepy.geometry.factory")
    def polygonal(vertices: Iterable[Point2D]) -> PiecewiseCurve:
        """Initialize a piecewwise from given vertices

        :param vertices: The list of vertices
        :type vertices: Iterable[Point2D]
        :return: The created segment
        :rtype: PiecewiseCurve
        """
        vertices = tuple(map(To.point, vertices))
        return FactoryPiecewise.bezier(pairs(vertices))

    @staticmethod
    @debug("shapepy.geometry.factory")
    def bezier(all_ctrlpoints: Iterable[Iterable[Point2D]]) -> PiecewiseCurve:
        """Initialize a bezier segment from a list of control points

        :param ctrlpoints: The list of control points
        :type ctrlpoints: Iterable[Point2D]
        :return: The created segment
        :rtype: Segment
        """
        all_ctrlpoints = tuple(map(To.point, pts) for pts in all_ctrlpoints)

        segments = (
            FactorySegment.bezier(ctrlpoints, [i, i + 1])
            for i, ctrlpoints in enumerate(all_ctrlpoints)
        )
        return PiecewiseCurve(segments)


class FactoryJordan:
    """
    Define functions to create Jordan Curves
    """

    @staticmethod
    @debug("shapepy.geometry.factory")
    def polygon(vertices: Iterable[Point2D]) -> JordanCurve:
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
        vertices = list(vertices)
        vertices.append(vertices[0])
        return JordanCurve(FactoryPiecewise.polygonal(vertices))

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
        piecewise = FactoryPiecewise.bezier(
            bezier.ctrlpoints
            for bezier in spline_curve.split(spline_curve.knots)
        )
        return JordanCurve(piecewise)

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
