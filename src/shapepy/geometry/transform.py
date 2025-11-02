"""Contains some functions that are able to transform the curves,
doing operations such as moving, scaling or rotating"""

from typing import Tuple, Union

from ..scalar.angle import Angle
from ..scalar.reals import Real
from ..tools import Is, NotExpectedError, To
from .base import IGeometricCurve, IParametrizedCurve
from .piecewise import PiecewiseCurve
from .point import Point2D
from .segment import Segment


def move(curve: IGeometricCurve, vector: Point2D) -> IGeometricCurve:
    """
    Moves/translate entire shape by an amount

    Parameters
    ----------

    point : Point2D
        The amount to move

    :return: The same instance
    :rtype: SubSetR2

    Example use
    -----------
    >>> from shapepy import Primitive
    >>> circle = Primitive.circle()
    >>> circle.move(1, 2)

    """
    vector = To.point(vector)
    if Is.instance(curve, Segment):
        newxfunc = curve.xfunc + vector.xcoord
        newyfunc = curve.yfunc + vector.ycoord
        return Segment(newxfunc, newyfunc)
    if Is.instance(curve, PiecewiseCurve):
        newsegs = (move(seg, vector) for seg in curve)
        return PiecewiseCurve(newsegs, curve.knots)
    if not Is.instance(curve, IParametrizedCurve):
        return curve.__class__(move(curve.parametrize(), vector))
    raise NotExpectedError(f"Invalid typo: {type(curve)}")


def scale(
    curve: IGeometricCurve, amount: Union[Real, Tuple[Real, Real]]
) -> IGeometricCurve:
    """
    Scales entire subset by an amount

    Parameters
    ----------

    amount : Real | Tuple[Real, Real]
        The amount to scale in horizontal and vertical direction

    :return: The same instance
    :rtype: SubSetR2

    Example use
    -----------
    >>> from shapepy import Primitive
    >>> circle = Primitive.circle()
    >>> circle.scale(2, 3)

    """
    if Is.instance(curve, Segment):
        newxfunc = curve.xfunc * (amount if Is.real(amount) else amount[0])
        newyfunc = curve.yfunc * (amount if Is.real(amount) else amount[1])
        return Segment(newxfunc, newyfunc)
    if Is.instance(curve, PiecewiseCurve):
        newsegs = (scale(seg, amount) for seg in curve)
        return PiecewiseCurve(newsegs, curve.knots)
    if not Is.instance(curve, IParametrizedCurve):
        return curve.__class__(scale(curve.parametrize(), amount))
    raise NotExpectedError(f"Invalid typo: {type(curve)}")


def rotate(curve: IGeometricCurve, angle: Angle) -> IGeometricCurve:
    """
    Rotates entire curve around the origin by given angle

    Parameters
    ----------

    angle : Angle
        The amount to rotate around origin

    :return: The same instance
    :rtype: SubSetR2

    Example use
    -----------
    >>> from shapepy import Primitive
    >>> circle = Primitive.circle()
    >>> circle.rotate(degrees(90))

    """
    angle = To.angle(angle)
    if Is.instance(curve, Segment):
        cos, sin = angle.cos(), angle.sin()
        newxfunc = cos * curve.xfunc - sin * curve.yfunc
        newyfunc = sin * curve.xfunc + cos * curve.yfunc
        return Segment(newxfunc, newyfunc)
    if Is.instance(curve, PiecewiseCurve):
        newsegs = (rotate(seg, angle) for seg in curve)
        return PiecewiseCurve(newsegs, curve.knots)
    if not Is.instance(curve, IParametrizedCurve):
        return curve.__class__(rotate(curve.parametrize(), angle))
    raise NotExpectedError(f"Invalid typo: {type(curve)}")
