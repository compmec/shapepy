"""
This module analyse sections of beams by using the boundary element method
It uses mainly curves as boundary to compute the elements.
For the moment, it only uses polygon shapes:
    retangular is a 4-side shape while a circle is a polygon with many sides
"""
from compmec.shape.curve import IntegratePlanar, PlanarCurve
from compmec.shape.jordancurve import IntegrateJordan, JordanCurve
from compmec.shape.plot import ShapePloter
from compmec.shape.polygon import Point2D
from compmec.shape.primitive import Primitive
from compmec.shape.shape import (
    ConnectedShape,
    DisjointShape,
    EmptyShape,
    IntegrateShape,
    SimpleShape,
    WholeShape,
)

__version__ = "1.0.1"

if __name__ == "__main__":
    pass
