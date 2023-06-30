"""
This file contains functions to create primitive shapes such as:
- Regular polygons
- Circle
- Square
"""

from typing import Tuple

import numpy as np

from compmec.shape.jordancurve import JordanCurve
from compmec.shape.shape import Shape


def regular_polygon(nsides: int) -> Shape:
    """
    Creates a regular polygon of n-sides inscribed in a circle of radius 1.
        if nsides = 3, it's a triangle
        if nsides = 4, it's a square, of side square(2)
    """
    if not isinstance(nsides, int):
        raise TypeError("nsides must be an integer")
    if nsides < 3:
        raise ValueError("nsides must be >= 3")
    points = np.empty((nsides + 1, 2), dtype="float64")
    theta = np.linspace(0, 2 * np.pi, nsides + 1)
    points[:, 0] = np.cos(theta)
    points[:, 1] = np.sin(theta)
    curve = JordanCurve.init_from_points(points)
    return Shape([curve])


def triangle(side: float = 1, center: Tuple[float] = (0, 0)) -> Shape:
    """
    Creates an equilatery triangle of side `side` and center `center`.
    """
    polygon = regular_polygon(3)
    polygon.rotate_radians(np.pi / 2)
    polygon.scale(side / np.sqrt(3), side / np.sqrt(3))
    polygon.move(center[0], center[1])
    return polygon


def square(side: float = 1, center: Tuple[float] = (0, 0)) -> Shape:
    """
    Creates a square of side `side` and center `center`.
    Its edges are aligned with the axes
    """
    polygon = regular_polygon(4)
    polygon.rotate_radians(np.pi / 4)
    polygon.scale(side / np.sqrt(2), side / np.sqrt(2))
    polygon.move(center[0], center[1])
    return polygon


def circle(radius: float = 1, center: Tuple[float] = (0, 0)) -> Shape:
    """
    Creates a circle with given radius and center.
    In fact it's a regular polygon of 100 sides, since
    smooth curves are yet not possible
    """
    polygon = regular_polygon(100)
    polygon.scale(radius, radius)
    polygon.move(center[0], center[1])
    return polygon
