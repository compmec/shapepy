"""
Defines the classes:
* GeometricPoint
* ContinuousCurve
* ClosedCurve
* JordanCurve
* BoundingBox

Defines the functions:
* compute_lenght
* compute_area
* move_point
* move_curve
* scale_point
* scale_curve
* rotate_point
* rotate_curve
* reverse
* geometric_point
"""

from __future__ import annotations

from numbers import Real
from typing import Optional, Tuple, Union

from . import default
from .analytic import IAnalytic1D
from .analytic.piecewise import PiecewiseAnalytic1D
from .angle import Angle
from .bool1d import EmptyR1, SubSetR1, extract_knots, infimum, supremum
from .loggers import debug
from .quadrature import chebyshev


class GeometricPoint:
    """
    Defines a geometric point to store the values of
    the xcoord, ycoord, radius and angle

    It's intended to be returned by the evaluation of the ContinuousCurve
    """

    @classmethod
    def cartesian(cls, x: Real, y: Real) -> GeometricPoint:
        """
        Creates an GeometricPoint instance from given cartesian coordinates

        Parameters
        ----------
        x: Real
            The x coordinate, the abscissa value
        y: Real
            The y coordinate, the ordinate value

        Return
        ------
        GeometricPoint
            The created point from given cartesian coordinates
        """
        x = default.real(x)
        y = default.real(y)
        radius = default.hypot(x, y)
        angle = Angle.arg(x, y)
        return cls(x, y, radius, angle)

    @classmethod
    def polar(cls, radius: Real, angle: Angle) -> GeometricPoint:
        """
        Creates an GeometricPoint instance from given polar coordinates

        Parameters
        ----------
        radius: Real
            Distance from the origin
        angle: Angle
            The angle between the point and the positive x-axis

        Return
        ------
        GeometricPoint
            The created point from given polar coordinates
        """
        sinval, cosval = angle.sin(), angle.cos()
        if radius < 0:
            raise ValueError(f"Cannot have radius = {radius} < 0")
        x = default.finite(0) if cosval == 0 else radius * cosval
        y = default.finite(0) if sinval == 0 else radius * sinval
        return cls(x, y, radius, angle)

    def __init__(self, x: Real, y: Real, radius: Real, angle: Real):
        self.__x = x
        self.__y = y
        self.__radius = radius
        self.__angle = angle

    @property
    def x(self) -> Real:
        """
        The first coordinate of the point

        :getter: Returns the first coordinate of the point
        :type: Real
        """
        return self.__x

    @property
    def y(self) -> Real:
        """
        The second coordinate of the point

        :getter: Returns the first coordinate of the point
        :type: Real
        """
        return self.__y

    @property
    def radius(self) -> Real:
        """
        The euclidian distance between the origin and the point

        :getter: Returns the L2 norm of the point
        :type: Real
        """
        return self.__radius

    @property
    def angle(self) -> Angle:
        """
        The angle measured from the x-axis

        :getter: Returns the angle of the point
        :type: Angle
        """
        return self.__angle

    def __str__(self) -> str:
        return (
            f"({self.x}, {self.y})"
            if default.isfinite(self.radius)
            else f"({self.radius}:{self.angle})"
        )

    def __repr__(self):
        return "GeomPt" + str(self)

    def __eq__(self, other: object):
        try:
            other = geometric_point(other)
            return self.x == other.x and self.y == other.y
        except (TypeError, IndexError):
            return NotImplemented


class ContinuousCurve:
    """
    Defines a parametrized geometric curve from given x and y functions

        C(t) = (x(t), y(t))
    """

    def __init__(self, xfunc: IAnalytic1D, yfunc: IAnalytic1D):
        if not isinstance(xfunc, IAnalytic1D):
            raise TypeError
        if not isinstance(yfunc, IAnalytic1D):
            raise TypeError
        if xfunc.domain != yfunc.domain:
            raise ValueError(
                "The domain must be equal! {xfunc.domain} != {yfunc.domain}"
            )

        self.__xfunc: IAnalytic1D = xfunc
        self.__yfunc: IAnalytic1D = yfunc
        self.__lenght: Optional[Real] = None
        self.__box: Optional[BoundingBox] = None

    def __getitem__(self, index) -> IAnalytic1D:
        return self.__yfunc if index else self.__xfunc

    @property
    def box(self) -> BoundingBox:
        """
        Gives the minimum box that contains entirely the curve

        :getter: Returns the box that contains the curve
        :type: BoundingBox
        """
        if self.__box is None:
            ximage = self[0].image()
            yimage = self[1].image()
            botpt = (infimum(ximage), infimum(yimage))
            toppt = (supremum(ximage), supremum(yimage))
            self.__box = BoundingBox(botpt, toppt)
        return self.__box

    @property
    def lenght(self) -> Real:
        """
        Gives the curve's length

        :getter: Returns the length of the curve
        :type: Real
        """
        if self.__lenght is None:
            self.__lenght = compute_lenght(self)
        return self.__lenght

    @debug("shapepy.geometry.curve")
    def eval(self, node: Real, derivate: int = 0) -> GeometricPoint:
        """
        Evaluate the curve at given node 't':

            C(t) = (x(t), y(t))

        Parameters
        ----------
        node: Real
            The t-value used to evaluate the curve
        derivate: int, default = 0
            Used when the derivate is required

        Return
        ------
        GeometricPoint
            The evaluated point C(t) = (x(t), y(t))
        """
        xcoord = self[0].eval(node, derivate)
        ycoord = self[1].eval(node, derivate)
        return GeometricPoint.cartesian(xcoord, ycoord)

    @debug("shapepy.geometry.curve")
    def projection(self, point: GeometricPoint) -> SubSetR1:
        """
        Computes the projection of a point in the given curve.

        Finds all the values 't' such minimizes the distance between the
        curve and the point

            min_t <C(t)-P, C(t)-P>

        It's possible to not have a projection point.
        In that case, gives an EmptyR1 instance.

        Parameters
        ----------
        point: GeometricPoint
            The point to be projected

        Return
        ------
        SubSetR1
            The values 't' that minimizes the distance
        """
        point = geometric_point(point)
        deltax: IAnalytic1D = self[0] - point.x
        deltay: IAnalytic1D = self[1] - point.y
        dist2: IAnalytic1D = deltax * deltax + deltay * deltay
        return dist2.where(infimum(dist2.image()))

    def __str__(self):
        return f"ContinuousCurve({self[0]}, {self[1]})"

    def __repr__(self):
        return f"ContinuousCurve({repr(self[0])}, {repr(self[1])})"

    def __eq__(self, other: object):
        if not isinstance(other, ContinuousCurve):
            return NotImplemented
        return self[0] == other[0] and self[1] == other[1]


class ClosedCurve(ContinuousCurve):
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
        """
        Gives the area enclosed by the curve

        :getter: Returns the area enclosed by the curve
        :type: Real
        """
        if self.__area is None:
            self.__area = compute_area(self)
        return self.__area

    @debug("shapepy.geometry.curve", 2)
    def winding(self, point: GeometricPoint) -> Real:
        """
        Computes the winding number with respect to a point.
        It gives a real value that depends

        For this function, we consider that
        """
        point = geometric_point(point)
        if point not in self.box:
            return 0 if self.area > 0 else 1

        deltax = self[0] - point.x
        deltay = self[1] - point.y
        radius_square = deltax * deltax + deltay * deltay
        roots = radius_square.where(0)
        if roots != EmptyR1():
            wind = 0
            roots = set(extract_knots(roots))
            # Remove the last point, cause the first one is already included
            roots -= {supremum(self[0].domain)}
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

        knots = set(extract_knots(roots))
        knots.add(infimum(radius_square.domain))
        knots.add(supremum(radius_square.domain))
        if isinstance(radius_square, PiecewiseAnalytic1D):
            knots |= set(radius_square.knots)
        knots = sorted(knots)
        wind = round(sum(windin(ta, tb) for ta, tb in zip(knots, knots[1:])))
        return wind if self.area > 0 else 1 + wind


class JordanCurve(ClosedCurve):
    """
    This class is to ensure that it doesn't intersect itself.

    For now, we only require it for being close.
    Still have to implement the check if the curve intersect itself
    """


class BoundingBox:
    """
    Defines a bounding rectangular box to speed up the evaluation
    if a point is inside a region defined by a curve
    """

    def __init__(self, bot_point: GeometricPoint, top_point: GeometricPoint):
        self.__bot = geometric_point(bot_point)
        self.__top = geometric_point(top_point)

    def winding(self, point: GeometricPoint) -> Real:
        """
        Computes the winding number for the rectangle.
        Gives one of the four values:
        * 0.00: Point is outside
        * 0.25: Point is at the vertex
        * 0.50: Point is on the edge
        * 1.00: Point is interior

        Parameters
        ----------
        point: GeometricPoint
            The point to check its position

        Return
        ------
        Real
            The winding number, a real number in: {0, 0.25, 0.5, 1}

        Example
        -------
        >>> box = BoundingBox((0, 0), (2, 2))
        >>> box.winding((-1, -1))  # Outside
        0
        >>> box.winding((0, 0))  # At vertex
        0.25
        >>> box.winding((0, 1))  # On the edge
        0.5
        >>> box.winding((1, 1))  # Interior
        1
        """

        def step(value: Real) -> Real:
            """
            Computes the step function:

            Parameters
            ----------
            value: Real
                The position to evaluate

            Return
            ------
            Real
                A real number in {0, 0.5, 1}

            Example
            -------
            >>> step(-2)
            0
            >>> step(-1)
            0
            >>> step(0)
            0.5
            >>> step(1)
            1
            >>> step(2)
            1
            """
            return 0 if value < 0 else 1 if value > 0 else 0.5

        point = geometric_point(point)
        xwind = step(point.x - self.__bot.x) * step(self.__top.x - point.x)
        ywind = step(point.y - self.__bot.y) * step(self.__top.y - point.y)
        return xwind * ywind

    def __contains__(self, point: GeometricPoint) -> bool:
        return 0 < self.winding(point)


quadrature = chebyshev(5)


def limit_curve(
    curve: ContinuousCurve, node: Real, left: bool, derivate: int = 0
) -> GeometricPoint:
    """
    Computes the limit of given curve
    """
    xvalue = limit_analytic(curve[0], node, left, derivate)
    yvalue = limit_analytic(curve[1], node, left, derivate)
    return GeometricPoint.cartesian(xvalue, yvalue)


def limit_analytic(
    analytic: IAnalytic1D, node: Real, left: bool, derivate: int = 0
) -> Real:
    """
    Computes the limit for an analytic function
    """
    if not isinstance(analytic, PiecewiseAnalytic1D):
        return analytic.eval(node, derivate)
    try:
        index = analytic.knots.index(node)
    except ValueError:
        return analytic.eval(node, derivate)

    if left:
        analytic = analytic.analytics[index - 1]
    else:
        analytic = analytic.analytics[index]

    return analytic.eval(node, derivate)


def limit_closed(
    curve: ClosedCurve, node: Real, left: bool, derivate: int = 0
) -> GeometricPoint:
    """
    Computes the limit for a closed curve
    """
    inf = infimum(curve[0].domain)
    sup = supremum(curve[0].domain)
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


def inner(pointa: GeometricPoint, pointb: GeometricPoint) -> Real:
    """
    Computes the inner product between two points

    Parameters
    ----------
    pointa: GeometricPoint
        The point A to compute <A, B>
    pointb: GeometricPoint
        The point B to compute <A, B>

    Return
    ------
    Real
        The value of the inner product

    Example
    -------
    >>> pointa = (3, 4)
    >>> pointb = (5, 2)
    >>> inner(pointa, pointb)
    23
    """
    pointa = geometric_point(pointa)
    pointb = geometric_point(pointb)
    return pointa.x * pointb.x + pointa.y * pointb.y


def cross(pointa: GeometricPoint, pointb: GeometricPoint) -> Real:
    """
    Computes the cross product between two points

    Parameters
    ----------
    pointa: GeometricPoint
        The point A to compute A x B
    pointb: GeometricPoint
        The point B to compute A x B

    Return
    ------
    Real
        The value of the cross product

    Example
    -------
    >>> pointa = (3, 4)
    >>> pointb = (5, 2)
    >>> cross(pointa, pointb)
    -14
    """
    pointa = geometric_point(pointa)
    pointb = geometric_point(pointb)
    return pointa.x * pointb.y - pointa.y * pointb.x


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

    tinf = infimum(ds2fun.domain)
    tsup = supremum(ds2fun.domain)

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
    point = geometric_point(point)
    if not isinstance(angle, Angle):
        raise TypeError
    cos, sin = angle.cos(), angle.sin()
    xval = cos * point.x - sin * point.y
    yval = sin * point.x + cos * point.y
    return GeometricPoint.cartesian(xval, yval)


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
    if not isinstance(angle, Angle):
        raise TypeError

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
    angle: Angle
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


def geometric_point(
    point: Union[GeometricPoint, Tuple[Real, Real]]
) -> GeometricPoint:
    """
    Transforms a point to a GeometricPoint if it's not already

    Parameters
    ----------
    point: ContinuousCurve
        -
    angle: Angle
        -

    Return
    ------
    GeometricPoint
        The point

    Example
    -------
    >>> point = geometric_point((0, 0))
    >>> point
    (0, 0)
    >>> type(point)
    <class "shapepy.geometry.GeometricPoint">
    """
    return (
        point
        if isinstance(point, GeometricPoint)
        else GeometricPoint.cartesian(point[0], point[1])
    )


def from_str(text: str) -> GeometricPoint:
    """
    Converts a string into a Geometric Point
    """
    if not isinstance(text, str):
        raise TypeError
    text = text.strip()
    if text[0] != "(" or text[-1] != ")":
        raise ValueError(f"Invalid string: {text}")
    if "," in text:
        items = tuple(sub.strip() for sub in text[1:-1].split(","))
        if len(items) != 2:
            raise ValueError(f"Invalid convert to point: '{text}' -> {items}")
        return GeometricPoint.cartesian(items[0], items[1])
    raise NotImplementedError
