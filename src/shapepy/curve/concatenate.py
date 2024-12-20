"""
This file contains the functions to concatenate open curves

It's used when, for a shape boolean intersection,
we find segments of differents curves to be used
"""
from .abc import (
    IClosedCurve,
    ICurve,
    IJordanCurve,
    IOpenCurve,
    IParameterCurve,
)
from .polygon import JordanPolygon, PolygonClosedCurve, PolygonOpenCurve


def concatenate(*curves: IOpenCurve) -> IParameterCurve:
    """
    Concatenate all the open curves into only one

    Gives an error if they are not continuous

    Parameters
    ----------
    curves: Iterable[IOpenCurve]
        The curves to be united
    return: IParameterCurve
        The concatenated curve
    """
    curves = tuple(curves)
    for curve in curves:
        if not isinstance(curve, IOpenCurve):
            raise TypeError
    if all(isinstance(curve, PolygonOpenCurve) for curve in curves):
        return concatenate_polygon(*curves)
    raise NotImplementedError("Not expected get here")


def concatenate_polygon(*curves: PolygonOpenCurve) -> PolygonOpenCurve:
    """
    Concatenates the polygon curve into only one polygon curve

    Parameters
    ----------
    curves: Iterable[PolygonOpenCurve]
        The open curves to be concatenated
    return: PolygonOpenCurve
        The concatenated final curve
    """
    curves = tuple(curves)
    if not all(isinstance(curve, PolygonOpenCurve) for curve in curves):
        raise TypeError
    final = curves[0]
    for curve in curves[1:]:
        if final.vertices[-1] != curve.vertices[0]:
            raise ValueError
        vertices = list(final.vertices) + list(curve.vertices[1:])
        final = PolygonOpenCurve(vertices)
    return final


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
        raise ValueError
    if isinstance(curve, PolygonOpenCurve):
        return PolygonClosedCurve(curve.vertices[:-1])
    raise NotImplementedError("Not expected get here")


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
    if isinstance(curve, IJordanCurve):
        return curve
    if isinstance(curve, IOpenCurve):
        curve = closes_curve(curve)
    if isinstance(curve, PolygonClosedCurve):
        return JordanPolygon(curve.vertices)
    raise NotImplementedError("Not expected get here")
