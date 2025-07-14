"""
Contains functions to integrate over a segment
"""

from __future__ import annotations

from typing import Union

import numpy as np
import pynurbs

from ..scalar.quadrature import (
    closed_linspace,
    inner,
    open_linspace,
    open_newton_cotes,
)
from ..scalar.reals import Math
from ..tools import Is
from .point import Point2D
from .segment import Segment


def vertical(
    curve: Segment,
    expx: int = 0,
    expy: int = 0,
    nnodes: Union[None, int] = None,
):
    """Computes the integral I

    I = int_C x^expx * y^expy * dy

    """
    if not Is.instance(curve, Segment):
        raise TypeError
    if not Is.integer(expx) or expx < 0:
        raise ValueError
    if not Is.integer(expy) or expy < 0:
        raise ValueError
    if nnodes is None:
        nnodes = 3 + expx + expy + curve.degree
    elif not Is.integer(nnodes) or nnodes < 0:
        raise ValueError
    dcurve = curve.derivate()
    nodes = open_linspace(nnodes)
    poids = pynurbs.heavy.IntegratorArray.open_newton_cotes(nnodes)
    points = curve(nodes)
    xvals = tuple(point[0] ** expx for point in points)
    yvals = tuple(point[1] ** expy for point in points)
    dyvals = tuple(point[1] for point in dcurve(nodes))
    funcvals = tuple(map(np.prod, zip(xvals, yvals, dyvals)))
    return np.inner(poids, funcvals)


def polynomial(
    curve: Segment, expx: int, expy: int, nnodes: Union[None, int] = None
):
    """
    Computes the integral

    I = int_C x^expx * y^expy * ds
    """
    if not Is.instance(curve, Segment):
        raise TypeError
    if nnodes is None:
        nnodes = 3 + expx + expy + curve.degree
    elif not Is.integer(nnodes) or nnodes < 0:
        raise ValueError
    assert expx == 0
    assert expy == 0
    dcurve = curve.derivate()
    nodes = open_linspace(nnodes)
    weights = open_newton_cotes(nnodes)
    funcvals = tuple(abs(point) for point in dcurve(nodes))
    return float(inner(weights, funcvals))


def lenght(curve: Segment, nnodes: int = 5):
    """Computes the integral I

        I = int_{C} ds

    Given the control points P of a bezier curve C(u) of
    degree p

        C(u) = sum_{i=0}^{p} B_{i,p}(u) * P_i

        I = int_{0}^{1} abs(C'(u)) * du

    """
    return polynomial(curve, 0, 0, nnodes)


def area(curve: Segment, nnodes: Union[None, int] = None):
    """Computes the integral I

    I = int_0^1 x * dy

    """
    return vertical(curve, 1, 0, nnodes)


def winding_number_linear(
    pointa: Point2D, pointb: Point2D, center: Point2D
) -> float:
    """
    Computes the winding number defined by the given points.
    It means, it's the angle made between the vector
    (pointb - center) and (pointa - center)
    """
    anglea = np.arctan2(
        float(pointa[1] - center[1]), float(pointa[0] - center[0])
    )
    angleb = np.arctan2(
        float(pointb[1] - center[1]), float(pointb[0] - center[0])
    )
    wind = (angleb - anglea) / Math.tau
    if abs(wind) < 0.5:
        return wind
    return wind - 1 if wind > 0 else wind + 1


def winding_number(
    curve: Segment,
    center: Point2D = (0.0, 0.0),
    nnodes: Union[None, int] = None,
) -> float:
    """
    Computes the integral for a bezier curve of given control points
    """
    assert Is.instance(curve, Segment)
    nnodes = curve.npts if nnodes is None else nnodes
    nodes = closed_linspace(nnodes)
    total = 0
    for nodea, nodeb in zip(nodes[:-1], nodes[1:]):
        pointa = curve(nodea)
        pointb = curve(nodeb)
        total += winding_number_linear(pointa, pointb, center)
    return total
