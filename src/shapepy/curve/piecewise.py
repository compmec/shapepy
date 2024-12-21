"""
This file contains the classes that defines a Piecewise Curve

It's the most generic type of curve, defined by
piecewise analytic functions
"""

from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Tuple

from ..analytic.utils import unit_angle
from ..core import IAnalytic, Math, Scalar
from ..point import GeneralPoint, Point2D
from .abc import (
    IClosedCurve,
    IJordanCurve,
    IOpenCurve,
    IParameterCurve,
    Parameter,
)


class PiecewiseCurve(IParameterCurve):
    """
    A general piecewise curve, that is defined by pairs of analytic functions
    """

    def __init__(self, functions: Iterable[Tuple[IAnalytic, IAnalytic]]):
        functions = tuple(functions)
        for func in functions:
            if len(func) != 2:
                raise ValueError
            if not isinstance(func[0], IAnalytic):
                raise TypeError
            if not isinstance(func[1], IAnalytic):
                raise TypeError
        for i, funci in enumerate(functions[:-1]):
            funcj = functions[i + 1]
            for fik, fjk in zip(funci, funcj):
                if fik.eval(i + 1) != fjk.eval(i + 1):
                    msg = f"Not continous curve: ({fik}) != ({fjk}) at ({i+1})"
                    raise ValueError(msg)
        self.__funcs = functions
        self.__lenght = compute_lenght(self)
        self.__knots = tuple(Fraction(i) for i in range(len(functions) + 1))

    @property
    def nsegs(self) -> int:
        """
        Gives the number of segments of the piecewise
        """
        return len(self.__funcs)

    @property
    def knots(self) -> Iterable[Parameter]:
        return self.__knots

    @property
    def functions(self) -> Iterable[Tuple[IAnalytic, IAnalytic]]:
        """
        Gives all the pairs of analytic functions that defines the curve
        """
        return self.__funcs

    @property
    def lenght(self) -> Scalar:
        return self.__lenght

    def eval(self, node: Parameter, derivate: int = 0) -> Point2D:
        index = int(Math.floor(node))
        if index == len(self.__funcs):
            index -= 1
        xfunc, yfunc = self.__funcs[index]
        xval = xfunc.eval(node, derivate)
        yval = yfunc.eval(node, derivate)
        return Point2D((xval, yval))

    def projection(self, point: GeneralPoint) -> Iterable[Parameter]:
        if not isinstance(point, Point2D):
            point = Point2D(point)
        nodes = set(self.knots)
        for i, (xfunc, yfunc) in enumerate(self.functions):
            deltax = xfunc - point[0]
            deltay = yfunc - point[1]
            dist2 = (deltax**2 + deltay**2).derivate()
            newnodes = set(dist2.roots(self.knots[i], self.knots[i + 1]))
            nodes |= newnodes
        nodes = tuple(sorted(nodes))
        vects = (self.eval(node) - point for node in nodes)
        squares = tuple(vect.norm2() for vect in vects)
        minsqua = min(squares)
        nodes = tuple(
            node for node, dist2 in zip(nodes, squares) if dist2 == minsqua
        )

        return nodes

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PiecewiseCurve):
            return False
        if self.nsegs != other.nsegs:
            return False
        for funis, funjs in zip(self.functions, other.functions):
            for funi, funj in zip(funis, funjs):
                if funi != funj:
                    return False
        return True

    def section(self, nodea: Parameter, nodeb: Parameter) -> IParameterCurve:
        if nodea == self.knots[0] and nodeb == self.knots[-1]:
            return self
        if not nodea < nodeb:
            raise ValueError
        indexa = int(Math.floor(nodea))
        indexb = int(Math.ceil(nodeb)) - 1
        if indexa == indexb:
            denom = 1 / (nodeb - nodea)
            xfunc, yfunc = self.functions[indexa]
            xfunc = xfunc.shift(-nodea).scale(denom)
            yfunc = yfunc.shift(-nodea).scale(denom)
            return PiecewiseOpenCurve(((xfunc, yfunc),))
        secfuncs = list(
            (xfunc.shift(-indexa), yfunc.shift(-indexa))
            for i, (xfunc, yfunc) in enumerate(self.functions)
            if indexa <= i <= indexb
        )
        if nodea != indexa:
            xfunc, yfunc = secfuncs[0]
            amount = indexa + 1 - nodea
            xfunc = xfunc.shift(indexa - nodea)
            yfunc = yfunc.shift(indexa - nodea)
            xfunc = xfunc.scale(amount)
            yfunc = yfunc.scale(amount)
            secfuncs[0] = (xfunc, yfunc)
        if indexb + 1 != nodeb:
            xfunc, yfunc = secfuncs[-1]
            amount = nodeb - indexb
            xfunc = xfunc.shift(indexa - indexb)
            yfunc = yfunc.shift(indexa - indexb)
            xfunc = xfunc.scale(amount)
            yfunc = yfunc.scale(amount)
            xfunc = xfunc.shift(indexb - indexa)
            yfunc = yfunc.shift(indexb - indexa)
            secfuncs[-1] = (xfunc, yfunc)
        return PiecewiseOpenCurve(secfuncs)


class PiecewiseOpenCurve(PiecewiseCurve, IOpenCurve):
    """
    A Piecewise Open Curve that doesn't connect its ending points
    """

    def eval(self, node: Parameter, derivate: int = 0) -> Point2D:
        if node < 0 or self.nsegs < node:
            raise ValueError
        return super().eval(node, derivate)

    @property
    def vertices(self) -> Tuple[Point2D, ...]:
        return tuple(map(self.eval, self.knots))


class PiecewiseClosedCurve(PiecewiseCurve, IClosedCurve):
    """
    A Piecewise Closed Curve defined by analytic functions
    """

    def __init__(self, functions: Tuple[Tuple[IAnalytic]]):
        super().__init__(functions)
        nsegs = self.nsegs
        for funci, funcj in zip(functions[0], functions[-1]):
            if funci.eval(0) != funcj.eval(nsegs):
                raise ValueError("Not continous closed curve")

    def winding(self, point: GeneralPoint) -> Scalar:
        if not isinstance(point, Point2D):
            point = Point2D(point)
        return compute_winding(self, point)

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

    def projection(self, point: GeneralPoint) -> Iterable[Parameter]:
        nodes = tuple(super().projection(point))
        if nodes and nodes[-1] == self.nsegs:
            nodes = nodes[:-1]
        return nodes


class JordanPiecewise(IJordanCurve, PiecewiseClosedCurve):
    """
    A Jordan Piecewise Curve that doesn't intersect itself
    """

    @property
    def param_curve(self) -> PiecewiseClosedCurve:
        return self


def compute_lenght(curve: PiecewiseCurve, tolerance: Scalar = 1e-9) -> Scalar:
    """
    Computes the lenght of the Piecewise curve

    Adaptative numerical integration is used to compute it

    Some curves that are easier to compute, like a Polygon,
    does not need integration
    """
    if not isinstance(curve, PiecewiseCurve):
        raise TypeError

    def direct_integral(pleft: Parameter, prigh: Parameter) -> Scalar:
        nodes = (1 / 4, 1 / 2, 3 / 4)
        weigs = (2 / 3, -1 / 3, 2 / 3)
        dsvas = map(Math.sqrt, map(ds2fun.eval, nodes))
        return (prigh - pleft) * sum(w * ds for w, ds in zip(weigs, dsvas))

    def adapt_integral(
        pleft: Parameter, prigh: Parameter, tolerance: Scalar
    ) -> Scalar:
        pmidd = (pleft + prigh) / 2
        imidd = direct_integral(pleft, prigh)
        ileft = direct_integral(pleft, pmidd)
        irigh = direct_integral(pmidd, prigh)
        if abs(ileft + irigh - imidd) >= tolerance:
            ileft = adapt_integral(pleft, pmidd, tolerance / 2)
            irigh = adapt_integral(pmidd, prigh, tolerance / 2)
        return ileft + irigh

    lenght = 0
    for i, (xfunc, yfunc) in enumerate(curve.functions):
        dxfunc = xfunc.derivate()
        dyfunc = yfunc.derivate()
        ds2fun = dxfunc**2 + dyfunc**2
        lenght += adapt_integral(i, i + 1, tolerance)

    return lenght


# pylint: disable=too-many-locals
def compute_winding(curve: PiecewiseClosedCurve, point: Point2D) -> Scalar:
    """
    Computes the winding number of the given point

    Parameters
    ----------
    curve: PiecewiseClosedCurve
        The closed curve that surronds (or not) the point
    point: Point2D
        The point to be computed the winding number
    """
    if not isinstance(curve, PiecewiseClosedCurve):
        raise TypeError
    if not isinstance(point, Point2D):
        raise TypeError

    nodes = curve.projection(point)
    if len(nodes) == 1:
        node = nodes[0]
        curpt = curve.eval(node)
        if curpt == point:
            if node != int(node):  # Not a vertex
                return 0.5
            node = int(node)
            xleft, yleft = curve.functions[node - 1]
            xrigh, yrigh = curve.functions[node]
            if node != curve.knots[0]:
                dxl = xleft.eval(node, 1)
                dyl = yleft.eval(node, 1)
            else:
                dxl = xleft.eval(curve.knots[-1], 1)
                dyl = yleft.eval(curve.knots[-1], 1)
            dxr = xrigh.eval(node, 1)
            dyr = yrigh.eval(node, 1)
            inner = dxl * dxr + dyl * dyr
            cross = dxl * dyr - dyl * dxr
            angle = unit_angle(-inner, cross)
            return 0.5 if angle == -1 else angle

    # Getting here, the only possible result is either 0 or 1
    nodes = sorted(set(nodes) | set(curve.knots))
    vertices = tuple(curve.eval(node) - point for node in nodes)
    nverts = len(nodes)
    wind: Scalar = 0
    for i, vertex0 in enumerate(vertices):
        vertex1 = vertices[(i + 1) % nverts]
        cross = float(vertex0.cross(vertex1))
        inner = float(vertex0.inner(vertex1))
        subwind = unit_angle(inner, cross)
        wind += subwind

    if abs(wind) < 1e-9:
        wind = 0
    elif abs(wind - 1) < 1e-9:
        wind = 1
    elif abs(wind + 1) < 1e-9:
        wind = -1
    if curve.area > 0:
        return wind
    return 0 if abs(wind + 1) < 1e-9 else 1 - wind
