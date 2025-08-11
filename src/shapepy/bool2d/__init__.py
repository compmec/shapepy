"""
Defines the internal module that computes the boolean
operations between subsets
"""

from .boolean import intersect, unite
from .shape import Future

Future.unite = unite
Future.intersect = intersect
