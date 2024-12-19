from typing import Any, Iterable, List, Tuple

from .boolean import BoolAnd, BoolNot, BoolOr
from .core import (
    Configuration,
    Empty,
    IBoolean2D,
    ICurve,
    IObject2D,
    IShape,
    Scalar,
    Whole,
)
from .curve import JordanPolygon, PolygonClosedCurve, PolygonOpenCurve
from .point import GeneralPoint, Point2D
from .shape import ConnectedShape, DisjointShape, SimpleShape
from .shape.boolean import (
    flatten2simples,
    identify_shape,
    intersect_shapes,
    unite_shapes,
)


def permutations(*numbers: int) -> Iterable[Tuple[int, ...]]:
    """
    Permutes the numbers using tensorproduct

    Example
    -------
    >>> permutations(4)
    [0, 1, 2, 3]
    >>> permutations(4, 2)
    [(0, 0), (0, 1), (1, 0), ..., (3, 0), (3, 0)]
    >>> permutations(2, 4, 1)
    [(0, 0, 0), ..., (1, 3, 1), (1, 3, 2)]
    """
    if len(numbers) == 1:
        for j in range(numbers[0]):
            yield j
        return
    for j in range(numbers[0]):
        for perm in permutations(*numbers[1:]):
            if isinstance(perm, int):
                yield (j, perm)
            else:
                yield (j,) + perm


def sorter(items: Iterable[Any], /, *, reverse: bool = False) -> Iterable[int]:
    """
    Gives the indexs of sorting of the objects

    Parameters
    ---------
    items: iterable[Any]
        The itens that must be sorted
    reverse: bool, default = False
        To switch between increasing/decreasing order

    Example
    -------
    >>> sorter([3, 4, 5])
    (0, 1, 2)
    >>> sorter([3, 5, 4])
    (0, 2, 1)
    """
    items = tuple(items)
    values = sorted(zip(items, range(len(items))), reverse=reverse)
    return (vs[-1] for vs in values)


class Transformation:
    @staticmethod
    def move_curve(obje: ICurve, vector: Point2D) -> ICurve:
        if not isinstance(obje, ICurve):
            raise TypeError
        if not isinstance(vector, Point2D):
            raise TypeError
        if isinstance(
            obje, (JordanPolygon, PolygonOpenCurve, PolygonClosedCurve)
        ):
            new_vertices = (vertex.move(vector) for vertex in obje.vertices)
            return obje.__class__(tuple(new_vertices))
        raise NotImplementedError("Not expected to get here")

    @staticmethod
    def scale_curve(obje: ICurve, xscale: Scalar, yscale: Scalar) -> ICurve:
        if not isinstance(obje, ICurve):
            raise TypeError
        if isinstance(
            obje, (JordanPolygon, PolygonOpenCurve, PolygonClosedCurve)
        ):
            new_vertices = (
                vertex.scale(xscale, yscale) for vertex in obje.vertices
            )
            return obje.__class__(tuple(new_vertices))
        raise NotImplementedError("Not expected to get here")

    @staticmethod
    def rotate_curve(obje: ICurve, uangle: Scalar) -> ICurve:
        if not isinstance(obje, ICurve):
            raise TypeError
        if isinstance(
            obje, (JordanPolygon, PolygonOpenCurve, PolygonClosedCurve)
        ):
            new_vertices = (vertex.rotate(uangle) for vertex in obje.vertices)
            return obje.__class__(tuple(new_vertices))
        raise NotImplementedError("Not expected to get here")

    @staticmethod
    def move_shape(obje: IShape, point: Point2D) -> IShape:
        if not isinstance(obje, IShape):
            raise TypeError(f"Received type {type(obje)}")
        if isinstance(obje, SimpleShape):
            newjordan = Transformation.move(obje.jordan, point)
            return SimpleShape(newjordan, obje.boundary)
        newsubshapes = tuple(
            Transformation.move_shape(subshape, point) for subshape in obje
        )
        return obje.__class__(newsubshapes)

    @staticmethod
    def scale_shape(obje: IShape, xscale: Scalar, yscale: Scalar) -> IShape:
        if not isinstance(obje, IShape):
            raise TypeError(f"Received type {type(obje)}")
        if isinstance(obje, SimpleShape):
            newjordan = Transformation.scale_curve(obje.jordan, xscale, yscale)
            return SimpleShape(newjordan, obje.boundary)
        newsubshapes = tuple(
            Transformation.scale_shape(subshape, xscale, yscale)
            for subshape in obje
        )
        return obje.__class__(newsubshapes)

    @staticmethod
    def rotate_shape(obje: IShape, uangle: Scalar) -> IShape:
        if not isinstance(obje, IShape):
            raise TypeError(f"Received type {type(obje)}")
        if isinstance(obje, SimpleShape):
            newjordan = Transformation.rotate_curve(obje.jordan, uangle)
            return SimpleShape(newjordan, obje.boundary)
        newsubshapes = tuple(
            Transformation.rotate_shape(subshape, uangle) for subshape in obje
        )
        return obje.__class__(newsubshapes)

    @staticmethod
    def move(obje: IObject2D, point: GeneralPoint) -> IObject2D:
        if not isinstance(point, IObject2D):
            point = Point2D(point)
        if isinstance(obje, (Empty, Whole)):
            return obje
        if isinstance(obje, ICurve):
            return Transformation.move_curve(obje, point)
        if isinstance(obje, IShape):
            return Transformation.move_shape(obje, point)
        raise NotImplementedError("Not expected to get here")

    @staticmethod
    def scale(obje: IObject2D, xscale: Scalar, yscale: Scalar) -> IObject2D:
        if not isinstance(obje, IObject2D):
            raise TypeError
        if isinstance(obje, (Empty, Whole)):
            return obje
        if isinstance(obje, Point2D):
            return Transformation.scale_point(obje, xscale, yscale)
        if isinstance(obje, ICurve):
            return Transformation.scale_curve(obje, xscale, yscale)
        if isinstance(obje, IShape):
            return Transformation.scale_shape(obje, xscale, yscale)
        raise NotImplementedError("Not expected to get here")

    @staticmethod
    def rotate(obje: IObject2D, angle: Scalar) -> IObject2D:
        if not isinstance(obje, IObject2D):
            raise TypeError
        if isinstance(obje, (Empty, Whole)):
            return obje
        if isinstance(obje, Point2D):
            return Transformation.rotate_point(obje, angle)
        if isinstance(obje, ICurve):
            return Transformation.rotate_curve(obje, angle)
        if isinstance(obje, IShape):
            return Transformation.rotate_shape(obje, angle)
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
        raise NotImplementedError(
            f"Not expected: {type(shape)}, {type(point)}"
        )

    @staticmethod
    def curve_in_simple(obje: SimpleShape, other: ICurve) -> bool:
        if not isinstance(obje, SimpleShape):
            raise TypeError
        if not isinstance(other, ICurve):
            raise TypeError
        if not all(vertex in obje for vertex in other.vertices):
            return False
        nnodes = 64
        unodes = tuple(i / nnodes for i in range(1, nnodes))
        param_curve = other.param_curve
        for ka, kb in zip(param_curve.knots, param_curve.knots[1:]):
            for unode in unodes:
                tnode = (1 - unode) * ka + unode * kb
                if param_curve.eval(tnode, 0) not in obje:
                    return False
        return True

    @staticmethod
    def simple_in_simple(obje: SimpleShape, other: SimpleShape) -> bool:
        if not isinstance(obje, SimpleShape):
            raise TypeError
        if not isinstance(other, SimpleShape):
            raise TypeError
        spos = obje.area > 0
        opos = other.area > 0
        if spos ^ opos:
            if spos and not opos:
                return False
        elif obje.area < other.area:
            return False
        elif spos and opos:
            return other.jordan in obje
        elif obje == other:
            return True
        if obje.boundary or other.boundary:
            return other.jordan in obje and obje.jordan not in other
        obje = SimpleShape(obje.jordan, True)
        return other.jordan in obje and obje.jordan not in other

    @staticmethod
    def shape_in_shape(obje: IShape, other: IShape) -> bool:
        if not isinstance(obje, IShape):
            raise TypeError
        if not isinstance(other, IShape):
            raise TypeError
        if isinstance(obje, SimpleShape):
            if isinstance(other, SimpleShape):
                return Contains.simple_in_simple(obje, other)
            invobj = -obje
            if isinstance(other, ConnectedShape):
                return any(invobj in -sub for sub in other)
        raise NotImplementedError(f"Not expected: {type(obje)}, {type(other)}")


class BooleanOperate:
    @staticmethod
    def contains(obje: IBoolean2D, other: IBoolean2D) -> bool:
        if isinstance(other, (Empty, Whole)):
            raise NotImplementedError("Not expected get here")
        if isinstance(obje, (Empty, Whole)):
            raise NotImplementedError("Not expected get here")
        if isinstance(obje, (BoolAnd, ConnectedShape)):
            raise NotImplementedError("Not expected get here")
        if not isinstance(other, IBoolean2D):
            other = Point2D(other)
        if other.ndim > obje.ndim:
            return False
        if isinstance(other, (DisjointShape, BoolOr)):
            return all(sub in obje for sub in other)
        if isinstance(obje, IShape):
            if isinstance(other, IShape):
                return Contains.shape_in_shape(obje, other)
            if isinstance(other, ICurve) and isinstance(obje, SimpleShape):
                return Contains.curve_in_simple(obje, other)
            if isinstance(other, Point2D):
                return Contains.point_in_shape(obje, other)
        if isinstance(obje, ICurve):
            if isinstance(other, Point2D):
                return Contains.point_in_curve(obje, other)
        if isinstance(obje, Point2D) and isinstance(other, Point2D):
            return obje == other
        if isinstance(obje, BoolNot) and isinstance(obje.obje, Point2D):
            return obje.obje not in other
        raise NotImplementedError(f"Not expected: {type(obje)}, {type(other)}")

    @staticmethod
    def invert(obje: IBoolean2D) -> IBoolean2D:
        if isinstance(obje, (Empty, Whole, BoolNot)):
            raise NotImplementedError("Not expected get here")
        retorno = BoolNot(obje)
        if Configuration.AUTOEXPAND:
            retorno = Simplify.expand(retorno)
        if Configuration.AUTOSIMPLIFY:
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
                raise TypeError
        ndims = (obj.ndim for obj in objects)
        objects = tuple(objects[i] for i in sorter(ndims))
        retorno = BoolOr(objects)
        if Configuration.AUTOEXPAND:
            retorno = Simplify.expand(retorno)
        if Configuration.AUTOSIMPLIFY:
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
                raise TypeError
        ndims = (obj.ndim for obj in objects)
        objects = tuple(objects[i] for i in sorter(ndims))
        retorno = BoolAnd(objects)
        if Configuration.AUTOEXPAND:
            retorno = Simplify.expand(retorno)
        if Configuration.AUTOSIMPLIFY:
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
            BoolOr(obje, ~obje) -> Whole
            Intersection(obje, ~obje) -> Empty
        """
        objects = tuple(objects)
        inveobjs = tuple(obj for obj in objects if type(obj) is BoolNot)
        normobjs = tuple(
            obj for obj in objects if not isinstance(obj, BoolNot)
        )
        for inveobj in inveobjs:
            for normobj in normobjs:
                if inveobj.obje == normobj:
                    return True
        return False

    @staticmethod
    def flatten(obje: IObject2D) -> IObject2D:
        """
        Flat the obje, doing:

        or[or[A, B], C] = or[A, B, C]
        and[and[A, B], C] = and[A, B, C]
        """
        if type(obje) not in (BoolOr, BoolAnd):
            return obje
        subobjs = tuple(obje)
        items = []
        for subobj in subobjs:
            subobj = Simplify.flatten(subobj)
            if isinstance(subobj, obje.__class__):
                items += list(subobj)
            else:
                items.append(subobj)
        return obje.__class__(items)

    @staticmethod
    def expand_not(obje: BoolNot) -> IObject2D:
        if type(obje) is not BoolNot:
            raise TypeError
        invobj = obje.obje
        if type(invobj) is BoolOr:
            newobjs = map(BooleanOperate.invert, invobj)
            obje = BooleanOperate.intersect(*newobjs)
        elif type(invobj) is BoolAnd:
            newobjs = map(BooleanOperate.invert, invobj)
            obje = BooleanOperate.union(*newobjs)
        return obje

    @staticmethod
    def expand_and(obje: BoolAnd) -> IObject2D:
        if type(obje) is not BoolAnd:
            raise TypeError
        subobjs = tuple(Simplify.flatten(obje))
        sizes = [1] * len(subobjs)
        for i, subobj in enumerate(subobjs):
            if type(subobj) is BoolOr:
                sizes[i] = len(subobj)
        if all(size == 1 for size in sizes):
            return obje
        subinters = []
        for indexs in permutations(*sizes):
            subitems = [subobjs[i] for i in indexs]
            subinters.append(BoolAnd(subitems))
        return Simplify.expand_or(BoolOr(subinters))

    @staticmethod
    def expand_or(obje: BoolOr) -> IObject2D:
        if type(obje) is not BoolOr:
            raise TypeError
        return Simplify.flatten(obje)

    @staticmethod
    def expand(obje: IObject2D) -> IObject2D:
        """
        Expand the obje by using Morgan's law, to get something like

        Union[Intersection[Inversion[OBJECT]]]

        * not[A or B] -> (not A) and (not B)
        * not[A and B] -> (not A) or (not B)
        * and[A or B, C] -> (A and C) or (B and C)
        * or[A and B, C] -> or[A and B, C]

        """
        if not isinstance(obje, IObject2D):
            raise TypeError
        if type(obje) is BoolNot:
            return Simplify.expand_not(obje)
        elif type(obje) is BoolAnd:
            return Simplify.expand_and(obje)
        elif type(obje) is BoolOr:
            return Simplify.expand_or(obje)
        return obje

    @staticmethod
    def treat_contains_or(obje: IBoolean2D) -> IBoolean2D:
        if type(obje) is not BoolOr:
            return obje
        subobjs = tuple(obje)[::-1]
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
    def treat_contains_and(obje: IBoolean2D) -> IBoolean2D:
        if type(obje) is not BoolAnd:
            return obje
        subobjs = tuple(obje)
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
    def treat_points(obje: IBoolean2D) -> IBoolean2D:
        if type(obje) is not BoolAnd:
            return obje
        points = tuple(sub for sub in obje if isinstance(sub, Point2D))
        for point in points:
            for sub in obje:
                if point not in sub:
                    return Empty()
        if len(points) > 0:
            return points[0]
        return obje

    @staticmethod
    def simplify_not(obje: BoolNot) -> IObject2D:
        if not isinstance(obje, BoolNot):
            raise TypeError
        invobj = obje.obje
        if isinstance(invobj, (Point2D, ICurve)):
            return obje
        if isinstance(invobj, (SimpleShape, ConnectedShape)):
            return -invobj
        if isinstance(invobj, DisjointShape):
            simples = (~sub for sub in flatten2simples(invobj))
            return identify_shape(simples)
        raise NotImplementedError(f"Not expected get here: {obje}")

    @staticmethod
    def simplify_and(obje: BoolAnd) -> IObject2D:
        if type(obje) is not BoolAnd:
            raise TypeError
        return obje

    @staticmethod
    def simplify_or(obje: BoolOr) -> IObject2D:
        if type(obje) is not BoolOr:
            raise TypeError
        return obje

    @staticmethod
    def simplify(obje: IObject2D) -> IObject2D:
        if not isinstance(obje, IObject2D):
            raise TypeError
        obje = Simplify.expand(obje)
        if isinstance(obje, (Point2D, ICurve, IShape, Empty, Whole)):
            return obje
        if type(obje) not in (BoolNot, BoolOr, BoolAnd):
            return obje
        if isinstance(obje, BoolNot):
            return Simplify.simplify_not(obje)
        subobjs = tuple(map(Simplify.simplify, obje))
        subobjs = Simplify.filter_equal(subobjs)
        if len(subobjs) == 1:
            return Simplify.simplify(subobjs[0])
        if Simplify.has_inverse(subobjs):
            if type(obje) is BoolOr:
                return Whole()
            if type(obje) is BoolAnd:
                return Empty()
            raise NotImplementedError("Not expected get here")
        obje = obje.__class__(subobjs)
        if type(obje) is BoolOr:
            obje = Simplify.treat_contains_or(obje)
        elif type(obje) is BoolAnd:
            obje = Simplify.treat_contains_and(obje)
            obje = Simplify.treat_points(obje)
        if type(obje) not in (BoolOr, BoolAnd):
            return obje
        shapes = tuple(sub for sub in obje if isinstance(sub, IShape))
        if len(shapes) > 1:
            others = [sub for sub in obje if not isinstance(sub, IShape)]
            if type(obje) is BoolOr:
                shape = unite_shapes(*shapes)
            elif type(obje) is BoolAnd:
                shape = intersect_shapes(*shapes)
            others.append(shape)
            if type(obje) is BoolAnd:
                obje = BooleanOperate.intersect(*others)
            elif type(obje) is BoolOr:
                obje = BooleanOperate.union(*others)
            return Simplify.simplify(obje)
        return obje
