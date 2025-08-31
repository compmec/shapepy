"""
Defines the Density class that is used for the subsets to verify
the density of a given point a

It's the Lebesgue density.
"""

from __future__ import annotations

from typing import Iterable, Optional, Union

from ..analytic.tools import find_minimum, where_minimum
from ..geometry.integral import IntegrateJordan
from ..geometry.jordancurve import JordanCurve
from ..geometry.point import Point2D
from ..geometry.segment import Segment
from ..loggers import debug
from ..rbool import EmptyR1, SingleR1, SubSetR1, create_interval, subset_length
from ..scalar.angle import Angle, degrees
from ..scalar.reals import Real
from ..tools import Is, NotExpectedError, To


@debug("shapepy.bool2d.density")
def half_density_jordan(
    segments: Iterable[Segment], point: Point2D
) -> Density:
    """Computes the value of the density when the point is at
    an smooth edge of any of the given segments
    """
    for segment in segments:
        deltax = segment.xfunc - point.xcoord
        deltay = segment.yfunc - point.ycoord
        radius_square = deltax * deltax + deltay * deltay
        minimal = find_minimum(radius_square, [0, 1])
        if minimal < 1e-6:
            place = where_minimum(radius_square, [0, 1])
            if not Is.instance(place, SingleR1):
                raise NotExpectedError(f"Not single value: {place}")
            parameter = To.finite(place.internal)
            angle = segment(parameter, 1).angle
            return line(angle)
    raise NotExpectedError("Not found minimum < 1e-6")


@debug("shapepy.bool2d.density")
def lebesgue_density_jordan(
    jordan: JordanCurve, point: Optional[Point2D] = (0.0, 0.0)
) -> Density:
    """Computes the lebesgue density number from jordan curve

    Returns a value in the interval [0, 1]:
    * 0 -> means the point is outside the interior region
    * 1 -> means the point is completly inside the interior
    * between 0 and 1, it's on the boundary
    """
    point = To.point(point)
    box = jordan.box()
    if point not in box:
        return Density.zero if jordan.area > 0 else Density.one

    segments = tuple(jordan.parametrize())
    for i, segmenti in enumerate(segments):
        if point == segmenti(0):
            segmentj = segments[(i - 1) % len(segments)]
            anglei = segmenti(0, 1).angle
            anglej = segmentj(1, 1).angle
            return sector(anglei, ~anglej)

    turns = IntegrateJordan.turns(jordan, point)
    density = turns if jordan.area > 0 else 1 + turns
    if density == 0.5:
        return half_density_jordan(segments, point)
    return Density.one if round(density) == 1 else Density.zero


@debug("shapepy.bool2d.density")
def line(angle: Angle) -> Density:
    """Creates a Density of value 0.5 aligned with given angle"""
    angle = To.angle(angle)
    return sector(angle, angle + degrees(180))


@debug("shapepy.bool2d.density")
def sector(anglea: Angle, angleb: Angle) -> Density:
    """Creates a Density instance within given two angles"""
    uvala: Real = To.angle(anglea).turns % 1
    uvalb: Real = To.angle(angleb).turns % 1
    if uvalb == 0:
        subset = create_interval(uvala, 1)
    elif uvala < uvalb:
        subset = create_interval(uvala, uvalb)
    else:
        subset = create_interval(0, uvalb) | create_interval(uvala, 1)
    return Density(subset)


class Density:
    """
    Density class that stores the sectors of circles that allows computing
    the density of union and intersection of some subsets
    """

    zero: Density = None
    one: Density = None

    def __init__(self, subset: SubSetR1):
        if not Is.instance(subset, SubSetR1):
            raise TypeError
        if subset not in create_interval(0, 1):
            raise ValueError(f"{subset} not in [0, 1]")
        self.subset = subset

    def __float__(self) -> float:
        value = subset_length(self.subset)
        return float(value)

    def __invert__(self) -> Density:
        return Density(create_interval(0, 1) - self.subset)

    def __or__(self, value: Density):
        if not Is.instance(value, Density):
            raise TypeError
        return Density(self.subset | value.subset)

    def __and__(self, value: Density):
        if not Is.instance(value, Density):
            raise TypeError
        return Density(self.subset & value.subset)

    def __str__(self):  # pragma: no cover
        return str(float(self))

    def __repr__(self):  # pragma: no cover
        return "D" + str(self)

    @debug("shapepy.bool2d.density")
    def __eq__(self, value: Union[Real, Density]) -> bool:
        return abs(float(self) - float(value)) < 1e-6


Density.zero = Density(EmptyR1())
Density.one = Density(create_interval(0, 1))


@debug("shapepy.bool2d.density")
def unite_densities(densities: Iterable[Density]) -> Density:
    """Computes the union of Density units"""
    densities = iter(densities)
    result = next(densities)
    if not Is.instance(result, Density):
        raise TypeError(f"Invalid {type(result)}")
    for density in densities:
        if not Is.instance(density, Density):
            raise TypeError(f"Invalid {type(density)}")
        result |= density
    return result


@debug("shapepy.bool2d.density")
def intersect_densities(densities: Iterable[Density]) -> Density:
    """Computes the intersection of Density units"""
    densities = iter(densities)
    result = next(densities)
    if not Is.instance(result, Density):
        raise TypeError(f"Invalid {type(result)}")
    for density in densities:
        if not Is.instance(density, Density):
            raise TypeError(f"Invalid {type(density)}")
        result &= density
    return result
