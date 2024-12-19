from .abc import (
    IClosedCurve,
    ICurve,
    IJordanCurve,
    IOpenCurve,
    IParameterCurve,
)
from .polygon import JordanPolygon, PolygonClosedCurve, PolygonOpenCurve


def concatenate(*curves: IOpenCurve) -> IParameterCurve:
    curves = tuple(curves)
    for curve in curves:
        if not isinstance(curve, IOpenCurve):
            raise TypeError
    if all(isinstance(curve, PolygonOpenCurve) for curve in curves):
        return concatenate_polygon(*curves)
    raise NotImplementedError("Not expected get here")


def concatenate_polygon(*curves: PolygonOpenCurve) -> IParameterCurve:
    curves = tuple(curves)
    for curve in curves:
        if not isinstance(curve, PolygonOpenCurve):
            raise TypeError
    final = curves[0]
    for curve in curves[1:]:
        if final.vertices[-1] != curve.vertices[0]:
            raise ValueError
        vertices = list(final.vertices) + list(curve.vertices[1:])
        final = PolygonOpenCurve(vertices)
    return final


def closes_curve(curve: IOpenCurve) -> IClosedCurve:
    if not isinstance(curve, IOpenCurve):
        raise TypeError
    if curve.vertices[0] != curve.vertices[-1]:
        raise ValueError
    if isinstance(curve, PolygonOpenCurve):
        return PolygonClosedCurve(curve.vertices[:-1])
    raise NotImplementedError("Not expected get here")


def transform_to_jordan(curve: ICurve) -> IJordanCurve:
    if not isinstance(curve, ICurve):
        raise TypeError
    if isinstance(curve, IJordanCurve):
        return curve
    if isinstance(curve, IOpenCurve):
        curve = closes_curve(curve)
    if isinstance(curve, PolygonClosedCurve):
        return JordanPolygon(curve.vertices)
    raise NotImplementedError("Not expected get here")
