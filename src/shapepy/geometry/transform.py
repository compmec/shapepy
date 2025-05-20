"""
Defines some functions to transform the geometric objects like:
* translating (move) a point or a curve
* rotate around the origin, a point or a curve
* scale a point or a curve
* reverse the orientation of a curve
"""

from numbers import Real
from typing import Tuple, Union

from .. import default
from ..angle import Angle, to_angle
from ..bool1d import infimum, supremum
from ..loggers import debug
from .curve import ContinuousCurve
from .point import GeometricPoint, geometric_point


@debug("shapepy.geometry.transform")
def move_point(
    point: GeometricPoint, vector: GeometricPoint
) -> GeometricPoint:
    """
    Moves the point by given vector

    Parameters
    ----------
    point: GeometricPoint
        -
    vector: GeometricPoint
        -

    Return
    ------
    GeometricPoint
        The moved point
    """
    point = geometric_point(point)
    vector = geometric_point(vector)
    return GeometricPoint.cartesian(point.x + vector.x, point.y + vector.y)


@debug("shapepy.geometry.transform")
def scale_point(
    point: GeometricPoint, amount: Union[Real, Tuple[Real, Real]]
) -> GeometricPoint:
    """
    Scales the point by given amount

    Parameters
    ----------
    point: GeometricPoint
        -
    amount: Union[Real, Tuple[Real, Real]]
        -

    Return
    ------
    GeometricPoint
        The scaled point
    """
    xamount = amount if default.isfinite(amount) else amount[0]
    yamount = amount if default.isfinite(amount) else amount[1]
    point = geometric_point(point)
    return GeometricPoint.cartesian(xamount * point.x, yamount * point.y)


@debug("shapepy.geometry.transform")
def rotate_point(point: GeometricPoint, angle: Angle) -> GeometricPoint:
    """
    Rotates the point around the origin by given angle

    Parameters
    ----------
    point: GeometricPoint
        -
    angle: Angle
        -

    Return
    ------
    GeometricPoint
        The rotated point
    """
    angle = to_angle(angle)
    point = geometric_point(point)
    if not isinstance(angle, Angle):
        raise TypeError
    cos, sin = angle.cos(), angle.sin()
    xval = cos * point.x - sin * point.y
    yval = sin * point.x + cos * point.y
    return GeometricPoint.cartesian(xval, yval)


@debug("shapepy.geometry.transform")
def move_curve(
    curve: ContinuousCurve, vector: GeometricPoint
) -> ContinuousCurve:
    """
    Moves the point by given vector

    Parameters
    ----------
    curve: ContinuousCurve
        -
    vector: GeometricPoint
        -

    Return
    ------
    ContinuousCurve
        The moved curve
    """
    vector = geometric_point(vector)
    new_xfunc = curve[0] + vector.x
    new_yfunc = curve[1] + vector.y
    return curve.__class__(new_xfunc, new_yfunc)


@debug("shapepy.geometry.transform")
def scale_curve(
    curve: ContinuousCurve, amount: Union[Real, Tuple[Real, Real]]
) -> ContinuousCurve:
    """
    Scales the curve by given amount

    Parameters
    ----------
    curve: ContinuousCurve
        -
    amount: Union[Real, Tuple[Real, Real]]
        -

    Return
    ------
    ContinuousCurve
        The scaled curve
    """
    xamount = amount if default.isfinite(amount) else amount[0]
    yamount = amount if default.isfinite(amount) else amount[1]
    new_xfunc = xamount * curve[0]
    new_yfunc = yamount * curve[1]
    return curve.__class__(new_xfunc, new_yfunc)


@debug("shapepy.geometry.transform")
def rotate_curve(curve: ContinuousCurve, angle: Angle) -> ContinuousCurve:
    """
    Rotates the curve around the origin by given angle

    Parameters
    ----------
    curve: ContinuousCurve
        -
    angle: Angle
        -

    Return
    ------
    ContinuousCurve
        The rotated curve
    """
    angle = to_angle(angle)
    cos, sin = angle.cos(), angle.sin()
    xfunc = cos * curve[0] - sin * curve[1]
    yfunc = sin * curve[0] + cos * curve[1]
    return curve.__class__(xfunc, yfunc)


@debug("shapepy.geometry.transform")
def reverse(curve: ContinuousCurve) -> ContinuousCurve:
    """
    Rotates the curve around the origin by given angle

    Parameters
    ----------
    curve: ContinuousCurve
        -

    Return
    ------
    ContinuousCurve
        The rotated curve
    """
    domain = curve[0].domain & curve[1].domain
    midpoint = (infimum(domain) + supremum(domain)) / 2
    newxfunc = curve[0].shift(-midpoint).scale(-1).shift(midpoint)
    newyfunc = curve[1].shift(-midpoint).scale(-1).shift(midpoint)
    return curve.__class__(newxfunc, newyfunc)
