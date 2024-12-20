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
from .abc import ICurve
from .piecewise import PiecewiseCurve
from .polygon import PolygonCurve, PolygonOpenCurve
from .transform import transform_to_piecewise


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
    if isinstance(curvea, PolygonCurve) and isinstance(curveb, PolygonCurve):
        return polygon_and_polygon(curvea, curveb)
    if not isinstance(curvea, PiecewiseCurve):
        curvea = transform_to_piecewise(curvea)
    if not isinstance(curveb, PiecewiseCurve):
        curveb = transform_to_piecewise(curveb)
    return piecewise_and_piecewise(curvea, curveb)


# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
def polygon_and_polygon(
    curvea: PolygonCurve, curveb: PolygonCurve
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
    if not isinstance(curvea, PolygonCurve):
        raise TypeError
    if not isinstance(curveb, PolygonCurve):
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


# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
def piecewise_and_piecewise(
    curvea: PiecewiseCurve, curveb: PiecewiseCurve
) -> IBoolean2D:
    """
    Computes the intersection of two piecewise curves

    Parameters
    ----------
    curvea: PiecewiseCurve
        The first curve
    curveb: PiecewiseCurve
        The second curve
    return: IBoolean2D
        Either Empty, Point, ICurve or BoolOr
    """
    if not isinstance(curvea, PiecewiseCurve):
        raise TypeError
    if not isinstance(curveb, PiecewiseCurve):
        raise TypeError
    raise NotImplementedError
