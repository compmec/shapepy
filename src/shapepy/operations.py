"""
This file contains the operations that are more complex
than it's already implemented.
For example, it's simple computing the intersection of a point and another obj
then we let it be Point's responsability.
Otherwise, we use the functions of this file

It also contains the function simplify, which expands
and simplifies the boolean operations.
"""

from typing import Any, Iterable, List, Tuple

from .boolean import BoolAnd, BoolNot, BoolOr
from .core import Configuration, Empty, IBoolean2D, IObject2D, IShape, Whole
from .curve.abc import ICurve
from .point import Point2D
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


class Contains:
    """
    Class to store static functions that checks if one
    object is inside another object
    """

    @staticmethod
    def point_in_curve(curve: ICurve, point: Point2D) -> bool:
        """
        Checks if the point is inside the curve
        """
        if not isinstance(point, Point2D):
            raise TypeError
        if not isinstance(curve, ICurve):
            raise TypeError
        return 0 < curve.winding(point) < 1

    @staticmethod
    def object_in_object(obje: IBoolean2D, other: IBoolean2D) -> bool:
        """
        Checks if one object is inside another object
        """
        if not isinstance(other, IBoolean2D):
            other = Point2D(other)
            return other in obje
        if isinstance(obje, ICurve):
            if isinstance(other, Point2D):
                return Contains.point_in_curve(obje, other)
        if isinstance(obje, BoolNot) and isinstance(obje.obje, Point2D):
            return obje.obje not in other
        raise NotImplementedError(f"Not expected: {type(obje)}, {type(other)}")


class BooleanOperate:
    """
    Class to store functions responsible to make the boolean operations
    """

    @staticmethod
    def contains(obje: IBoolean2D, other: IBoolean2D) -> bool:
        """
        Checks if one object is inside another object
        """
        return Contains.object_in_object(obje, other)

    @staticmethod
    def invert(obje: IBoolean2D) -> IBoolean2D:
        """
        Computes the inversion of the object
        """
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
        """
        Computes the union of the objects
        """
        objects = (obj for obj in objects if not isinstance(obj, Empty))
        objects = [
            obj if isinstance(obj, IBoolean2D) else Point2D(obj)
            for obj in objects
        ]
        if any(isinstance(obj, Whole) for obj in objects):
            return Whole()
        if len(objects) == 1:
            return objects[0]
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
        """
        Computes the intersection of the objects
        """
        objects = (obj for obj in objects if not isinstance(obj, Whole))
        objects = [
            obj if isinstance(obj, IBoolean2D) else Point2D(obj)
            for obj in objects
        ]
        if any(isinstance(obj, Empty) for obj in objects):
            return Empty()
        if len(objects) == 1:
            return objects[0]
        ndims = (obj.ndim for obj in objects)
        objects = tuple(objects[i] for i in sorter(ndims))
        retorno = BoolAnd(objects)
        if Configuration.AUTOEXPAND:
            retorno = Simplify.expand(retorno)
        if Configuration.AUTOSIMPLIFY:
            retorno = Simplify.simplify(retorno)
        return retorno


class Simplify:
    """
    Class responsible to simplify the object, like computing the intersection
    or the union of the shapes, remove the repeted elements, etc
    """

    @staticmethod
    def filter_equal(objects: Iterable[IObject2D]) -> Iterable[IObject2D]:
        """
        This function remove the equal elements (by id)
        """
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
    def has_inverse(objects: Iterable[IObject2D]) -> bool:
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
        """
        This function expands the BoolNot object using Morgan's law
        """
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
        """
        This function expands the BoolAnd object using Morgan's law
        """
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
        """
        This function expands the BoolOr object using Morgan's law
        """
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
        if type(obje) is BoolAnd:
            return Simplify.expand_and(obje)
        if type(obje) is BoolOr:
            return Simplify.expand_or(obje)
        return obje

    @staticmethod
    def treat_contains_or(obje: IBoolean2D) -> IBoolean2D:
        """
        This function checks if one subobject is inside another subobject
        If that's the case, remove the internal object, since the bigger
        object contains the smaller one, remaining only the biggest one
        """
        if type(obje) is not BoolOr:
            raise TypeError
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
        """
        This function checks if one subobject is inside another subobject
        If that's the case, remove the external object, since the bigger
        object contains the smaller one, remaining only the small one
        """
        if type(obje) is not BoolAnd:
            raise TypeError
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
    def simplify_not(obje: BoolNot) -> IObject2D:
        """
        Simplify the BoolNot object
        """
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

    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches
    @staticmethod
    def simplify(obje: IObject2D) -> IObject2D:
        """
        Simplify the object arbitrary object
        """
        if not isinstance(obje, IObject2D):
            raise TypeError
        obje = Simplify.expand(obje)
        if isinstance(obje, (Point2D, ICurve, IShape, Empty, Whole)):
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
