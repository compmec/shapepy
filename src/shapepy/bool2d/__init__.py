"""
Defines the internal module that computes the boolean
operations between subsets
"""

from ..tools import Is
from .base import Future
from .boolean import (
    clean_bool2d,
    contains_bool2d,
    intersect_bool2d,
    invert_bool2d,
    unite_bool2d,
    xor_bool2d,
)
from .convert import from_any

Future.invert = invert_bool2d
Future.unite = unite_bool2d
Future.intersect = intersect_bool2d
Future.clean = clean_bool2d
Future.convert = from_any
Future.xor = xor_bool2d
Future.contains = contains_bool2d
