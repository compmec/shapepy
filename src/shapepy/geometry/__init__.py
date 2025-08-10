"""
Init file for submodule geometry of shapepy package
"""

from .base import Future
from .intersection import intersect

Future.intersect = intersect
