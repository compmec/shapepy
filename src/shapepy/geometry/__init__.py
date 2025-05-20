"""
Init file that is used to easy import from shapepy module.

It only includes the most used classes and functions
"""

from .cage import BoxCage
from .curve import ClosedCurve, ContinuousCurve, JordanCurve
from .point import GeometricPoint, geometric_point
from .transform import (
    move_curve,
    move_point,
    reverse,
    rotate_curve,
    rotate_point,
    scale_curve,
    scale_point,
)
