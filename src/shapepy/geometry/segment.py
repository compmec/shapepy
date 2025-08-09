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

import pynurbs

from shapepy.geometry.box import Box
from shapepy.geometry.point import Point2D

from ..analytic.base import IAnalytic
from ..analytic.bezier import split
from ..scalar.nodes_sample import NodeSampleFactory
from ..scalar.quadrature import AdaptativeIntegrator, IntegratorFactory
from ..scalar.reals import Math, Real
from ..tools import Is, To, vectorize
from .base import IGeometricCurve


class Segment(IGeometricCurve):
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

    def __or__(self, other: Segment) -> Segment:
        """Computes the union of two bezier curves"""
        assert Is.segment(other)
        assert self.degree == other.degree
        assert self.ctrlpoints[-1] == other.ctrlpoints[0]
        # Last point of first derivative
        dapt = self.ctrlpoints[-1] - self.ctrlpoints[-2]
        # First point of first derivative
        dbpt = other.ctrlpoints[1] - other.ctrlpoints[0]
        if abs(dapt ^ dbpt) > 1e-6:
            node = To.rational(1, 2)
        else:
            dsumpt = dapt + dbpt
            denomin = dsumpt @ dsumpt
            node = dapt @ dsumpt / denomin
        knotvectora = pynurbs.GeneratorKnotVector.bezier(
            self.degree, To.rational
        )
        knotvectora.scale(node)
        knotvectorb = pynurbs.GeneratorKnotVector.bezier(
            other.degree, To.rational
        )
        knotvectorb.scale(1 - node).shift(node)
        newknotvector = tuple(knotvectora) + tuple(
            knotvectorb[self.degree + 1 :]
        )
        finalcurve = pynurbs.Curve(newknotvector)
        finalcurve.ctrlpoints = tuple(self.ctrlpoints) + tuple(
            other.ctrlpoints
        )
        finalcurve.knot_clean((node,))
        if finalcurve.degree + 1 != finalcurve.npts:
            raise ValueError("Union is not a bezier curve!")
        return self.__class__(finalcurve.ctrlpoints)

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
        params = Projection.point_on_curve(point, self)
        vectors = tuple(cval - point for cval in self(params))
        distances = tuple(abs(vector) for vector in vectors)
        for dist in distances:
            if dist < 1e-6:  # Tolerance
                return True
        return False

    @vectorize(1, 0)
    def __call__(self, node: Real) -> Point2D:
        planar = To.bezier(self.ctrlpoints)
        return planar(node)

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
        return Box(Point2D(xmin, ymin), Point2D(xmax, ymax))

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


class Projection:
    """
    Defines the methods used to find the projection of a point into a curve
    """

    @staticmethod
    def point_on_curve(point: Point2D, curve: Segment) -> float:
        """Finds parameter u* such abs(C(u*)) is minimal

        Find the parameter by reducing the distance J(u)

        J(u) = abs(curve(u) - point)^2
        dJ/du = 0 ->  <C'(u), C(u) - P> = 0

        We find it by Newton's iteration


        """
        point = To.point(point)
        assert Is.segment(curve)
        nsample = 2 + curve.degree
        usample = NodeSampleFactory.closed_linspace(nsample)
        usample = Projection.newton_iteration(point, curve, usample)
        curvals = tuple(cval - point for cval in curve(usample))
        distans2 = tuple(curval @ curval for curval in curvals)
        mindist2 = min(distans2)
        params = []
        for i, dist2 in enumerate(distans2):
            if abs(dist2 - mindist2) < 1e-6:  # Tolerance
                params.append(usample[i])
        return tuple(params)

    # pylint: disable=too-many-locals
    @staticmethod
    def newton_iteration(
        point: Point2D, curve: Segment, usample: Tuple[float]
    ) -> Tuple[float]:
        """
        Uses newton iterations to find the parameters ``usample``
        such <C'(u), C(u) - P> = 0 stabilizes
        """
        point = To.point(point)
        dcurve = curve.derivate()
        ddcurve = dcurve.derivate()
        usample = list(usample)
        zero, one = To.rational(0), To.rational(1)
        for _ in range(10):  # Number of iterations
            curvals = tuple(cval - point for cval in curve(usample))
            dcurvals = dcurve(usample)
            ddcurvals = ddcurve(usample)
            for k, uk in enumerate(usample):
                curval = curvals[k]
                deriva = dcurvals[k]
                fuk = deriva @ curval
                dfuk = ddcurvals[k] @ curval
                dfuk += deriva @ deriva
                dfuk = dfuk if abs(dfuk) > 1e-6 else 1e-6
                newu = uk - fuk / dfuk
                usample[k] = min(one, max(newu, zero))
            usample = list(set(usample))
            if len(usample) == 1:
                break
        return usample


def compute_length(segment: Segment) -> Real:
    """
    Computes the length of the jordan curve
    """
    domain = (0, 1)
    xfunc, yfunc = extract_xyfunctions(segment)
    dpsquare: IAnalytic = xfunc.derivate() ** 2 + yfunc.derivate() ** 2
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


def extract_xyfunctions(segment: Segment) -> Tuple[IAnalytic, IAnalytic]:
    """
    Extracts the analytic functions of x(t) and y(t) that defines the segment

    Example
    -------
    >>> segment = Segment([(-3, 2), (7, -1)])
    >>> xfunc, yfunc = extract_xyfunctions(segment)
    >>> xfunc
    -3 + 10 * t
    >>> yfunc
    2 - 3 * t
    """
    xfunc: IAnalytic = To.bezier(pt[0] for pt in segment.ctrlpoints)
    yfunc: IAnalytic = To.bezier(pt[1] for pt in segment.ctrlpoints)
    return xfunc, yfunc


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
