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
from ..rbool import IntervalR1, SubSetR1, extract_knots, from_any
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

    def __init__(
        self,
        xfunc: IAnalytic,
        yfunc: IAnalytic,
        domain: Union[None, SubSetR1] = None,
    ):
        if not Is.instance(xfunc, IAnalytic):
            raise TypeError
        if not Is.instance(yfunc, IAnalytic):
            raise TypeError
        self.__domain = (
            (xfunc.domain & yfunc.domain)
            if domain is None
            else from_any(domain)
        )
        self.__length = None
        self.__knots = None
        self.__xfunc = xfunc.clean()
        self.__yfunc = yfunc.clean()

    def __str__(self) -> str:
        return f"Seg{self.domain}:({self.xfunc}, {self.yfunc})"

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
        return find_minimum(dist_square, self.domain) < 1e-12

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
    def domain(self) -> SubSetR1:
        return self.__domain

    @property
    def knots(self) -> Tuple[Real, Real]:
        if self.__knots is None:
            self.__knots = tuple(extract_knots(self.domain))
        return self.__knots

    def derivate(self, times: Optional[int] = 1) -> Segment:
        """
        Gives the first derivative of the curve
        """
        if not Is.integer(times) or times <= 0:
            raise ValueError(f"Times must be integer >= 1, not {times}")
        dxfunc = copy(self.xfunc).derivate(times)
        dyfunc = copy(self.yfunc).derivate(times)
        return Segment(dxfunc, dyfunc, self.domain)

    def box(self) -> Box:
        """Returns two points which defines the minimal exterior rectangle

        Returns the pair (A, B) with A[0] <= B[0] and A[1] <= B[1]
        """
        xmin = find_minimum(self.xfunc, self.domain)
        xmax = -find_minimum(-self.xfunc, self.domain)
        ymin = find_minimum(self.yfunc, self.domain)
        ymax = -find_minimum(-self.yfunc, self.domain)
        return Box(cartesian(xmin, ymin), cartesian(xmax, ymax))

    def clean(self) -> Segment:
        """Cleans the segment"""
        self.__xfunc = self.__xfunc.clean()
        self.__yfunc = self.__yfunc.clean()
        return self

    def __copy__(self) -> Segment:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> Segment:
        return Segment(copy(self.xfunc), copy(self.yfunc), self.domain)

    def __invert__(self) -> Segment:
        """
        Inverts the direction of the curve.
        If the curve is clockwise, it becomes counterclockwise
        """
        half = (self.knots[0] + self.knots[1]) / 2
        xfunc = self.__xfunc.shift(-half).scale(-1).shift(half)
        yfunc = self.__yfunc.shift(-half).scale(-1).shift(half)
        return Segment(xfunc, yfunc, self.domain)

    def split(self, nodes: Iterable[Real]) -> Tuple[Segment, ...]:
        """
        Splits the curve into more segments
        """
        nodes = (n for n in nodes if self.knots[0] <= n <= self.knots[-1])
        nodes = sorted(set(nodes) | set(self.knots))
        return tuple(self.extract([ka, kb]) for ka, kb in pairs(nodes))

    def extract(self, interval: IntervalR1) -> Segment:
        """Extracts a subsegment from the given segment"""
        interval = self.domain & interval
        if not Is.instance(interval, IntervalR1):
            raise TypeError
        return Segment(self.xfunc, self.yfunc, self.domain)


@debug("shapepy.geometry.segment")
def compute_length(segment: Segment) -> Real:
    """
    Computes the length of the jordan curve
    """
    dpsquare: IAnalytic = (
        segment.xfunc.derivate() ** 2 + segment.yfunc.derivate() ** 2
    )
    assert Is.analytic(dpsquare)
    if dpsquare == dpsquare(0):  # Check if it's constant
        delta = segment.domain[1] - segment.domain[0]
        return delta * Math.sqrt(dpsquare(0))
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


Is.segment = is_segment
