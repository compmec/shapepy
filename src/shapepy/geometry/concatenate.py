"""
Contains methods to concatenate curves
"""

from typing import Iterable, Union

from ..loggers import debug
from ..tools import Is, NotExpectedError, pairs
from .base import IGeometricCurve
from .piecewise import PiecewiseCurve
from .segment import Segment
from .unparam import UPiecewiseCurve, USegment


@debug("shapepy.geometry.concatenate")
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


@debug("shapepy.geometry.concatenate")
def concatenate_usegments(
    usegments: Iterable[USegment],
) -> Union[USegment, UPiecewiseCurve]:
    """
    Concatenates all the unparametrized segments
    """
    usegments = tuple(usegments)
    assert all(Is.instance(useg, USegment) for useg in usegments)
    segments = list(useg.parametrize() for useg in usegments)
    for i in range(len(segments) - 1):
        delta = segments[i].knots[-1] - segments[i + 1].knots[0]
        segments[i + 1] = segments[i + 1].shift(delta)

    union = concatenate_segments(segments)
    return (
        USegment(union)
        if Is.instance(union, Segment)
        else UPiecewiseCurve(map(USegment, union))
    )


@debug("shapepy.geometry.concatenate")
def concatenate_segments(
    segments: Iterable[Segment],
) -> Union[Segment, PiecewiseCurve]:
    """
    Concatenates all the segments
    """
    segments = tuple(segments)
    if len(segments) == 0:
        raise ValueError(f"Number sizes: {len(segments)}")
    for segi, segj in pairs(segments):
        if segi.knots[-1] != segj.knots[0]:
            raise ValueError(f"Invalid domains: {segi.domain}|{segj.domain}")
    filtsegments = []
    segments = iter(segments)
    segmenti = next(segments)
    for segmentj in segments:
        union = bezier_and_bezier(segmenti, segmentj)
        if union is None:
            filtsegments.append(segmenti)
            segmenti = segmentj
        else:
            segmenti = union
    filtsegments.append(segmenti)
    return (
        PiecewiseCurve(filtsegments)
        if len(filtsegments) > 1
        else filtsegments[0]
    )


@debug("shapepy.geometry.concatenate")
def bezier_and_bezier(curvea: Segment, curveb: Segment) -> Segment:
    """Computes the union of two bezier curves"""

    if (
        not Is.instance(curvea, Segment)
        or not Is.instance(curveb, Segment)
        or curvea.knots[-1] != curveb.knots[0]
        or curvea.xfunc != curveb.xfunc
        or curvea.yfunc != curveb.yfunc
    ):
        return None

    return Segment(curvea.xfunc, curveb.yfunc, curvea.domain | curveb.domain)
