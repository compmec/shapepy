from ..analytic import Polynomial
from .abc import IClosedCurve, ICurve, IJordanCurve, IOpenCurve
from .piecewise import (
    JordanPiecewise,
    PiecewiseClosedCurve,
    PiecewiseCurve,
    PiecewiseOpenCurve,
)
from .polygon import JordanPolygon, PolygonClosedCurve, PolygonCurve


def transform_to_piecewise(curve: ICurve) -> PiecewiseCurve:
    """
    Transform the given curve into a PiecewiseCurve instance
    """
    if isinstance(curve, PolygonCurve):
        return polygon_to_piecewise(curve)
    if not isinstance(curve, PiecewiseCurve):
        raise NotImplementedError(f"Could not treat {curve}")
    return curve


def polygon_to_piecewise(curve: PolygonCurve) -> PiecewiseCurve:
    """
    Transform the given polygonal curve into a PiecewiseCurve instance
    """
    functions = []
    for i, (delx, dely) in enumerate(curve.vectors):
        posx, posy = curve.vertices[i]
        xpoly = Polynomial((posx - i * delx, delx))
        ypoly = Polynomial((posy - i * dely, dely))
        functions.append((xpoly, ypoly))
    if isinstance(curve, IJordanCurve):
        return JordanPiecewise(functions)
    if isinstance(curve, IClosedCurve):
        return PiecewiseClosedCurve(functions)
    return PiecewiseOpenCurve(functions)


def closes_curve(curve: IOpenCurve) -> IClosedCurve:
    """
    Transforms an open curve into a closed one

    Parameters
    ----------
    curve: IOpenCurve
        The open curve to be transformed
    return: IClosedCurve
        The closed curve
    """
    if not isinstance(curve, IOpenCurve):
        raise TypeError
    if curve.vertices[0] != curve.vertices[-1]:
        raise ValueError(f"Cannot close the curve {curve}")
    if isinstance(curve, PolygonCurve):
        return PolygonClosedCurve(curve.vertices[:-1])
    if isinstance(curve, PiecewiseCurve):
        return PiecewiseClosedCurve(curve.functions)
    raise NotImplementedError(f"Not expected get here with {curve}")


def transform_to_jordan(curve: ICurve) -> IJordanCurve:
    """
    Transforms an arbitrary curve into a jordan one

    This function closes the curve if it's open

    Parameters
    ----------
    curve: IOpenCurve
        The open curve to be transformed
    return: IClosedCurve
        The closed curve
    """
    if not isinstance(curve, ICurve):
        raise TypeError
    if isinstance(curve, IOpenCurve):
        curve = closes_curve(curve)
    if isinstance(curve, IJordanCurve):
        return curve
    if isinstance(curve, PolygonClosedCurve):
        return JordanPolygon(curve.vertices)
    if isinstance(curve, PiecewiseClosedCurve):
        return JordanPiecewise(curve.functions)
    raise NotImplementedError(f"Not expected get here with {curve}")
