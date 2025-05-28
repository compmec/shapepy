"""
File that contains functios to create classical shapes such as
`triangle`, `square`, `regular_polygon` and a generic `polygon`

"""

from numbers import Real
from typing import Iterable

from shapepy.bool2d.singles import ShapeR2

from .. import default
from ..angle import Angle
from ..geometry import primitive as geomprim
from ..geometry.point import GeometricPoint, any2point, polar


def polygon(vertices: Iterable[GeometricPoint]) -> ShapeR2:
    """
    Creates a generic polygon

    Parameters
    ----------
    vertices: tuple[GeometricPoint]
        Vertices of the polygon

    Return
    ------
    ShapeR2
        The ShapeR2 instance that represents the polygon

    Example
    -------
    >>> from shapepy import Primitive
    >>> vertices = [(1, 0), (0, 1), (-1, 1), (0, -1)]
    >>> shape = polygon(vertices)

    .. image:: ../img/primitive/diamond.svg

    """
    jordan_curve = geomprim.polygon(vertices)
    return ShapeR2(jordan_curve)


def triangle(side: float = 1, center: GeometricPoint = (0, 0)) -> ShapeR2:
    """
    Create a right triangle

    Parameters
    ----------
    side : Real, default: 1
        Width and height of the triangle
    center : GeometricPoint, default: (0, 0)
        Position of the vertex of right angle

    Return
    ------
    ShapeR2
        The ShapeR2 instance that represents the triangle

    Example use
    -----------
    >>> from shapepy import Primitive
    >>> triangle = triangle()

    .. image:: ../img/primitive/triangle.svg

    """
    side = default.finite(side)
    center = any2point(center)
    vertices = [(0, 0), (side, 0), (0, side)]
    return polygon(vertices).move(center)


def square(side: Real = 1, center: GeometricPoint = (0, 0)) -> ShapeR2:
    """
    Creates a square with sides aligned with axis

    Parameters
    ----------
    side : Real, default: 1
        Side of the square.
    center : GeometricPoint, default: (0, 0)
        The geometric center of the square

    Return
    ------
    ShapeR2
        The simple shape that represents the square

    Example use
    -----------
    >>> from shapepy import Primitive
    >>> square = square()

    .. image:: ../img/primitive/square.svg

    """
    half_side = default.finite(side) / 2
    if half_side <= 0:
        raise ValueError(f"The side must be positive! {side} invalid")
    center = any2point(center)
    vertices = [
        (half_side, half_side),
        (-half_side, half_side),
        (-half_side, -half_side),
        (half_side, -half_side),
    ]
    return polygon(vertices).move(center)


def regular_polygon(
    nsides: int, radius: Real = 1, center: GeometricPoint = (0, 0)
) -> ShapeR2:
    """
    Creates a regular polygon of `nsides` sides

    Parameters
    ----------
    nsides : int
        Number of sides of regular polygon, >= 3
    radius : Real, default: 1
        Radius of the external circle that contains the polygon.
    center : GeometricPoint, default: (0, 0)
        The geometric center of the regular polygon

    Return
    ------
    ShapeR2
        The simple shape that represents the regular polygon

    Example use
    -----------
    >>> from shapepy import primitive
    >>> triangle = primitive.regular_polygon(nsides = 3)

    .. image:: ../img/primitive/regular3.svg

    .. image:: ../img/primitive/regular4.svg

    .. image:: ../img/primitive/regular5.svg

    """
    nsides = default.integer(nsides)
    radius = default.finite(radius)
    center = any2point(center)
    if nsides < 3:
        raise ValueError(f"The nsides={nsides} must be at least 3!")
    if radius <= 0:
        raise ValueError(f"The radius must be positive! {radius} invalid")

    vertices = []
    for i in range(nsides):
        angle = Angle.turns(default.rational(i, nsides))
        vertex = polar(radius, angle)
        vertices.append(vertex)
    return polygon(vertices).move(center)
