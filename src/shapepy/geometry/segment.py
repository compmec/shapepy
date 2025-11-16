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
from typing import Optional, Tuple, Union

from ..analytic.base import IAnalytic
from ..analytic.bezier import Bezier
from ..analytic.tools import find_minimum, is_constant
from ..loggers import debug
from ..rbool import IntervalR1, WholeR1, from_any, infimum, supremum
from ..rbool.tools import is_continuous
from ..scalar.quadrature import AdaptativeIntegrator, IntegratorFactory
from ..scalar.reals import Math, Real
from ..tools import Is, To
from .base import IParametrizedCurve
from .box import Box
from .point import Point2D, cartesian


class Segment(IParametrizedCurve):
    """
    Defines a planar curve in the plane,
    that contains a bezier curve inside it
    """

    def __init__(
        self,
        xfunc: IAnalytic,
        yfunc: IAnalytic,
        *,
        domain: Union[None, IntervalR1, WholeR1] = None,
    ):
        if not Is.instance(xfunc, IAnalytic):
            raise TypeError
        if not Is.instance(yfunc, IAnalytic):
            raise TypeError
        if domain is None:
            domain = xfunc.domain & yfunc.domain
        elif not is_continuous(domain):
            raise TypeError(f"Domain is not continuous: {domain}")
        elif domain not in (xfunc.domain & yfunc.domain):
            raise ValueError(
                f"Given domain must be in {xfunc.domain & yfunc.domain}"
            )
        self.__length = None
        self.__domain = domain
        self.__knots = (infimum(self.domain), supremum(self.domain))
        self.__xfunc = xfunc
        self.__yfunc = yfunc

    @property
    def domain(self) -> Union[IntervalR1, WholeR1]:
        return self.__domain

    @property
    def knots(self) -> Tuple[Real, Real]:
        return self.__knots

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
        if self.__length is None:
            self.__length = compute_length(self)
        return self.__length

    def __str__(self) -> str:
        return f"BS{self.domain}:({self.xfunc}, {self.yfunc})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Segment) -> bool:
        return (
            Is.instance(other, Segment)
            and self.domain == other.domain
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
        return find_minimum(dist_square, self.domain) < 1e-12

    def eval(self, node: Real, derivate: int = 0) -> Point2D:
        xcoord = self.xfunc.eval(node, derivate)
        ycoord = self.yfunc.eval(node, derivate)
        return cartesian(xcoord, ycoord)

    def derivate(self, times: Optional[int] = 1) -> Segment:
        """
        Gives the first derivative of the curve
        """
        if not Is.integer(times) or times <= 0:
            raise ValueError(f"Times must be integer >= 1, not {times}")
        dxfunc = self.xfunc.derivate(times)
        dyfunc = self.yfunc.derivate(times)
        return Segment(dxfunc, dyfunc, domain=self.domain)

    def box(self) -> Box:
        """Returns two points which defines the minimal exterior rectangle

        Returns the pair (A, B) with A[0] <= B[0] and A[1] <= B[1]
        """
        xmin = find_minimum(self.xfunc, self.domain)
        xmax = -find_minimum(-self.xfunc, self.domain)
        ymin = find_minimum(self.yfunc, self.domain)
        ymax = -find_minimum(-self.yfunc, self.domain)
        return Box(cartesian(xmin, ymin), cartesian(xmax, ymax))

    def __copy__(self) -> Segment:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> Segment:
        return Segment(copy(self.xfunc), copy(self.yfunc), domain=self.domain)

    def __invert__(self) -> Segment:
        """
        Inverts the direction of the curve.
        If the curve is clockwise, it becomes counterclockwise
        """
        composition = Bezier(
            [self.knots[-1], self.knots[0]], [self.knots[0], self.knots[-1]]
        )
        xfunc = self.__xfunc.compose(composition)
        yfunc = self.__yfunc.compose(composition)
        return Segment(xfunc, yfunc, domain=self.domain)

    def section(self, domain: Union[IntervalR1, WholeR1]) -> Segment:
        """Extracts a subsegment from the given segment"""
        domain = from_any(domain)
        if domain not in self.domain:
            raise ValueError(f"Given {domain} not in {self.domain}")
        return Segment(self.xfunc, self.yfunc, domain=domain)


@debug("shapepy.geometry.segment")
def compute_length(segment: Segment) -> Real:
    """
    Computes the length of the jordan curve
    """
    dpsquare = segment.xfunc.derivate() ** 2 + segment.yfunc.derivate() ** 2
    assert Is.instance(dpsquare, IAnalytic)
    if is_constant(dpsquare):  # Check if it's constant
        knota, knotb = segment.knots
        return (knotb - knota) * Math.sqrt(dpsquare((knota + knotb) / 2))
    integrator = IntegratorFactory.clenshaw_curtis(3)
    adaptative = AdaptativeIntegrator(integrator, 1e-9, 12)

    def function(node):
        return Math.sqrt(dpsquare(node))

    return adaptative.integrate(function, segment.domain)


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
