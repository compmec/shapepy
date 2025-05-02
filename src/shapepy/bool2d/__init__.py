"""
Init file that is used to easy import from shapepy module.

It only includes the most used classes and functions
"""

from .base import EmptyR2, Future, WholeR2
from .bool2d import contains, intersect, invert, unite
from .container import expand
from .converter import from_any
from .simplify import simplify
from .transform import move, rotate, scale

Future.convert = from_any
Future.unite = unite
Future.intersect = intersect
Future.invert = invert
Future.contains = contains
Future.move = move
Future.scale = scale
Future.rotate = rotate
Future.simplify = simplify
