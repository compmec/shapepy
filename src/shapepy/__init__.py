"""
This module analyse sections of beams by using the boundary element method
It uses mainly curves as boundary to compute the elements.
For the moment, it only uses polygon shapes:
    retangular is a 4-side shape while a circle is a polygon with many sides
"""

import importlib

from shapepy.bool2d.base import EmptyShape, WholeShape
from shapepy.bool2d.primitive import Primitive
from shapepy.bool2d.shape import ConnectedShape, DisjointShape, SimpleShape
from shapepy.common import move, rotate, scale
from shapepy.geometry.integral import IntegrateJordan
from shapepy.geometry.jordancurve import JordanCurve
from shapepy.geometry.point import Point2D
from shapepy.geometry.segment import Segment
from shapepy.plot.plot import ShapePloter

__version__ = importlib.metadata.version("shapepy")

if __name__ == "__main__":
    pass
