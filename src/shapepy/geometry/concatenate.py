"""
Contains methods to concatenate curves
"""

from typing import Iterable, Union

from ..analytic import Bezier
from ..tools import Is, NotExpectedError
from .base import IGeometricCurve
from .piecewise import PiecewiseCurve
from .point import cross
from .segment import Segment
from .unparam import UPiecewiseCurve, USegment


def concatenate(curves: Iterable[IGeometricCurve]) -> IGeometricCurve:
    """
    Concatenates the given curves.

    Ignores all the curves parametrization
    """
    curves = tuple(curves)
    if not all(Is.instance(curve, IGeometricCurve) for curve in curves):
        raise ValueError
    if all(Is.instance(curve, Segment) for curve in curves):
        return concatenate_segments(curves)
    if all(Is.instance(curve, USegment) for curve in curves):
        return concatenate_usegments(curves)
    raise NotExpectedError(str(tuple(str(type(c)) for c in curves)))


def concatenate_usegments(
    usegments: Iterable[USegment],
) -> Union[USegment, UPiecewiseCurve]:
    """
    Concatenates all the unparametrized segments
    """
    usegments = tuple(usegments)
    assert all(Is.instance(useg, USegment) for useg in usegments)
    union = concatenate_segments(useg.parametrize() for useg in usegments)
    return (
        USegment(union)
        if Is.instance(union, Segment)
        else UPiecewiseCurve(map(USegment, union))
    )


def concatenate_segments(
    segments: Iterable[Segment],
) -> Union[Segment, PiecewiseCurve]:
    """
    Concatenates all the segments
    """
    segments = tuple(segments)
    if len(segments) == 0:
        raise ValueError(f"Number sizes: {len(segments)}")
    filtsegments = []
    segments = iter(segments)
    segmenti = next(segments)
    for segmentj in segments:
        try:
            segmenti = bezier_and_bezier(segmenti, segmentj)
        except ValueError:
            filtsegments.append(segmenti)
            segmenti = segmentj
    filtsegments.append(segmenti)
    print("filtsegments = ", filtsegments)
    return (
        PiecewiseCurve(filtsegments)
        if len(filtsegments) > 1
        else filtsegments[0]
    )


def bezier_and_bezier(curvea: Segment, curveb: Segment) -> Segment:
    """Computes the union of two bezier curves"""
    if not Is.instance(curvea, Segment):
        raise TypeError(f"Invalid type: {type(curvea)}")
    if not Is.instance(curveb, Segment):
        raise TypeError(f"Invalid type: {type(curveb)}")
    if abs(cross(curvea(1, 1), curveb(0, 1))) > 1e-6:
        raise ValueError
    if curvea.xfunc.degree != curveb.xfunc.degree:
        raise ValueError
    if curvea.yfunc.degree != curveb.yfunc.degree:
        raise ValueError
    if curvea.xfunc.degree > 1 or curvea.yfunc.degree > 1:
        raise ValueError

    if curvea(1) != curveb(0):
        raise ValueError
    startpoint = curvea(0)
    endpoint = curveb(1)
    nxfunc = Bezier((startpoint[0], endpoint[0]))
    nyfunc = Bezier((startpoint[1], endpoint[1]))
    return Segment(nxfunc, nyfunc)
