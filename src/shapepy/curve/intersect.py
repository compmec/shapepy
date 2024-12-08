from ..boolean import BoolOr
from ..core import Empty, IBoolean2D, ICurve
from .abc import IClosedCurve, IJordanCurve
from .polygon import PolygonClosedCurve, PolygonOpenCurve


def curve_and_curve(curvea: ICurve, curveb: ICurve) -> IBoolean2D:
    if not isinstance(curvea, ICurve):
        raise TypeError
    if not isinstance(curveb, ICurve):
        raise TypeError
    if isinstance(curvea, IJordanCurve) and isinstance(curveb, IJordanCurve):
        return jordan_and_jordan(curvea, curveb)
    if isinstance(curvea, IClosedCurve) and isinstance(curveb, IClosedCurve):
        return closed_and_closed(curvea, curveb)
    raise NotImplementedError(
        f"Not expected: {type(curvea)} and {type(curveb)}"
    )


def jordan_and_jordan(
    curvea: IJordanCurve, curveb: IJordanCurve
) -> IBoolean2D:
    if not isinstance(curvea, IJordanCurve):
        raise TypeError
    if not isinstance(curveb, IJordanCurve):
        raise TypeError
    return curve_and_curve(curvea.param_curve, curveb.param_curve)


def closed_and_closed(
    curvea: IClosedCurve, curveb: IClosedCurve
) -> IBoolean2D:
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


def polygon_and_polygon(
    curvea: PolygonClosedCurve, curveb: PolygonClosedCurve
) -> IBoolean2D:
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
    if not len(inters):
        return Empty()
    if len(inters) == 1:
        return inters[0]
    return BoolOr(inters)
