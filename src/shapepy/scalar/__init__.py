"""Defines the scalar submodule for shapepy package

It contains the functions of conversion between the standard numbers,
defines the class Angle to handle conversions between radians and degrees,
defines the methods of numerical integration (quadrature)"""

from ..tools import To
from .angle import Angle, to_angle
from .reals import Math, Rational, Real

To.angle = to_angle
