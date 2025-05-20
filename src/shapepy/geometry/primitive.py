"""
File that contains the functions to create the geometric curve for the
primitive types, such as polygon and circle
"""

from typing import Iterable

from .. import default
from ..analytic.elementar import linear_piecewise
from .abc import IJordanCurve
from .curve import JordanCurve
from .point import GeometricPoint, geometric_point


def polygon(vertices: Iterable[GeometricPoint]) -> IJordanCurve:
    """
    Gives the polygonal curve defined by given vertices
    """
    vertices = tuple(map(geometric_point, vertices))
    knots = tuple(map(default.finite, range(len(vertices) + 1)))
    xvalues = list(vertex.x for vertex in vertices)
    yvalues = list(vertex.y for vertex in vertices)
    xvalues.append(xvalues[0])
    yvalues.append(yvalues[0])
    xanalytic = linear_piecewise(xvalues, knots)
    yanalytic = linear_piecewise(yvalues, knots)
    return JordanCurve(xanalytic, yanalytic)
