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
from typing import Iterable, Optional, Tuple

from ..analytic.base import IAnalytic
from ..analytic.bezier import split
from ..analytic.tools import find_minimum
from ..scalar.quadrature import AdaptativeIntegrator, IntegratorFactory
from ..scalar.reals import Math, Real
from ..tools import Is, To, vectorize
from .base import IGeometricCurve, IParametrizedCurve
from .box import Box
from .point import Point2D, cartesian


class Segment(IGeometricCurve, IParametrizedCurve):
    """
    Defines a planar curve in the plane,
    that contains a bezier curve inside it
    """

    def __init__(self, ctrlpoints: Iterable[Point2D]):
        if not Is.iterable(ctrlpoints):
            raise ValueError("Control points must be iterable")
        self.__length = None
        self.ctrlpoints = list(map(To.point, ctrlpoints))
        self.__knots = (To.rational(0, 1), To.rational(1, 1))

    def __str__(self) -> str:
        return f"Bezier Segment {tuple(self.ctrlpoints)}"

    def __repr__(self) -> str:
        msg = f"Segment (deg {self.degree})"
        return msg

    def __eq__(self, other: Segment) -> bool:
        if not Is.segment(other):
            raise ValueError
        if self.npts != other.npts:
            return False
        for pta, ptb in zip(self.ctrlpoints, other.ctrlpoints):
            if pta != ptb:
                return False
        return True

    def __contains__(self, point: Point2D) -> bool:
        point = To.point(point)
        if point not in self.box():
            return False
        dist_square = (self.xfunc - point[0]) ** 2 + (
            self.yfunc - point[1]
        ) ** 2
        return find_minimum(dist_square, [0, 1]) < 1e-12

    @vectorize(1, 0)
    def __call__(self, node: Real, derivate: int = 0) -> Point2D:
        planar = To.bezier(self.ctrlpoints)
        return planar(node, derivate)

    @property
    def xfunc(self) -> IAnalytic:
        """
        Gives the analytic function x(t) from p(t) = (x(t), y(t))
        """
        return To.bezier(pt[0] for pt in self.ctrlpoints)

    @property
    def yfunc(self) -> IAnalytic:
        """
        Gives the analytic function y(t) from p(t) = (x(t), y(t))
        """
        return To.bezier(pt[1] for pt in self.ctrlpoints)

    @property
    def degree(self) -> int:
        """
        The degree of the bezier curve

        Degree = 1 -> Linear curve
        Degree = 2 -> Quadratic
        """
        return self.npts - 1

    @property
    def npts(self) -> int:
        """
        The number of control points used by the curve
        """
        return len(self.ctrlpoints)

    @property
    def length(self) -> Real:
        """
        The length of the segment
        """
        if self.__length is None:
            self.__length = compute_length(self)
        return self.__length

    @property
    def knots(self) -> Tuple[Real, ...]:
        return self.__knots

    @property
    def ctrlpoints(self) -> Tuple[Point2D, ...]:
        """
        The control points that defines the planar curve
        """
        return self.__ctrlpoints

    @ctrlpoints.setter
    def ctrlpoints(self, points: Iterable[Point2D]):
        self.__length = None
        self.__ctrlpoints = list(map(To.point, points))
        self.__planar = To.bezier(self.ctrlpoints)

    def derivate(self, times: Optional[int] = 1) -> Segment:
        """
        Gives the first derivative of the curve
        """
        if not Is.integer(times) or times <= 0:
            raise ValueError(f"Times must be integer >= 1, not {times}")
        planar: IAnalytic = To.bezier(self.ctrlpoints)
        newplanar: IAnalytic = planar.derivate(times)
        return self.__class__(newplanar)

    def box(self) -> Box:
        """Returns two points which defines the minimal exterior rectangle

        Returns the pair (A, B) with A[0] <= B[0] and A[1] <= B[1]
        """
        xmin = min(point[0] for point in self.ctrlpoints)
        xmax = max(point[0] for point in self.ctrlpoints)
        ymin = min(point[1] for point in self.ctrlpoints)
        ymax = max(point[1] for point in self.ctrlpoints)
        return Box(cartesian(xmin, ymin), cartesian(xmax, ymax))

    def __copy__(self) -> Segment:
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo) -> Segment:
        ctrlpoints = tuple(copy(point) for point in self.ctrlpoints)
        return self.__class__(ctrlpoints)

    def invert(self) -> Segment:
        """
        Inverts the direction of the curve.
        If the curve is clockwise, it becomes counterclockwise
        """
        points = tuple(self.ctrlpoints)
        self.ctrlpoints = (points[i] for i in range(self.degree, -1, -1))
        return self

    def split(self, nodes: Iterable[Real]) -> Tuple[Segment, ...]:
        """
        Splits the curve into more segments
        """
        nodes = sorted(nodes)
        beziers = split(self.__planar, nodes)
        return tuple(map(Segment, beziers))


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


def segment_self_intersect(segment: Segment) -> bool:
    """Tells if the segment intersects itself"""
    return len(segment.ctrlpoints) > 3


def clean_segment(segment: Segment) -> Segment:
    """Reduces at maximum the degree of the bezier curve"""
    newplanar = To.bezier(segment.ctrlpoints)
    if newplanar.degree == segment.degree:
        return segment
    return Segment(tuple(newplanar))


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
