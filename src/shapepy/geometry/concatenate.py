"""
Contains methods to concatenate curves
"""

from typing import Iterable, Union

from ..tools import Is, NotExpectedError
from .base import IGeometricCurve
from .piecewise import PiecewiseCurve
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
        return simplify_piecewise(PiecewiseCurve(curves))
    if all(Is.instance(curve, USegment) for curve in curves):
        return concatenate_usegments(curves)
    raise NotExpectedError(str(tuple(str(type(c)) for c in curves)))


def concatenate_usegments(
    usegments: Iterable[USegment],
) -> Union[USegment, UPiecewiseCurve]:
    """
    Concatenates all the unparametrized segments
    """
    union = simplify_piecewise(UPiecewiseCurve(usegments).parametrize())
    return (
        USegment(union)
        if Is.instance(union, Segment)
        else UPiecewiseCurve(union)
    )


def simplify_piecewise(
    piecewise: PiecewiseCurve,
) -> Union[Segment, PiecewiseCurve]:
    """
    Concatenates all the segments
    """
    filtsegments = []
    segments = iter(piecewise)
    segmenti = next(segments)
    for segmentj in segments:
        if can_concatenate(segmenti, segmentj):
            domain = segmenti.domain | segmentj.domain
            segmenti = Segment(segmenti.xfunc, segmenti.yfunc, domain=domain)
        else:
            filtsegments.append(segmenti)
            segmenti = segmentj
    filtsegments.append(segmenti)
    return (
        PiecewiseCurve(filtsegments)
        if len(filtsegments) > 1
        else filtsegments[0]
    )


def can_concatenate(curvea: Segment, curveb: Segment) -> bool:
    """Tells if it's possible to concatenate two segments into a single one"""
    return curvea.xfunc == curveb.xfunc and curvea.yfunc == curveb.yfunc
