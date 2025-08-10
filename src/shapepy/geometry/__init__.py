"""
Init file for submodule geometry of shapepy package
"""

from .base import Future
from .concatenate import concatenate
from .intersection import intersect

Future.intersect = intersect
Future.concatenate = concatenate
