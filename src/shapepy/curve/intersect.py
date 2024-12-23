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

from fractions import Fraction
from typing import Iterable, Set, Tuple

from ..boolean import BoolOr
from ..core import Empty, IAnalytic, IBoolean2D, Parameter, Scalar
from ..point import Point2D
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


class IntersectPoints:
    @staticmethod
    def curve_and_curve(curvea: ICurve, curveb: ICurve) -> Iterable[Point2D]:
        """
        Computes the intersection points between two curves
        """
        if not isinstance(curvea, ICurve):
            raise TypeError
        if not isinstance(curveb, ICurve):
            raise TypeError
        if isinstance(curvea, PolygonCurve) and isinstance(
            curveb, PolygonCurve
        ):
            return IntersectPoints.polygon_and_polygon(curvea, curveb)
        if not isinstance(curvea, PiecewiseCurve):
            curvea = transform_to_piecewise(curvea)
        if not isinstance(curveb, PiecewiseCurve):
            curveb = transform_to_piecewise(curveb)
        return IntersectPoints.piecewise_and_piecewise(curvea, curveb)

    @staticmethod
    def polygon_and_polygon(
        curvea: PolygonCurve, curveb: PolygonCurve
    ) -> Iterable[Point2D]:
        if not isinstance(curvea, PolygonCurve):
            raise TypeError
        if not isinstance(curveb, PolygonCurve):
            raise TypeError
        inters = set()
        for a, vectora in enumerate(curvea.vectors):
            vertexa = curvea.vertices[a]
            for b, vectorb in enumerate(curveb.vectors):
                vertexb = curveb.vertices[b]
                denom = vectorb.cross(vectora)
                diforigin = vertexb - vertexa
                if denom != 0:  # Not Parallel lines
                    tparam = vectorb.cross(diforigin) / denom
                    if tparam < 0 or 1 < tparam:
                        continue
                    uparam = vectora.cross(diforigin) / denom
                    if uparam < 0 or 1 < uparam:
                        continue
                    point = curvea.eval(a + tparam)
                    inters.add(tuple(point))
                    continue
                if vectora.cross(diforigin):
                    continue  # Not coincident lines
                paramc = vectora.inner(diforigin)
                paramc /= vectora.inner(vectora)
                if paramc < 0 or 1 < paramc:
                    continue
                paramd = vectora.inner(diforigin + vectorb)
                paramd /= vectora.inner(vectora)
                if paramd < 0 or 1 < paramd:
                    continue
                if paramd < paramc:
                    paramc, paramd = paramd, paramc
                inters.add(tuple(vertexa + paramc * vectora))
                inters.add(tuple(vertexa + paramd * vectora))
        return map(Point2D, inters)

    @staticmethod
    def piecewise_and_piecewise(
        curvea: PiecewiseCurve, curveb: PiecewiseCurve
    ) -> Iterable[Point2D]:
        if not isinstance(curvea, PiecewiseCurve):
            raise TypeError
        if not isinstance(curveb, PiecewiseCurve):
            raise TypeError

        inters = set()
        for a, (axf, ayf) in enumerate(curvea.functions):
            ainf, asup = curvea.knots[a], curvea.knots[a + 1]
            apack = (axf, ayf, ainf, asup)
            for b, (bxf, byf) in enumerate(curveb.functions):
                binf, bsup = curveb.knots[b], curveb.knots[b + 1]
                bpack = (bxf, byf, binf, bsup)
                inters |= IntersectPoints.pack_and_pack(apack, bpack)
        return map(Point2D, inters)

    @staticmethod
    def pack_and_pack(
        apack: Tuple[IAnalytic, IAnalytic, Parameter, Parameter],
        bpack: Tuple[IAnalytic, IAnalytic, Parameter, Parameter],
    ) -> Set[Tuple[Scalar, Scalar]]:
        axf, ayf, ainf, asup = apack
        bxf, byf, binf, bsup = bpack
        otipos = {type(axf), type(ayf), type(bxf), type(byf)}
        if len(otipos) == 1:
            raise ValueError(f"Not expected be here: {otipos}")

        def newton(
            aknot: Parameter, bknot: Parameter
        ) -> Tuple[Parameter, Parameter]:
            delx = axf(aknot) - bxf(bknot)
            dely = ayf(aknot) - byf(bknot)
            dax, day = axf.eval(aknot, 1), ayf.eval(aknot, 1)
            dbx, dby = bxf.eval(bknot, 1), byf.eval(bknot, 1)
            ddax, dday = axf.eval(aknot, 2), ayf.eval(aknot, 2)
            ddbx, ddby = bxf.eval(bknot, 2), byf.eval(bknot, 2)
            mat00 = dax**2 + day**2 + ddax * delx + dday * dely
            mat11 = dbx**2 + dby**2 - ddbx * delx - ddby * dely
            mat01 = dax * dbx + day * dby
            denom = mat00 * mat11 - mat01**2
            if denom == 0:
                return 0, 0
            vec0 = dax * delx + day * dely
            vec1 = dbx * delx + dby * dely
            dela = (mat11 * vec0 - mat01 * vec1) / denom
            delb = (mat01 * vec0 - mat00 * vec1) / denom
            dela = max(ainf + aknot, min(asup + aknot, dela))
            delb = max(binf + bknot, min(bsup + bknot, delb))
            return dela, delb

        ndivs = 16
        aknots = tuple(Fraction(i, ndivs) for i in range(ndivs + 1))
        bknots = tuple(Fraction(i, ndivs) for i in range(ndivs + 1))
        inters = set()
        for i in range(ndivs + 1):
            for bknot in bknots:
                aknot = aknots[i]
                for _ in range(4):  # Newton iteration
                    dela, delb = newton(aknot, bknot)
                    if not (dela or delb):
                        break
                    aknot = max(0, min(1, aknot - dela))
                    bknot = max(0, min(1, bknot - delb))
                axv = axf(aknot)
                ayv = ayf(aknot)
                bxv = bxf(bknot)
                byv = byf(bknot)
                if (axv - bxv) ** 2 + (ayv - byv) ** 2 < 1e-6:
                    inters.add((axv, ayv))
        return inters
