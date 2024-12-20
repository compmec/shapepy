"""
File to use import of most important classes used in the package

Basically it allows importing like:

    from shapepy.curve import JordanSpline
"""
from .knotvector import KnotVector
from .spline import JordanSpline, SplineClosedCurve, SplineOpenCurve
