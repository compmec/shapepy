"""
This module analyse sections of beams by using the boundary element method
It uses mainly curves as boundary to compute the elements.
For the moment, it only uses polygon shapes:
    retangular is a 4-side shape while a circle is a polygon with many sides
"""

from shapepy.core import Empty, Whole
from shapepy.curve import IntegratePlanar, PlanarCurve
from shapepy.jordancurve import IntegrateJordan, JordanCurve
from shapepy.plot import ShapePloter
from shapepy.point import Point2D
from shapepy.primitive import Primitive
from shapepy.shape import (
    ConnectedShape,
    DisjointShape,
    IntegrateShape,
    SimpleShape,
)

__version__ = "1.1.0"

if __name__ == "__main__":
    pass
