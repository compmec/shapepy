"""
Defines the Factory to create Jordan Curves
"""

from typing import Tuple

from ..tools import To
from .jordancurve import JordanCurve
from .point import Point2D
from .segment import Segment, clean_segment


class FactoryJordan:
    """
    Define functions to create Jordan Curves
    """

    @staticmethod
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
        beziers = [0] * nverts
        for i in range(nverts):
            ctrlpoints = vertices[i : i + 2]
            new_bezier = Segment(ctrlpoints)
            beziers[i] = new_bezier
        return JordanCurve(beziers)

    @staticmethod
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
            clean_segment(Segment(bezier.ctrlpoints)) for bezier in beziers
        )
        return JordanCurve(segments)
