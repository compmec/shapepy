"""
File that defines the classes

* Math: to store mathematical methods used
* BaseCurve: Defines a parent of BezierCurve and Segment
* Operations
* Intersection
* Projection
* Derivate
* IntegratePlanar
"""

from __future__ import annotations

from copy import copy
from typing import Iterable, Optional, Tuple, Union

from ..analytic.base import IAnalytic
from ..analytic.tools import find_minimum
from ..loggers import debug
from ..rbool import EmptyR1, IntervalR1, from_any, infimum, supremum
from ..scalar.angle import Angle
from ..scalar.quadrature import AdaptativeIntegrator, IntegratorFactory
from ..scalar.reals import Math, Real
from ..tools import Is, To, pairs, vectorize
from .base import IParametrizedCurve
from .box import Box
from .point import Point2D, cartesian


class Segment(IParametrizedCurve):
    """
    Defines a planar curve in the plane,
    that contains a bezier curve inside it
    """

    def __init__(self, xfunc: IAnalytic, yfunc: IAnalytic):
        if not Is.instance(xfunc, IAnalytic):
            raise TypeError
        if not Is.instance(yfunc, IAnalytic):
            raise TypeError
        self.__length = None
        self.__knots = (To.rational(0, 1), To.rational(1, 1))
        self.__xfunc = xfunc.clean()
        self.__yfunc = yfunc.clean()

    def __str__(self) -> str:
        return f"BS{list(self.knots)}:({self.xfunc}, {self.yfunc})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Segment) -> bool:
        return (
            Is.instance(other, Segment)
            and self.xfunc == other.xfunc
            and self.yfunc == other.yfunc
        )

    @debug("shapepy.geometry.segment")
    def __contains__(self, point: Point2D) -> bool:
        point = To.point(point)
        if point not in self.box():
            return False
        deltax = self.xfunc - point.xcoord
        deltay = self.yfunc - point.ycoord
        dist_square = deltax * deltax + deltay * deltay
        return find_minimum(dist_square, [0, 1]) < 1e-12

    @vectorize(1, 0)
    def __call__(self, node: Real, derivate: int = 0) -> Point2D:
        xcoord = self.xfunc(node, derivate)
        ycoord = self.yfunc(node, derivate)
        return cartesian(xcoord, ycoord)

    @property
    def xfunc(self) -> IAnalytic:
        """
        Gives the analytic function x(t) from p(t) = (x(t), y(t))
        """
        return self.__xfunc

    @property
    def yfunc(self) -> IAnalytic:
        """
        Gives the analytic function y(t) from p(t) = (x(t), y(t))
        """
        return self.__yfunc

    @property
    def length(self) -> Real:
        """
        The length of the segment
        """
        if self.__length is None:
            self.__length = compute_length(self)
        return self.__length

    @property
    def knots(self) -> Tuple[Real, Real]:
        return self.__knots

    def derivate(self, times: Optional[int] = 1) -> Segment:
        """
        Gives the first derivative of the curve
        """
        if not Is.integer(times) or times <= 0:
            raise ValueError(f"Times must be integer >= 1, not {times}")
        dxfunc = copy(self.xfunc).derivate(times)
        dyfunc = copy(self.yfunc).derivate(times)
        return Segment(dxfunc, dyfunc)

    def box(self) -> Box:
        """Returns two points which defines the minimal exterior rectangle

        Returns the pair (A, B) with A[0] <= B[0] and A[1] <= B[1]
        """
        xmin = find_minimum(self.xfunc, [0, 1])
        xmax = -find_minimum(-self.xfunc, [0, 1])
        ymin = find_minimum(self.yfunc, [0, 1])
        ymax = -find_minimum(-self.yfunc, [0, 1])
        return Box(cartesian(xmin, ymin), cartesian(xmax, ymax))

    def clean(self) -> Segment:
        """Cleans the segment"""
        self.__xfunc = self.__xfunc.clean()
        self.__yfunc = self.__yfunc.clean()
        return self

    def __copy__(self) -> Segment:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> Segment:
        return Segment(copy(self.xfunc), copy(self.yfunc))

    @debug("shapepy.geometry.segment")
    def invert(self) -> Segment:
        """
        Inverts the direction of the curve.
        If the curve is clockwise, it becomes counterclockwise
        """
        half = To.rational(1, 2)
        self.__xfunc = self.__xfunc.shift(-half).scale(-1).shift(half)
        self.__yfunc = self.__yfunc.shift(-half).scale(-1).shift(half)
        return self

    @debug("shapepy.geometry.segment")
    def split(self, nodes: Iterable[Real]) -> Tuple[Segment, ...]:
        """
        Splits the curve into more segments
        """
        nodes = (n for n in nodes if self.knots[0] <= n <= self.knots[-1])
        nodes = sorted(set(nodes) | set(self.knots))
        return tuple(self.section([ka, kb]) for ka, kb in pairs(nodes))

    @debug("shapepy.geometry.segment")
    def move(self, vector: Point2D) -> Segment:
        vector = To.point(vector)
        self.__xfunc += vector.xcoord
        self.__yfunc += vector.ycoord
        return self

    @debug("shapepy.geometry.segment")
    def scale(self, amount: Union[Real, Tuple[Real, Real]]) -> Segment:
        self.__xfunc *= amount if Is.real(amount) else amount[0]
        self.__yfunc *= amount if Is.real(amount) else amount[1]
        return self

    @debug("shapepy.geometry.segment")
    def rotate(self, angle: Angle) -> Segment:
        angle = To.angle(angle)
        cos, sin = angle.cos(), angle.sin()
        xfunc, yfunc = self.xfunc, self.yfunc
        self.__xfunc = xfunc * cos - yfunc * sin
        self.__yfunc = xfunc * sin + yfunc * cos
        return self

    @debug("shapepy.geometry.segment")
    def section(self, interval: IntervalR1) -> Segment:
        interval = from_any(interval)
        if not 0 <= interval[0] < interval[1] <= 1:
            raise ValueError(f"Invalid {interval}")
        if interval is EmptyR1():
            raise TypeError(f"Cannot extract with interval {interval}")
        if interval == [0, 1]:
            return self
        knota = infimum(interval)
        knotb = supremum(interval)
        denom = 1 / (knotb - knota)
        nxfunc = copy(self.xfunc).shift(-knota).scale(denom)
        nyfunc = copy(self.yfunc).shift(-knota).scale(denom)
        return Segment(nxfunc, nyfunc)


@debug("shapepy.geometry.segment")
def compute_length(segment: Segment) -> Real:
    """
    Computes the length of the jordan curve
    """
    domain = (0, 1)
    dpsquare: IAnalytic = (
        segment.xfunc.derivate() ** 2 + segment.yfunc.derivate() ** 2
    )
    assert Is.analytic(dpsquare)
    if dpsquare == dpsquare(0):  # Check if it's constant
        return (domain[1] - domain[0]) * Math.sqrt(dpsquare(0))
    integrator = IntegratorFactory.clenshaw_curtis(3)
    adaptative = AdaptativeIntegrator(integrator, 1e-9, 12)

    def function(node):
        return Math.sqrt(dpsquare(node))

    return adaptative.integrate(function, domain)


def is_segment(obj: object) -> bool:
    """
    Checks if the parameter is a Segment

    Parameters
    ----------
    obj : The object to be tested

    Returns
    -------
    bool
        True if the obj is a Segment, False otherwise
    """
    return Is.instance(obj, Segment)


Is.segment = is_segment
