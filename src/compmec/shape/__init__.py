"""
This module analyse sections of beams by using the boundary element method
It uses mainly curves as boundary to compute the elements.
For the moment, it only uses polygon shapes:
    retangular is a 4-side shape while a circle is a polygon with many sides
"""
from compmec.shape import primitive
from compmec.shape.jordancurve import JordanCurve, JordanPolygon
from compmec.shape.shape import SimpleShape

__version__ = "0.1.0"

if __name__ == "__main__":
    pass
