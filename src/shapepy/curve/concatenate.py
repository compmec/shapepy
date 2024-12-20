"""
This file contains the functions to concatenate open curves

It's used when, for a shape boolean intersection,
we find segments of differents curves to be used
"""
from .abc import IOpenCurve, IParameterCurve
from .piecewise import PiecewiseOpenCurve
from .polygon import PolygonOpenCurve
from .transform import transform_to_piecewise


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
    curves = map(transform_to_piecewise, curves)
    return concatenate_piecewise(*curves)


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


def concatenate_piecewise(*curves: PiecewiseOpenCurve) -> PiecewiseOpenCurve:
    """
    Concatenates the piecewise curve into only one polygon curve

    Parameters
    ----------
    curves: Iterable[PolygonOpenCurve]
        The open curves to be concatenated
    return: PolygonOpenCurve
        The concatenated final curve
    """
    curves = tuple(curves)
    if not all(isinstance(curve, PiecewiseOpenCurve) for curve in curves):
        raise TypeError
    for leftcurve, righcurve in zip(curves, curves[1:]):
        if righcurve.vertices[0] != leftcurve.vertices[-1]:
            raise ValueError("Cannot concatenate")
    allfunctions = []
    for curve in curves:
        allfunctions += list(curve.functions)
    return PiecewiseOpenCurve(allfunctions)
