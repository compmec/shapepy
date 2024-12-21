"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""

from __future__ import annotations

from typing import Iterable, Union

from ..boolean import BoolAnd, BoolOr
from ..core import Empty, IBoolean2D, IObject2D, IShape, Scalar, Whole
from ..curve.abc import ICurve, IJordanCurve
from ..point import GeneralPoint, Point2D
from .boolean import JordanContainer, intersect_containers, unite_containers


def shape_to_container(shape: IShape) -> JordanContainer:
    if not isinstance(shape, IShape):
        raise TypeError(f"Not a IShape instance, but {type(shape)}")
    if isinstance(shape, SimpleShape):
        alljordans = [(shape.jordan,)]
    elif isinstance(shape, ConnectedShape):
        alljordans = [tuple(sub.jordan for sub in shape)]
    elif isinstance(shape, DisjointShape):
        alljordans = []
        for sub in shape:
            if isinstance(sub, SimpleShape):
                current = [sub.jordan]
            elif isinstance(sub, ConnectedShape):
                current = tuple(s.jordan for s in sub)
            alljordans.append(current)
    return JordanContainer(alljordans)


def container_to_shape(container: JordanContainer) -> IShape:
    allconshapes = []
    for jords in container.alljords:
        simples = tuple(SimpleShape(jordan) for jordan in jords)
        conshape = ConnectedShape(simples) if len(simples) > 1 else simples[0]
        allconshapes.append(conshape)
    if len(allconshapes) == 1:
        return allconshapes[0]
    return DisjointShape(allconshapes)


def decide_boundary(
    jordan: IJordanCurve, controls: Iterable[IShape], union: bool
) -> IShape:
    if not isinstance(jordan, IJordanCurve):
        raise TypeError

    curve = jordan.param_curve
    knots = curve.knots
    posmidpts = [True] * (len(knots) - 1)
    for i, (knota, knotb) in enumerate(zip(knots, knots[1:])):
        midpoint = curve.eval((knota + knotb) / 2, 0)
        positions = (midpoint in subctrl for subctrl in controls)
        posmidpts[i] = any(positions) if union else all(positions)
    return all(posmidpts)


def unite_shapes(*shapes: IShape) -> IBoolean2D:
    containers = tuple(map(shape_to_container, shapes))
    new_jordans = tuple(unite_containers(containers))
    if len(new_jordans) == 0:
        return Whole()
    simples = []
    for jordan in new_jordans:
        boundary = decide_boundary(jordan, shapes, True)
        simples.append(SimpleShape(jordan, boundary))
    shape = identify_shape(simples)
    return shape


def intersect_shapes(*shapes: IShape) -> IBoolean2D:
    containers = tuple(map(shape_to_container, shapes))
    new_jordans = tuple(intersect_containers(containers))
    if len(new_jordans) == 0:
        return Empty()
    simples = []
    for jordan in new_jordans:
        boundary = decide_boundary(jordan, shapes, False)
        simples.append(SimpleShape(jordan, boundary))
    shape = identify_shape(simples)
    return shape


def close_shape(shape: IShape) -> IShape:
    """
    Gives a new closed shape that contains all the boundaries.

    Parameters
    ----------
    shape: IShape
        The shape to be closed
    return: IShape:
        The new closed shape, a new instance
    """
    if not isinstance(shape, IShape):
        raise TypeError
    if isinstance(shape, SimpleShape):
        return SimpleShape(shape.jordan, True)
    return shape.__class__(map(close_shape, shape))


def identify_shape(
    simples: Iterable[SimpleShape],
) -> IShape:
    """
    Identify the final shape (Simple, Connected, Disjoint) from the
    received simple shapes
    """
    simples = tuple(simples)
    for simple in simples:
        if not isinstance(simple, SimpleShape):
            raise TypeError(f"Received {type(simple)}")
    if len(simples) == 1:
        return simples[0]

    def sorter(jordan):
        return jordan.area

    simples = sorted(simples, key=sorter)
    disshapes = []
    while simples:
        connsimples = [simples.pop(len(simples) - 1)]
        index = 0
        while index < len(simples):
            simple = simples[index]
            for simplj in connsimples:
                if simple.jordan not in simplj:
                    break
                if simplj.jordan not in simple:
                    break
            else:
                connsimples.append(simples.pop(index))
                index -= 1
            index += 1
        if len(connsimples) == 1:
            conshape = connsimples[0]
        else:
            conshape = ConnectedShape(connsimples)
        disshapes.append(conshape)
    return disshapes[0] if len(disshapes) == 1 else DisjointShape(disshapes)


class SimpleShape(IShape):
    """
    SimpleShape class

    Is a shape which is defined by only one jordan curve.
    It represents the interior/exterior region of the jordan curve
    if the jordan curve is counter-clockwise/clockwise

    """

    def __init__(self, jordancurve: IJordanCurve, boundary: bool = True):
        if not isinstance(jordancurve, IJordanCurve):
            raise TypeError
        self.__jordan = jordancurve
        self.boundary = boundary

    @property
    def jordan(self) -> IJordanCurve:
        """
        The jordan's curve that defines the Simple Shape
        """
        return self.__jordan

    @property
    def area(self) -> Scalar:
        """
        The area defined by the jordan's curve.
        It's negative if jordans is clockwise
        """
        return self.jordan.area

    @property
    def boundary(self) -> bool:
        """
        Flag that tells if shape contains the boundary or not
        """
        return self.__boundary

    @boundary.setter
    def boundary(self, newval: bool):
        self.__boundary = bool(newval)

    def __str__(self) -> str:
        msg = f"Simple Shape of area {self.area} with vertices:\n"
        msg += "[" + ",\n ".join(map(str, self.jordan.vertices)) + "]"
        return msg

    def __repr__(self) -> str:
        area, vertices = self.area, self.jordan.vertices
        msg = f"Simple shape of area {area} with {len(vertices)} vertices"
        return msg

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IObject2D):
            raise ValueError
        if not isinstance(other, SimpleShape):
            return False
        if self.area != other.area:
            return False
        if self.boundary != other.boundary:
            return False
        return self.jordan == other.jordan

    def __neg__(self) -> SimpleShape:
        return self.__class__(~self.jordan, not self.boundary)

    def __contains_curve(self, curve: ICurve) -> bool:
        if not isinstance(curve, ICurve):
            raise TypeError
        if not all(map(self.__contains__, curve.vertices)):
            return False
        nnodes = 64
        unodes = tuple(i / nnodes for i in range(1, nnodes))
        param_curve = curve.param_curve
        pairs = zip(param_curve.knots, param_curve.knots[1:])
        for knota, knotb in pairs:
            for unode in unodes:
                tnode = (1 - unode) * knota + unode * knotb
                if param_curve.eval(tnode, 0) not in self:
                    return False
        return True

    def __contains_simple(self, other: SimpleShape) -> bool:
        if not isinstance(other, SimpleShape):
            raise TypeError
        spos = self.area > 0
        opos = other.area > 0
        if spos ^ opos:
            if spos and not opos:
                return False
        elif self.area < other.area:
            return False
        elif spos and opos:
            return other.jordan in self
        elif self == other:
            return True
        if self.boundary or other.boundary:
            return other.jordan in self and self.jordan not in other
        simp = SimpleShape(self.jordan, True)
        return other.jordan in simp and self.jordan not in other

    def __contains__(self, other):
        if not isinstance(other, IObject2D):
            other = Point2D(other)
        if isinstance(other, Point2D):
            wind = self.winding(other)
            return wind == 1 or (0 < wind and self.boundary)
        if isinstance(other, BoolOr):
            return all(sub in self for sub in other)
        if isinstance(other, BoolAnd):
            return ~self in ~other
        if isinstance(other, ICurve):
            return self.__contains_curve(other)
        if isinstance(other, SimpleShape):
            return self.__contains_simple(other)
        return isinstance(other, Empty)

    def winding(self, point: GeneralPoint) -> Scalar:
        """
        Computes the winding number relative to the given point

        Parameters
        ----------
        point: Point2D
            The point to check its position
        return: Scalar
            Number in the interval [0, 1]
            0 means the point is outside the simple shape
            1 means the point is inside the simple shape
            other means it's on the boundary
        """
        return self.jordan.winding(point)

    def move(self, vector: GeneralPoint) -> SimpleShape:
        """
        Moves the simple shape in the plane by the given vector

        Parameters
        ----------
        vector: Point
            The pair (x, y) that must be added to the coordinates
        return: SimpleShape
            The moved simple shape

        """
        return self.__class__(self.jordan.move(vector), self.boundary)

    def scale(self, xscale: Scalar, yscale: Scalar) -> Point2D:
        """
        Scales the object in the X and Y directions

        Parameters
        ----------
        xscale: Scalar
            The amount to be scaled in the X direction
        yscale: Scalar
            The amount to be scaled in the Y direction
        """
        return self.__class__(self.jordan.scale(xscale, yscale), self.boundary)

    def rotate(self, uangle: Scalar, degrees: bool = False) -> Point2D:
        """
        Rotates the simple shape around the origin.

        The angle mesure is unitary:
        * angle = 1 means 360 degrees rotation
        * angle = 0.5 means 180 degrees rotation
        * angle = 0.125 means 45 degrees rotation

        Parameters
        ----------
        angle: Scalar
            The unitary angle the be rotated.
        degrees: bool, default = False
            If the angle is mesure in degrees
        """
        return self.__class__(
            self.jordan.rotate(uangle, degrees), self.boundary
        )


class ConnectedShape(IShape, BoolAnd):

    """
    ConnectedShape Class

    A shape defined by intersection of two or more SimpleShapes

    """

    def __init__(self, subshapes: Iterable[SimpleShape]):
        subshapes = tuple(subshapes)
        for subshape in subshapes:
            if not isinstance(subshape, SimpleShape):
                raise TypeError
        super().__init__(subshapes)

    def __str__(self) -> str:
        msg = f"Connected shape total area {self.area}"
        return msg

    def __eq__(self, other: IObject2D) -> bool:
        if not isinstance(other, ConnectedShape):
            return False
        if abs(self.area - other.area) > 1e-6:
            return False
        return True

    def __neg__(self) -> DisjointShape:
        return DisjointShape(~simple for simple in self)

    @property
    def area(self) -> Scalar:
        return sum(subshape.area for subshape in self)

    def winding(self, point: GeneralPoint) -> Scalar:
        """
        Computes the winding number relative to the given point

        Parameters
        ----------
        point: Point2D
            The point to check its position
        return: Scalar
            Number in the interval [0, 1]
            0 means the point is outside the simple shape
            1 means the point is inside the simple shape
            other means it's on the boundary
        """
        for subshape in self:
            wind = subshape.winding(point)
            if wind != 1:
                return wind
        return 1


class DisjointShape(IShape, BoolOr):
    """
    DisjointShape Class

    A shape defined by the union of some SimpleShape instances and
    ConnectedShape instances
    """

    def __init__(
        self, subshapes: Iterable[Union[SimpleShape, ConnectedShape]]
    ):
        subshapes = tuple(subshapes)
        for subshape in subshapes:
            if not isinstance(subshape, (SimpleShape, ConnectedShape)):
                raise TypeError
        super().__init__(subshapes)

    @property
    def area(self) -> Scalar:
        return sum(subshape.area for subshape in self)

    def __eq__(self, other: IObject2D):
        if not isinstance(other, DisjointShape):
            return False
        if self.area != other.area:
            return False
        self_subshapes = list(self)
        othe_subshapes = list(other)
        # Compare if a curve is inside another
        while len(self_subshapes) > 0 and len(othe_subshapes) > 0:
            for j, osbshape in enumerate(othe_subshapes):
                if osbshape.area != self_subshapes[0].area:
                    continue
                if osbshape == self_subshapes[0]:
                    self_subshapes.pop(0)
                    othe_subshapes.pop(j)
                    break
            else:
                return False
        return not (len(self_subshapes) or len(othe_subshapes))

    def __neg__(self):
        simples = []
        for sub in self:
            if isinstance(sub, SimpleShape):
                simples.append(-sub)
            elif isinstance(sub, ConnectedShape):
                simples += [-s for s in sub]
        return identify_shape(simples)

    def __str__(self) -> str:
        msg = f"Disjoint shape with total area {self.area} and "
        msg += f"{len(self)} subshapes"
        return msg

    def winding(self, point: GeneralPoint) -> Scalar:
        """
        Computes the winding number relative to the given point

        Parameters
        ----------
        point: Point2D
            The point to check its position
        return: Scalar
            Number in the interval [0, 1]
            0 means the point is outside the simple shape
            1 means the point is inside the simple shape
            other means it's on the boundary
        """
        return sum(sub.winding(point) for sub in self)

    def __contains__(self, other):
        if isinstance(other, BoolOr):
            return all(sub in self for sub in other)
        return any(other in sub for sub in self)
