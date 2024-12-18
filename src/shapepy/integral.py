"""
This file contains the functions to compute the integrals
over the package's objects, like shapes and curves
"""
from typing import Tuple

from .core import IShape, Scalar
from .curve.polygon import JordanPolygon
from .curve.polygon.integral import polybidim
from .shape import ConnectedShape, DisjointShape, SimpleShape


def polynomial(shape: IShape, exponents: Tuple[int, int]) -> Scalar:
    """
    Computes the polynomial integral in the given shape

    I = int_{S} x^{a} * y^{b} dx dy

    Parameters
    ----------
    shape: IShape
        The shape which we must compute the integral
    exponents: tuple[int, int]
        The pair of exponents (a, b), must be positives

    Example
    -------
    >>> myshape = Primitive.square(side=4)
    >>> polynomial(myshape, (0, 0))  # area
    16
    """
    if not isinstance(shape, IShape):
        raise TypeError
    if isinstance(shape, (ConnectedShape, DisjointShape)):
        return sum(polynomial(sub, exponents) for sub in shape)
    if not isinstance(shape, SimpleShape):
        raise TypeError
    expx, expy = exponents
    if isinstance(shape.jordan, JordanPolygon):
        vertices = shape.jordan.vertices
        vertices = tuple(map(tuple, vertices))
        return polybidim(vertices, expx, expy)

    curve = shape.jordan.param_curve
    soma = 0
    for i, (xfunc, yfunc) in enumerate(curve.functions):
        cross = xfunc * yfunc.derivate(1) - yfunc * xfunc.derivate(1)
        ifunc = (xfunc**expx) * (yfunc**expy) * cross
        soma += ifunc.defintegral(i, i + 1)
    soma /= expx + expy + 2
    return soma
