"""
This module analyse sections of beams by using the boundary element method
It uses mainly curves as boundary to compute the elements.
For the moment, it only uses polygon shapes:
    retangular is a 4-side shape while a circle is a polygon with many sides
"""

from .core import Empty, IBoolean2D, IObject2D, Whole
from .curve import JordanPolygon, JordanSpline
from .operations import BooleanOperate
from .plot import ShapePloter
from .point import Point2D
from .primitive import Primitive
from .shape import ConnectedShape, DisjointShape, SimpleShape

__version__ = "1.1.0"

IBoolean2D.booloperate = BooleanOperate

if __name__ == "__main__":
    pass
