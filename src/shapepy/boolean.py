"""
This file defines basic boolean classes:
* Inverse
* Union
* Inverse

These are result of boolean operation between other things
"""

from typing import Any, Iterable, List, Tuple

from .core import Empty, IBoolean2D, IObject2D, Whole


def permutations(*numbers: int) -> Iterable[Tuple[int, ...]]:
    """
    Permutes the numbers

    Example:
    permutations(4) -> [0, 1, 2, 3]
    permutations(4, 2) -> [(0, 0), (0, 1), (1, 0), ..., (3, 0), (3, 0)]
    permutations(2, 4, 1) -> [(0, 0, 0), ..., (1, 3, 1), (1, 3, 2)]
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


class BoolNot(IBoolean2D):
    """
    Inverse container of an object
    """

    @property
    def ndim(self) -> int:
        return 4

    def __init__(self, object: IObject2D):
        if not isinstance(object, IObject2D):
            raise TypeError
        if isinstance(object, (Empty, Whole)):
            raise TypeError
        self.object = object

    def __eq__(self, other: IObject2D) -> bool:
        if not isinstance(other, IObject2D):
            raise TypeError
        selff = expand(self)
        other = expand(other)
        if type(selff) is not type(other):
            return False
        if not isinstance(selff, BoolNot):
            return selff == other
        return selff.object == other.object

    def __str__(self) -> str:
        return f"NOT[{str(self.object)}]"

    def __repr__(self) -> str:
        return f"NOT[{repr(self.object)}]"

    def __invert__(self) -> IObject2D:
        return self.object

    def __ror__(self, other: IObject2D) -> IObject2D:
        return union(self, other)

    def __rand__(self, other: IObject2D) -> IObject2D:
        return intersection(self, other)


class BoolOr(IBoolean2D):
    """
    Union container of some objects
    """

    @property
    def ndim(self) -> int:
        return 4

    def __init__(self, objects: Iterable[IObject2D]):
        objects = tuple(objects)
        for object in objects:
            if not isinstance(object, IObject2D):
                raise TypeError
            if isinstance(object, (Empty, Whole)):
                raise TypeError
        self.__objects = objects

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IObject2D):
            raise TypeError
        selff = expand(self)
        other = expand(other)
        if type(selff) is not type(other):
            return False
        if not isinstance(selff, BoolOr):
            return selff == other
        selfobjs = tuple(selff)
        otheobjs = list(other)
        for obji in selfobjs:
            for j, objj in enumerate(otheobjs):
                if obji == objj:
                    otheobjs.pop(j)
                    break
            else:
                return False
        return True

    def __str__(self) -> str:
        return f"OR[{', '.join(map(str, self))}]"

    def __repr__(self) -> str:
        return f"OR[{', '.join(map(repr, self))}]"

    def __iter__(self):
        yield from self.__objects

    def __getitem__(self, index):
        return self.__objects[index]

    def __len__(self) -> int:
        return len(self.__objects)

    def __invert__(self) -> Any:
        return invert(self)

    def __ror__(self, other: Any) -> Any:
        return union(self, other)

    def __rand__(self, other: Any) -> Any:
        return intersection(self, other)


class BoolAnd(IBoolean2D):
    """
    Intersection container of some objects
    """

    @property
    def ndim(self) -> int:
        return 4

    def __init__(self, objects: Iterable[IObject2D]):
        objects = tuple(objects)
        for object in objects:
            if not isinstance(object, IObject2D):
                raise TypeError
            if isinstance(object, (Empty, Whole)):
                raise TypeError
        self.__objects = objects

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IObject2D):
            raise TypeError
        selff = expand(self)
        other = expand(other)
        if type(selff) is not type(other):
            return False
        if not isinstance(self, BoolAnd):
            return selff == other
        selfobjs = tuple(selff)
        otheobjs = list(other)
        for obji in selfobjs:
            for j, objj in enumerate(otheobjs):
                if obji == objj:
                    otheobjs.pop(j)
                    break
            else:
                return False
        return True

    def __str__(self) -> str:
        return f"AND[{', '.join(map(str, self))}]"

    def __repr__(self) -> str:
        return f"AND[{', '.join(map(repr, self))}]"

    def __iter__(self):
        yield from self.__objects

    def __getitem__(self, index):
        return self.__objects[index]

    def __len__(self) -> int:
        return len(self.__objects)

    def __invert__(self) -> IObject2D:
        return invert(self)

    def __ror__(self, other: IObject2D) -> IObject2D:
        return union(self, other)

    def __rand__(self, other: IObject2D) -> IObject2D:
        return intersection(self, other)


def invert(object: IObject2D) -> IObject2D:
    """
    Inverts an object
    """
    if isinstance(object, (Empty, Whole)):
        raise NotImplementedError
    if isinstance(object, BoolNot):
        return object.object
    return BoolNot(object)


def union(*objects: IObject2D) -> IObject2D:
    """
    Unites some objects
    """
    for object in objects:
        if not isinstance(object, IObject2D):
            raise TypeError
    if any(isinstance(obj, Whole) for obj in objects):
        return Whole()
    objects = tuple(obj for obj in objects if not isinstance(obj, Empty))
    objects = filter_equal(objects)
    if len(objects) == 1:
        return objects[0]
    return flatten(BoolOr(objects))


def intersection(*objects: IObject2D) -> IObject2D:
    """
    Intersect some objects
    """
    for object in objects:
        if not isinstance(object, IObject2D):
            raise TypeError
    if any(isinstance(obj, Empty) for obj in objects):
        return Empty()
    objects = tuple(obj for obj in objects if not isinstance(obj, Whole))
    objects = filter_equal(objects)
    if len(objects) == 1:
        return objects[0]
    return flatten(BoolAnd(objects))


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
        subobj = flatten(subobj)
        if isinstance(subobj, object.__class__):
            items += list(subobj)
        else:
            items.append(subobj)
    return object.__class__(items)


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
    if not isinstance(object, (BoolNot, BoolOr, BoolAnd)):
        return object
    if isinstance(object, BoolNot):
        if not isinstance(object.object, (BoolOr, BoolAnd)):
            return object
        invobj = flatten(object.object)
        if isinstance(object.object, BoolOr):
            object = intersection(*map(invert, invobj))
        elif isinstance(object.object, BoolAnd):
            object = union(*map(invert, invobj))
        return expand(object)
    object = flatten(object)
    if not isinstance(object, (BoolOr, BoolAnd)):
        raise NotImplementedError("Not expected get here")
    if len(object) == 1:
        return expand(object[0])
    if isinstance(object, BoolOr):
        return object
    subobjs = tuple(object)
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
    return expand(BoolOr(subinters))


def simplify(object: IObject2D) -> IObject2D:
    if not isinstance(object, IObject2D):
        raise TypeError
    if not isinstance(object, (BoolNot, BoolOr, BoolAnd)):
        return object
    object = expand(object)
    if not isinstance(object, (BoolOr, BoolAnd)):
        return object
    subobjs = tuple(map(simplify, object))
    subobjs = filter_equal(subobjs)
    if len(subobjs) == 1:
        return simplify(subobjs[0])
    if has_inverse(subobjs):
        if isinstance(object, BoolOr):
            return Whole()
        if isinstance(object, BoolAnd):
            return Empty()
        raise NotImplementedError("Not expected get here")
    return object.__class__(subobjs)


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
    normobjs = tuple(obj for obj in objects if not isinstance(obj, BoolNot))
    for inveobj in inveobjs:
        for normobj in normobjs:
            if inveobj.object == normobj:
                return True
    return False
