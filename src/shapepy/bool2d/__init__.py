"""
Defines the internal module that computes the boolean
operations between subsets
"""

from .base import Future
from .boolean import intersect, unite

Future.unite = unite
Future.intersect = intersect
