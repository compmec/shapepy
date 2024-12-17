import math
from typing import Iterable, List, Tuple

from .analytic.trigonometric import Trignomial
from .boolean import BoolAnd, BoolNot, BoolOr
from .core import Empty, IBoolean2D, ICurve, IObject2D, IShape, Scalar, Whole
from .curve import JordanPolygon, PolygonClosedCurve, PolygonOpenCurve
from .point import GeneralPoint, Point2D
from .shape import ConnectedShape, DisjointShape, SimpleShape
from .shape.boolean import (
    close_shape,
    flatten2simples,
    identify_shape,
    intersect_shapes,
    open_shape,
    unite_shapes,
)
from .utils import permutations, sorter


def close(object: IBoolean2D) -> IBoolean2D:
    """
    Set boundaries to True
    """
    if isinstance(object, (Empty, Whole, Point2D)):
        return object
    if isinstance(object, IShape):
        return close_shape(object)
    raise NotImplementedError("Not expected get here")


def open(object: IBoolean2D) -> IBoolean2D:
    """
    Set boundaries to False
    """
    if isinstance(object, (Empty, Whole, Point2D)):
        return object
    if isinstance(object, IShape):
        return open_shape(object)
    raise NotImplementedError("Not expected get here")


class Configuration:
    autoexpand = True
    autosimplify = True


class Transformation:
    @staticmethod
    def move_point(object: Point2D, point: Point2D) -> Point2D:
        return Point2D(object[0] + point[0], object[1] + point[1])

    @staticmethod
    def scale_point(
        object: Point2D, xscale: Scalar, yscale: Scalar
    ) -> Point2D:
        return Point2D(xscale * object[0], yscale * object[1])

    @staticmethod
    def rotate_point(object: Point2D, angle: Scalar) -> Point2D:
        sin, cos = Trignomial.sincos(angle)
        oldx, oldy = object[0], object[1]
        newx = oldx * cos - oldy * sin
        newy = oldx * sin + oldy * cos
        return Point2D(newx, newy)

    @staticmethod
    def move_curve(object: ICurve, point: Point2D) -> ICurve:
        if not isinstance(object, ICurve):
            raise TypeError
        if not isinstance(point, Point2D):
            raise TypeError
        if isinstance(
            object, (JordanPolygon, PolygonOpenCurve, PolygonClosedCurve)
        ):
            new_vertices = (
                Transformation.move_point(vertex, point)
                for vertex in object.vertices
            )
            return object.__class__(tuple(new_vertices))
        raise NotImplementedError("Not expected to get here")

    @staticmethod
    def scale_curve(object: ICurve, xscale: Scalar, yscale: Scalar) -> ICurve:
        if not isinstance(object, ICurve):
            raise TypeError
        if isinstance(
            object, (JordanPolygon, PolygonOpenCurve, PolygonClosedCurve)
        ):
            new_vertices = (
                Transformation.scale_point(vertex, xscale, yscale)
                for vertex in object.vertices
            )
            return object.__class__(tuple(new_vertices))
        raise NotImplementedError("Not expected to get here")

    @staticmethod
    def rotate_curve(object: ICurve, angle: Scalar) -> ICurve:
        if not isinstance(object, ICurve):
            raise TypeError
        if isinstance(
            object, (JordanPolygon, PolygonOpenCurve, PolygonClosedCurve)
        ):
            new_vertices = (
                Transformation.rotate_point(vertex, angle)
                for vertex in object.vertices
            )
            return object.__class__(tuple(new_vertices))
        raise NotImplementedError("Not expected to get here")

    @staticmethod
    def move_shape(object: IShape, point: Point2D) -> IShape:
        if not isinstance(object, IShape):
            raise TypeError(f"Received type {type(object)}")
        if isinstance(object, SimpleShape):
            newjordan = Transformation.move(object.jordan, point)
            return SimpleShape(newjordan, object.boundary)
        newsubshapes = tuple(
            Transformation.move_shape(subshape, point) for subshape in object
        )
        return object.__class__(newsubshapes)

    @staticmethod
    def scale_shape(object: IShape, xscale: Scalar, yscale: Scalar) -> IShape:
        if not isinstance(object, IShape):
            raise TypeError(f"Received type {type(object)}")
        if isinstance(object, SimpleShape):
            newjordan = Transformation.scale_curve(
                object.jordan, xscale, yscale
            )
            return SimpleShape(newjordan, object.boundary)
        newsubshapes = tuple(
            Transformation.scale_shape(subshape, xscale, yscale)
            for subshape in object
        )
        return object.__class__(newsubshapes)

    @staticmethod
    def rotate_shape(object: IShape, angle: Scalar) -> IShape:
        if not isinstance(object, IShape):
            raise TypeError(f"Received type {type(object)}")
        if isinstance(object, SimpleShape):
            newjordan = Transformation.rotate_curve(object.jordan, angle)
            return SimpleShape(newjordan, object.boundary)
        newsubshapes = tuple(
            Transformation.rotate_shape(subshape, angle) for subshape in object
        )
        return object.__class__(newsubshapes)

    @staticmethod
    def move(object: IObject2D, point: GeneralPoint) -> IObject2D:
        if not isinstance(point, IObject2D):
            point = Point2D(point)
        if isinstance(object, (Empty, Whole)):
            return object
        if isinstance(object, Point2D):
            return Transformation.move_point(object, point)
        if isinstance(object, ICurve):
            return Transformation.move_curve(object, point)
        if isinstance(object, IShape):
            return Transformation.move_shape(object, point)
        raise NotImplementedError("Not expected to get here")

    @staticmethod
    def scale(object: IObject2D, xscale: Scalar, yscale: Scalar) -> IObject2D:
        if not isinstance(object, IObject2D):
            object = Point2D(object)
        if isinstance(object, (Empty, Whole)):
            return object
        if isinstance(object, Point2D):
            return Transformation.scale_point(object, xscale, yscale)
        if isinstance(object, ICurve):
            return Transformation.scale_curve(object, xscale, yscale)
        if isinstance(object, IShape):
            return Transformation.scale_shape(object, xscale, yscale)
        raise NotImplementedError("Not expected to get here")

    @staticmethod
    def rotate(object: IObject2D, angle: Scalar) -> IObject2D:
        if not isinstance(object, IObject2D):
            object = Point2D(object)
        if isinstance(object, (Empty, Whole)):
            return object
        if isinstance(object, Point2D):
            return Transformation.rotate_point(object, angle)
        if isinstance(object, ICurve):
            return Transformation.rotate_curve(object, angle)
        if isinstance(object, IShape):
            return Transformation.rotate_shape(object, angle)
        raise NotImplementedError("Not expected to get here")


class Contains:
    @staticmethod
    def point_in_curve(curve: ICurve, point: Point2D) -> bool:
        if not isinstance(point, Point2D):
            raise TypeError
        if not isinstance(curve, ICurve):
            raise TypeError
        return 0 < curve.winding(point) < 1

    @staticmethod
    def point_in_shape(shape: IShape, point: Point2D) -> bool:
        if not isinstance(point, Point2D):
            raise TypeError
        if not isinstance(shape, IShape):
            raise TypeError
        if isinstance(shape, SimpleShape):
            wind = shape.jordan.winding(point)
            return wind == 1 or (0 < wind and shape.boundary)
        if isinstance(shape, ConnectedShape):
            return all(Contains.point_in_shape(sub, point) for sub in shape)
        if isinstance(shape, DisjointShape):
            return any(Contains.point_in_shape(sub, point) for sub in shape)
        raise NotImplementedError(
            f"Not expected: {type(shape)}, {type(point)}"
        )

    @staticmethod
    def curve_in_simple(object: SimpleShape, other: ICurve) -> bool:
        if not isinstance(object, SimpleShape):
            raise TypeError
        if not isinstance(other, ICurve):
            raise TypeError
        if not all(vertex in object for vertex in other.vertices):
            return False
        nnodes = 64
        unodes = tuple(i / nnodes for i in range(1, nnodes))
        param_curve = other.param_curve
        for ka, kb in zip(param_curve.knots, param_curve.knots[1:]):
            for unode in unodes:
                tnode = (1 - unode) * ka + unode * kb
                if param_curve.eval(tnode, 0) not in object:
                    return False
        return True

    @staticmethod
    def simple_in_simple(object: SimpleShape, other: SimpleShape) -> bool:
        if not isinstance(object, SimpleShape):
            raise TypeError
        if not isinstance(other, SimpleShape):
            raise TypeError
        spos = object.area > 0
        opos = other.area > 0
        if spos ^ opos:
            if spos and not opos:
                return False
        elif object.area < other.area:
            return False
        elif spos and opos:
            return other.jordan in object
        elif object == other:
            return True
        if object.boundary or other.boundary:
            return other.jordan in object and object.jordan not in other
        object = SimpleShape(object.jordan, True)
        return other.jordan in object and object.jordan not in other

    @staticmethod
    def shape_in_shape(object: IShape, other: IShape) -> bool:
        if not isinstance(object, IShape):
            raise TypeError
        if not isinstance(other, IShape):
            raise TypeError
        if isinstance(object, SimpleShape):
            if isinstance(other, SimpleShape):
                return Contains.simple_in_simple(object, other)
            invobj = -object
            if isinstance(other, ConnectedShape):
                return any(invobj in -sub for sub in other)
            return invobj in Simplify.simplify(-other)
        if isinstance(other, DisjointShape):
            return all(Contains.shape_in_shape(object, sub) for sub in other)
        if isinstance(object, ConnectedShape):
            return all(Contains.shape_in_shape(sub, other) for sub in object)
        if isinstance(object, DisjointShape):
            return any(Contains.shape_in_shape(sub, other) for sub in object)
        raise NotImplementedError(
            f"Not expected: {type(object)}, {type(other)}"
        )


class BooleanOperate:
    @staticmethod
    def contains(object: IBoolean2D, other: IBoolean2D) -> bool:
        if not isinstance(other, IBoolean2D):
            other = Point2D(other)
        if isinstance(object, (BoolAnd, ConnectedShape)):
            return other in object
        if isinstance(other, Empty) or isinstance(object, Whole):
            return True
        if isinstance(object, Empty):
            return isinstance(other, Empty)
        if isinstance(other, Whole):
            return isinstance(object, Whole)
        if object.ndim < other.ndim:
            return False
        if isinstance(object, (ConnectedShape, BoolAnd)):
            return all(BooleanOperate.contains(sub, other) for sub in object)
        if isinstance(other, (DisjointShape, BoolOr)):
            return all(BooleanOperate.contains(object, sub) for sub in other)
        if isinstance(object, IShape):
            if isinstance(other, IShape):
                return Contains.shape_in_shape(object, other)
            if isinstance(other, ICurve) and isinstance(object, SimpleShape):
                return Contains.curve_in_simple(object, other)
            if isinstance(other, Point2D):
                return Contains.point_in_shape(object, other)
        if isinstance(object, ICurve):
            if isinstance(other, Point2D):
                return Contains.point_in_curve(object, other)
        if isinstance(object, Point2D) and isinstance(other, Point2D):
            return object == other
        if isinstance(object, BoolNot) and isinstance(object.object, Point2D):
            return not BooleanOperate.contains(other, object.object)
        raise NotImplementedError(
            f"Not expected: {type(object)}, {type(other)}"
        )

    @staticmethod
    def invert(object: IBoolean2D) -> IBoolean2D:
        if isinstance(object, Empty):
            return Whole()
        if isinstance(object, Whole):
            return Empty()
        if isinstance(object, BoolNot):
            return object.object
        retorno = BoolNot(object)
        if Configuration.autoexpand:
            retorno = Simplify.expand(retorno)
        if Configuration.autosimplify:
            retorno = Simplify.simplify(retorno)
        return retorno

    @staticmethod
    def union(*objects: IBoolean2D) -> IBoolean2D:
        objects = tuple(objects)
        if any(isinstance(obj, Whole) for obj in objects):
            return Whole()
        objects = list(obj for obj in objects if not isinstance(obj, Empty))
        if len(objects) == 0:
            return Empty()
        if len(objects) == 1:
            return objects[0]
        for i, obj in enumerate(objects):
            if not isinstance(obj, IObject2D):
                objects[i] = Point2D(obj)
        ndims = (obj.ndim for obj in objects)
        objects = tuple(objects[i] for i in sorter(ndims))
        retorno = BoolOr(objects)
        if Configuration.autoexpand:
            retorno = Simplify.expand(retorno)
        if Configuration.autosimplify:
            retorno = Simplify.simplify(retorno)
        return retorno

    @staticmethod
    def intersect(*objects: IBoolean2D) -> IBoolean2D:
        objects = tuple(objects)
        if any(isinstance(obj, Empty) for obj in objects):
            return Empty()
        objects = tuple(obj for obj in objects if not isinstance(obj, Whole))
        if len(objects) == 0:
            return Whole()
        if len(objects) == 1:
            return objects[0]
        for i, obj in enumerate(objects):
            if not isinstance(obj, IObject2D):
                objects[i] = Point2D(obj)
        ndims = (obj.ndim for obj in objects)
        objects = tuple(objects[i] for i in sorter(ndims))
        retorno = BoolAnd(objects)
        if Configuration.autoexpand:
            retorno = Simplify.expand(retorno)
        if Configuration.autosimplify:
            retorno = Simplify.simplify(retorno)
        return retorno


class Simplify:
    @staticmethod
    def filter_equal(objects: Iterable[IObject2D]) -> Tuple[IObject2D, ...]:
        items: List[IObject2D] = []
        for subobj in objects:
            if not isinstance(subobj, IObject2D):
                raise TypeError
            for item in items:
                if subobj is item:
                    break
            else:
                items.append(subobj)
        return tuple(items)

    @staticmethod
    def has_inverse(objects: Tuple[IObject2D, ...]) -> bool:
        """
        Private function used in simplify to know if there's
        the union or intersection of inversed shape.

        Example:
            BoolOr(object, ~object) -> Whole
            Intersection(object, ~object) -> Empty
        """
        objects = tuple(objects)
        inveobjs = tuple(obj for obj in objects if isinstance(obj, BoolNot))
        normobjs = tuple(
            obj for obj in objects if not isinstance(obj, BoolNot)
        )
        for inveobj in inveobjs:
            for normobj in normobjs:
                if inveobj.object == normobj:
                    return True
        return False

    @staticmethod
    def flatten(object: IObject2D) -> IObject2D:
        """
        Flat the object, doing:

        or[or[A, B], C] = or[A, B, C]
        and[and[A, B], C] = and[A, B, C]
        """
        if not isinstance(object, (BoolOr, BoolAnd)):
            return object
        subobjs = tuple(object)
        items = []
        for subobj in subobjs:
            subobj = Simplify.flatten(subobj)
            if isinstance(subobj, object.__class__):
                items += list(subobj)
            else:
                items.append(subobj)
        return object.__class__(items)

    @staticmethod
    def expand_not(object: BoolNot) -> IObject2D:
        if not isinstance(object, BoolNot):
            raise TypeError
        invobj = object.object
        if isinstance(invobj, BoolOr):
            newobjs = map(BooleanOperate.invert, invobj)
            object = BooleanOperate.intersect(*newobjs)
        elif isinstance(invobj, BoolAnd):
            newobjs = map(BooleanOperate.invert, invobj)
            object = BooleanOperate.union(*newobjs)
        return object

    @staticmethod
    def expand_and(object: BoolAnd) -> IObject2D:
        if not isinstance(object, BoolAnd):
            raise TypeError
        subobjs = tuple(Simplify.flatten(object))
        sizes = [1] * len(subobjs)
        for i, subobj in enumerate(subobjs):
            if isinstance(subobj, BoolOr):
                sizes[i] = len(subobj)
        if all(size == 1 for size in sizes):
            return object
        subinters = []
        for indexs in permutations(*sizes):
            subitems = [subobjs[i] for i in indexs]
            subinters.append(BoolAnd(subitems))
        return Simplify.expand_or(BoolOr(subinters))

    @staticmethod
    def expand_or(object: BoolOr) -> IObject2D:
        if not isinstance(object, BoolOr):
            raise TypeError
        return Simplify.flatten(object)

    @staticmethod
    def expand(object: IObject2D) -> IObject2D:
        """
        Expand the object by using Morgan's law, to get something like

        Union[Intersection[Inversion[OBJECT]]]

        * not[A or B] -> (not A) and (not B)
        * not[A and B] -> (not A) or (not B)
        * and[A or B, C] -> (A and C) or (B and C)
        * or[A and B, C] -> or[A and B, C]

        """
        if not isinstance(object, IObject2D):
            raise TypeError
        if isinstance(object, BoolNot):
            return Simplify.expand_not(object)
        elif isinstance(object, BoolAnd):
            return Simplify.expand_and(object)
        elif isinstance(object, BoolOr):
            return Simplify.expand_or(object)
        return object

    @staticmethod
    def treat_contains_or(object: IBoolean2D) -> IBoolean2D:
        if not isinstance(object, BoolOr):
            return object
        subobjs = tuple(object)[::-1]
        filtered = set(range(len(subobjs)))
        for i, subi in enumerate(subobjs):
            for j in filtered:
                if j == i:
                    continue
                if subi in subobjs[j]:
                    filtered.remove(i)
                    break
        if len(filtered) == 1:
            return subobjs[tuple(filtered)[0]]
        return BoolOr(tuple(subobjs[i] for i in filtered))

    @staticmethod
    def treat_contains_and(object: IBoolean2D) -> IBoolean2D:
        if not isinstance(object, BoolAnd):
            return object
        subobjs = tuple(object)
        filtered = set(range(len(subobjs)))
        for i, subi in enumerate(subobjs):
            for j in filtered:
                if j == i:
                    continue
                if subobjs[j] in subi:
                    filtered.remove(i)
                    break
        if len(filtered) == 1:
            return subobjs[tuple(filtered)[0]]
        return BoolAnd(tuple(subobjs[i] for i in filtered))

    @staticmethod
    def treat_points(object: IBoolean2D) -> IBoolean2D:
        if not isinstance(object, BoolAnd):
            return object
        points = tuple(sub for sub in object if isinstance(sub, Point2D))
        for point in points:
            for sub in object:
                if point not in sub:
                    return Empty()
        if len(points) > 0:
            return points[0]
        return object

    @staticmethod
    def simplify_not(object: BoolNot) -> IObject2D:
        if not isinstance(object, BoolNot):
            raise TypeError
        invobj = object.object
        if isinstance(invobj, (Point2D, ICurve)):
            return object
        if isinstance(invobj, (SimpleShape, ConnectedShape)):
            return -invobj
        if isinstance(invobj, DisjointShape):
            simples = (~sub for sub in flatten2simples(invobj))
            return identify_shape(simples)
        raise NotImplementedError(f"Not expected get here: {object}")

    @staticmethod
    def simplify_and(object: BoolAnd) -> IObject2D:
        if not isinstance(object, BoolAnd):
            raise TypeError
        return object

    @staticmethod
    def simplify_or(object: BoolOr) -> IObject2D:
        if not isinstance(object, BoolOr):
            raise TypeError
        return object

    @staticmethod
    def simplify(object: IObject2D) -> IObject2D:
        if not isinstance(object, IObject2D):
            raise TypeError
        object = Simplify.expand(object)
        if not isinstance(object, (BoolNot, BoolOr, BoolAnd)):
            return object
        if isinstance(object, BoolNot):
            return Simplify.simplify_not(object)
        subobjs = tuple(map(Simplify.simplify, object))
        subobjs = Simplify.filter_equal(subobjs)
        if len(subobjs) == 1:
            return Simplify.simplify(subobjs[0])
        if Simplify.has_inverse(subobjs):
            if isinstance(object, BoolOr):
                return Whole()
            if isinstance(object, BoolAnd):
                return Empty()
            raise NotImplementedError("Not expected get here")
        object = object.__class__(subobjs)
        if isinstance(object, BoolOr):
            object = Simplify.treat_contains_or(object)
        elif isinstance(object, BoolAnd):
            object = Simplify.treat_contains_and(object)
            object = Simplify.treat_points(object)
        if not isinstance(object, (BoolOr, BoolAnd)):
            return object
        shapes = tuple(sub for sub in object if isinstance(sub, IShape))
        if len(shapes) > 1:
            others = [sub for sub in object if not isinstance(sub, IShape)]
            if isinstance(object, BoolOr):
                shape = unite_shapes(*shapes)
            elif isinstance(object, BoolAnd):
                shape = intersect_shapes(*shapes)
            others.append(shape)
            if isinstance(object, BoolAnd):
                object = BooleanOperate.intersect(*others)
            elif isinstance(object, BoolOr):
                object = BooleanOperate.union(*others)
            return Simplify.simplify(object)
        return object
