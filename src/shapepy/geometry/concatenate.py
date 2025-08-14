"""
Contains methods to concatenate curves
"""

from typing import Iterable, Union

import pynurbs

from ..tools import Is, NotExpectedError, To
from .base import IParametrizedCurve
from .piecewise import PiecewiseCurve
from .point import cross, inner
from .segment import Segment


def concatenate(curves: Iterable[IParametrizedCurve]) -> IParametrizedCurve:
    """
    Concatenates the given curves.

    Ignores all the curves parametrization
    """
    curves = tuple(curves)
    if not all(Is.instance(curve, IParametrizedCurve) for curve in curves):
        raise ValueError
    # Check if the curves are connected
    for i, curvei in enumerate(curves[:-1]):
        curvej = curves[i + 1]
        if curvei(curvei.knots[-1]) != curvej(curvej.knots[0]):
            raise ValueError("The curves to concatenate are not connected")
    segments = []
    for curve in curves:
        if Is.instance(curve, Segment):
            segments.append(curve)
        elif Is.instance(curve, PiecewiseCurve):
            segments += list(curve)
        else:
            raise NotExpectedError(f"Unknown type: {type(curve)}")
    return concatenate_segments(segments)


def concatenate_segments(segments: Iterable[Segment]) -> IParametrizedCurve:
    """
    Concatenates all the segments
    """
    segments = list(segments)
    assert all(map(Is.segment, segments))
    filtsegments = []
    segment0 = segments.pop(0)
    while len(segments) > 0:
        segment1 = segments.pop(0)
        try:
            segment0 = bezier_and_bezier(segment0, segment1)
        except ValueError:
            filtsegments.append(segment0)
            segment0 = segment1
    filtsegments.append(segment0)
    try:
        union = bezier_and_bezier(filtsegments[-1], filtsegments[0])
        filtsegments.pop(0)
        filtsegments.pop()
        filtsegments.append(union)
    except ValueError:
        pass
    return (
        PiecewiseCurve(filtsegments)
        if len(filtsegments) > 1
        else filtsegments[0]
    )


def bezier_and_bezier(
    curvea: Segment, curveb: Segment
) -> Union[Segment, PiecewiseCurve]:
    """Computes the union of two bezier curves"""
    assert Is.instance(curvea, Segment)
    assert Is.instance(curveb, Segment)
    assert curvea.degree == curveb.degree
    if curvea.ctrlpoints[-1] != curveb.ctrlpoints[0]:
        raise ValueError
    # Last point of first derivative
    dapt = curvea.ctrlpoints[-1] - curvea.ctrlpoints[-2]
    # First point of first derivative
    dbpt = curveb.ctrlpoints[1] - curveb.ctrlpoints[0]
    if abs(cross(dapt, dbpt)) > 1e-6:
        node = To.rational(1, 2)
    else:
        dsumpt = dapt + dbpt
        denomin = inner(dsumpt, dsumpt)
        node = inner(dapt, dsumpt) / denomin
    knotvectora = pynurbs.GeneratorKnotVector.bezier(
        curvea.degree, To.rational
    )
    knotvectora.scale(node)
    knotvectorb = pynurbs.GeneratorKnotVector.bezier(
        curveb.degree, To.rational
    )
    knotvectorb.scale(1 - node).shift(node)
    newknotvector = tuple(knotvectora) + tuple(
        knotvectorb[curvea.degree + 1 :]
    )
    finalcurve = pynurbs.Curve(newknotvector)
    finalcurve.ctrlpoints = tuple(curvea.ctrlpoints) + tuple(curveb.ctrlpoints)
    finalcurve.knot_clean((node,))
    if finalcurve.degree + 1 != finalcurve.npts:
        raise ValueError("Union is not a bezier curve!")
    return Segment(finalcurve.ctrlpoints)
