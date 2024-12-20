"""
File to contains import of most important classes used in the package

Basically it allows importing like:

    from shapepy.curve import JordanPolygon
"""

from .polygon import JordanPolygon, PolygonClosedCurve, PolygonOpenCurve
from .spline import (
    JordanSpline,
    KnotVector,
    SplineClosedCurve,
    SplineOpenCurve,
)
