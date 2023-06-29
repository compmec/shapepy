"""
This file contains functions to create primitive shapes such as:
- Regular polygons
- Circle
- Square
"""

import numpy as np

from compmec.shape.shape import JordanCurve, Shape


def regular_polygon(nsides: int):
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
    curve = JordanCurve(points)
    return Shape([curve])
