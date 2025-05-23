"""
Defines the classes:
* ContinuousCurve
* ClosedCurve
* JordanCurve

Defines the functions:
* compute_lenght
* compute_area
"""

from __future__ import annotations

from numbers import Real
from typing import Iterable, Optional

from .. import bool1d, default
from ..analytic import IAnalytic1D
from ..analytic import tools as anatools
from ..analytic.piecewise import PiecewiseAnalytic1D
from ..bool1d import SubSetR1
from ..loggers import debug
from ..quadrature import chebyshev
from .abc import IClosedCurve, IContinuousCurve, IJordanCurve
from .cage import BoxCage
from .point import GeometricPoint, any2point, cartesian, cross, inner


class ContinuousCurve(IContinuousCurve):
    """
    Defines a parametrized geometric curve from given x and y functions

        C(t) = (x(t), y(t))
    """

    def __init__(self, xfunc: IAnalytic1D, yfunc: IAnalytic1D):
        if not isinstance(xfunc, IAnalytic1D):
            raise TypeError
        if not isinstance(yfunc, IAnalytic1D):
            raise TypeError
        domain = xfunc.domain & yfunc.domain
        if not anatools.is_continuous(xfunc, domain):
            raise ValueError(f"xana {xfunc} is not continuous on {domain}")
        if not anatools.is_continuous(yfunc, domain):
            raise ValueError(f"yana {yfunc} is not continuous on {domain}")

        self.__domain = domain
        self.__xfunc = xfunc.section(domain)
        self.__yfunc = yfunc.section(domain)
        self.__lenght: Optional[Real] = None
        self.__box: Optional[BoxCage] = None

    def __getitem__(self, index) -> IAnalytic1D:
        return self.__yfunc if index else self.__xfunc

    @property
    def domain(self) -> SubSetR1:
        return self.__domain

    @property
    def cage(self) -> BoxCage:
        if self.__box is None:
            ximage = self[0].image()
            yimage = self[1].image()
            botpt = (bool1d.infimum(ximage), bool1d.infimum(yimage))
            toppt = (bool1d.supremum(ximage), bool1d.supremum(yimage))
            self.__box = BoxCage(botpt, toppt)
        return self.__box

    @property
    def lenght(self) -> Real:
        if self.__lenght is None:
            self.__lenght = compute_lenght(self)
        return self.__lenght

    def section(
        self, subdomain: Optional[SubSetR1] = None
    ) -> IContinuousCurve:
        return self.__class__(
            self[0].section(subdomain), self[1].section(subdomain)
        )

    @debug("shapepy.geometry.curve")
    def eval(self, node: Real, derivate: int = 0) -> GeometricPoint:
        xcoord = self[0].eval(node, derivate)
        ycoord = self[1].eval(node, derivate)
        return cartesian(xcoord, ycoord)

    @debug("shapepy.geometry.curve")
    def projection(self, point: GeometricPoint) -> SubSetR1:
        point = any2point(point)
        deltax: IAnalytic1D = self[0] - point.x
        deltay: IAnalytic1D = self[1] - point.y
        dist2: IAnalytic1D = deltax * deltax + deltay * deltay
        return dist2.where(bool1d.infimum(dist2.image()))

    def __str__(self):
        return f"ContinuousCurve({self[0]}, {self[1]})"

    def __repr__(self):
        return f"ContinuousCurve({repr(self[0])}, {repr(self[1])})"

    def __eq__(self, other: object):
        if not isinstance(other, ContinuousCurve):
            return NotImplemented
        return self[0] == other[0] and self[1] == other[1]


class ClosedCurve(ContinuousCurve, IClosedCurve):
    """
    Defines a geometric curve which is also closed.

    Meaning, if the curve is defined in the interval [a, b],
    then it's required that C(a) == C(b)

    """

    def __init__(self, xfunc: IAnalytic1D, yfunc: IAnalytic1D):
        super().__init__(xfunc, yfunc)
        self.__area: Optional[Real] = None

    @property
    def area(self) -> Real:
        if self.__area is None:
            self.__area = compute_area(self)
        return self.__area

    @debug("shapepy.geometry.curve", 2)
    def winding(self, point: GeometricPoint) -> Real:
        point = any2point(point)
        if point not in self.cage:
            return 0 if self.area > 0 else 1

        deltax = self[0] - point.x
        deltay = self[1] - point.y
        radius_square = deltax * deltax + deltay * deltay
        roots = radius_square.where(0)
        if roots != bool1d.EmptyR1():
            wind = 0
            roots = set(bool1d.extract_knots(roots))
            # Remove the last point, cause the first one is already included
            roots -= {bool1d.supremum(self[0].domain)}
            for root in roots:
                pointa = limit_closed(self, root, True, 1)
                pointb = limit_closed(self, root, False, 1)
                wind += uatan2(cross(pointa, pointb), -inner(pointa, pointb))
            return wind

        def windin(knota: Real, knotb: Real) -> Real:
            pointa = self.eval(knota)
            pointb = self.eval(knotb)
            wind = uatan2(cross(pointa, pointb), inner(pointa, pointb))
            if abs(wind) > 0.25:
                knotm = (knota + knotb) / 2
                wind = windin(knota, knotm) + windin(knotm, knotb)
            return wind

        knots = set(anatools.extract_knots(radius_square))
        knots |= set(bool1d.extract_knots(roots))
        knots = sorted(knots)
        wind = round(sum(windin(ta, tb) for ta, tb in zip(knots, knots[1:])))
        return wind if self.area > 0 else 1 + wind


class JordanCurve(ClosedCurve, IJordanCurve):
    """
    This class is to ensure that it doesn't intersect itself.

    For now, we only require it for being close.
    Still have to implement the check if the curve intersect itself
    """


def extract_knots(curve: ContinuousCurve) -> Iterable[Real]:
    """
    Extract the knots of the given curve.
    This is usual when the curve contains at least one Piecewise analytic
    in x or in y.
    But this function is made to extract the boundary if there's no piecewise
    """
    knots = set()
    xcurve = curve[0]
    ycurve = curve[1]
    knots.add(bool1d.infimum(xcurve.domain))
    knots.add(bool1d.supremum(xcurve.domain))
    knots.add(bool1d.infimum(ycurve.domain))
    knots.add(bool1d.supremum(ycurve.domain))
    if isinstance(xcurve, PiecewiseAnalytic1D):
        knots |= set(xcurve.knots)
    if isinstance(ycurve, PiecewiseAnalytic1D):
        knots |= set(ycurve.knots)
    return sorted(knots)


def limit_curve(
    curve: ContinuousCurve, node: Real, left: bool, derivate: int = 0
) -> GeometricPoint:
    """
    Computes the limit of given curve
    """
    xvalue = anatools.limit(curve[0], node, left, derivate)
    yvalue = anatools.limit(curve[1], node, left, derivate)
    return cartesian(xvalue, yvalue)


def limit_closed(
    curve: ClosedCurve, node: Real, left: bool, derivate: int = 0
) -> GeometricPoint:
    """
    Computes the limit for a closed curve
    """
    inf = bool1d.infimum(curve.domain)
    sup = bool1d.supremum(curve.domain)
    if left and node == inf:
        node = sup
    elif not left and node == sup:
        node = inf
    return limit_curve(curve, node, left, derivate)


def uatan2(yval: Real, xval: Real) -> Real:
    """
    Computes the unitary arctan2, returning an angle in turns

    It's equivalent to arctan2(yval, xval)/tau

    Parameters
    ----------
    yval: Real
        The y coordinate
    xval: Real
        The x coordinate

    Return
    ------
    Real
        A value in the interval (-0.5, 0.5]

    Example
    -------
    >>> uatan2(0, 0)
    0
    >>> uatan2(0, 1)
    0
    >>> uatan2(0, -1)
    0.5
    >>> uatan2(1, 0)
    0.25
    >>> uatan2(-1, 0)
    -0.25
    """
    return default.atan2(yval, xval) / default.tau


@debug("shapepy.geometry.curve")
def compute_lenght(
    curve: ContinuousCurve,
    tolerance: Real = 1e-9,
) -> Real:
    """
    Uses adaptative integration to find the curve's lenght
    """
    tolerance = default.finite(tolerance)
    dxfunc: IAnalytic1D = curve[0].derivate(1)
    dyfunc: IAnalytic1D = curve[1].derivate(1)
    ds2fun: IAnalytic1D = dxfunc * dxfunc + dyfunc * dyfunc

    def dsfunc(x):
        return default.sqrt(ds2fun(x))

    tinf = bool1d.infimum(ds2fun.domain)
    tsup = bool1d.supremum(ds2fun.domain)

    quadra = chebyshev(5)
    return quadra.adaptative(dsfunc, tinf, tsup, tolerance)


@debug("shapepy.geometry.curve")
def compute_area(
    curve: ContinuousCurve,
    tolerance: Real = 1e-9,
) -> Real:
    """
    Computes the area of a closed curve

    Parameters
    ----------
    curve: ContinuousCurve
        The curve to compute the integral
    tolerance: Real
        Numerical tolerance to compute quadrature if necessary

    Return
    ------
    Real
        The computed area
    """
    tolerance = default.finite(tolerance)
    dxfunc: IAnalytic1D = curve[0].derivate(1)
    dyfunc: IAnalytic1D = curve[1].derivate(1)
    integfunc = curve[0] * dyfunc - curve[1] * dxfunc
    return integfunc.integrate(tolerance=tolerance) / 2
