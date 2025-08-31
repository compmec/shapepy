"""
This module analyse sections of beams by using the boundary element method
It uses mainly curves as boundary to compute the elements.
For the moment, it only uses polygon shapes:
    retangular is a 4-side shape while a circle is a polygon with many sides
"""

import importlib

from .bool2d.base import EmptyShape, WholeShape
from .bool2d.primitive import Primitive
from .bool2d.shape import ConnectedShape, DisjointShape, SimpleShape
from .common import lebesgue_density, move, rotate, scale
from .geometry.integral import IntegrateJordan
from .geometry.jordancurve import JordanCurve
from .geometry.point import Point2D
from .geometry.segment import Segment
from .loggers import set_level
from .plot.plot import ShapePloter

__version__ = importlib.metadata.version("shapepy")

set_level("shapepy", level="INFO")
# set_level("shapepy.bool2d", level="DEBUG")
# set_level("shapepy.rbool", level="DEBUG")


if __name__ == "__main__":
    pass
