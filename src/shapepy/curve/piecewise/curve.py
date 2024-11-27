from __future__ import annotations

import math
from typing import Iterable, Tuple

from ...core import IAnalytic, Scalar
from ...point import GeneralPoint, Point2D
from ..abc import IClosedCurve, IOpenCurve, IParameterCurve, Parameter


class Piecewise(IParameterCurve):

    def __init__(self, functions: Tuple[Tuple[IAnalytic, IAnalytic], ...]):
        functions = tuple(functions)
        for func in functions:
            if len(func) != 2:
                raise ValueError
            if not isinstance(func[0], IAnalytic):
                raise TypeError
            if not isinstance(func[1], IAnalytic):
                raise TypeError
        self.__funcs = functions

    @property
    def nsegs(self) -> int:
        return len(self.__funcs)

    @property
    def knots(self) -> Tuple[Parameter, ...]:
        return tuple(range(self.nsegs + 1))

    @property
    def functions(self) -> Tuple[Tuple[IAnalytic, IAnalytic], ...]:
        return self.__funcs

    @property
    def lenght(self) -> Scalar:
        raise NotImplementedError

    def eval(self, node: Parameter, derivate: int = 0) -> Point2D:
        index = int(math.floor(node))
        xfunc, yfunc = self.__funcs[index]
        xval = xfunc.eval(node, derivate)
        yval = yfunc.eval(node, derivate)
        return Point2D((xval, yval))

    def projection(self, point: GeneralPoint) -> Iterable[Parameter]:
        raise NotImplementedError

    def section(self, nodea: Parameter, nodeb: Parameter) -> IParameterCurve:
        raise NotImplementedError

    def winding(self, point: GeneralPoint) -> Scalar:
        raise NotImplementedError


class PiecewiseOpenCurve(Piecewise, IOpenCurve):

    def eval(self, node: Parameter, derivate: int = 0) -> Point2D:
        if node < 0 or self.nsegs < node:
            raise ValueError
        return super().eval(node, derivate)

    @property
    def vertices(self) -> Tuple[Point2D, ...]:
        return tuple(map(self.eval, self.knots))


class PiecewiseClosedCurve(Piecewise, IClosedCurve):

    def eval(self, node: Parameter, derivate: int = 0) -> Point2D:
        node %= self.nsegs
        return super().eval(node, derivate)

    @property
    def area(self) -> Scalar:
        area = 0
        for i, (xfunc, yfunc) in enumerate(self.functions):
            dxfun = xfunc.derivate(1)
            dyfun = yfunc.derivate(1)
            func = xfunc * dyfun - yfunc * dxfun
            area += func.defintegral(i, i + 1)
        return area / 2

    @property
    def vertices(self) -> Tuple[Point2D, ...]:
        return tuple(map(self.eval, self.knots[:-1]))
