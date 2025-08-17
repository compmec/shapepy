"""
Defines the internal module that computes the boolean
operations between subsets
"""

from .base import Future
from .boolean import intersect_bool2d, invert_bool2d, unite_bool2d

Future.unite = unite_bool2d
Future.intersect = intersect_bool2d
Future.invert = invert_bool2d
