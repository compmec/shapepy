"""
This file contains functions to computes the intersection
points of some curves, resulting either in:
* Empty : If the curves doesn't intersect each other
* Point2D : If the curves intersect only once
* ICurve : If there's infinite points between the curves
    meaning there's a side that is superposed
* BoolOr : The union of Point2D and ICurve
    It's used when there's more than one intersection point
    or if it's a mix of points and pieces of curves

"""

from ..boolean import BoolOr
from ..core import Empty, IBoolean2D
from .abc import IClosedCurve, ICurve, IJordanCurve
from .polygon import PolygonClosedCurve, PolygonOpenCurve


def curve_and_curve(curvea: ICurve, curveb: ICurve) -> IBoolean2D:
    """
    Computes the intersection of two arbitrary curves

    Parameters
    ----------
    curvea: ICurve
        The first curve
    curveb: ICurve
        The second curve
    return: IBoolean2D
        Either Empty, Point, ICurve or BoolOr
    """
    if not isinstance(curvea, ICurve):
        raise TypeError
    if not isinstance(curveb, ICurve):
        raise TypeError
    if isinstance(curvea, IClosedCurve) and isinstance(curveb, IClosedCurve):
        return closed_and_closed(curvea, curveb)
    if isinstance(curvea, IJordanCurve) and isinstance(curveb, IJordanCurve):
        return curve_and_curve(curvea.param_curve, curveb.param_curve)
    raise NotImplementedError(
        f"Not expected: {type(curvea)} and {type(curveb)}"
    )


def closed_and_closed(
    curvea: IClosedCurve, curveb: IClosedCurve
) -> IBoolean2D:
    """
    Computes the intersectioon of two closed curves

    Parameters
    ----------
    curvea: ICurve
        The first closed curve
    curveb: ICurve
        The second closed curve
    return: IBoolean2D
        Either Empty, Point, ICurve or BoolOr
    """
    if not isinstance(curvea, IClosedCurve):
        raise TypeError
    if not isinstance(curveb, IClosedCurve):
        raise TypeError
    if isinstance(curvea, PolygonClosedCurve) and isinstance(
        curveb, PolygonClosedCurve
    ):
        return polygon_and_polygon(curvea, curveb)
    raise NotImplementedError(
        f"Not expected: {type(curvea)} and {type(curveb)}"
    )


# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
def polygon_and_polygon(
    curvea: PolygonClosedCurve, curveb: PolygonClosedCurve
) -> IBoolean2D:
    """
    Computes the intersection of two polygon curves

    Parameters
    ----------
    curvea: PolygonClosedCurve
        The first curve
    curveb: PolygonClosedCurve
        The second curve
    return: IBoolean2D
        Either Empty, Point, ICurve or BoolOr
    """
    if not isinstance(curvea, PolygonClosedCurve):
        raise TypeError
    if not isinstance(curveb, PolygonClosedCurve):
        raise TypeError
    inters = []
    for i, avect in enumerate(curvea.vectors):
        avertex = curvea.vertices[i]
        for j, bvect in enumerate(curveb.vectors):
            bvertex = curveb.vertices[j]
            denom = bvect.cross(avect)
            diforigin = bvertex - avertex
            if denom != 0:  # Not Parallel lines
                tparam = bvect.cross(diforigin) / denom
                if tparam < 0 or 1 < tparam:
                    continue
                uparam = avect.cross(diforigin) / denom
                if uparam < 0 or 1 < uparam:
                    continue
                point = curvea.eval(i + tparam)
                inters.append(point)
                continue
            if avect.cross(diforigin):
                continue  # Not coincident lines
            paramc = avect.inner(diforigin) / avect.inner(avect)
            if paramc < 0 or 1 < paramc:
                continue
            paramd = avect.inner(diforigin + bvect) / avect.inner(avect)
            if paramd < 0 or 1 < paramd:
                continue
            if paramd < paramc:
                paramc, paramd = paramd, paramc
            pointc = avertex + paramc * avect
            pointd = avertex + paramd * avect
            segment = PolygonOpenCurve([pointc, pointd])
            inters.append(segment)
    if len(inters) == 0:
        return Empty()
    if len(inters) == 1:
        return inters[0]
    return BoolOr(inters)
