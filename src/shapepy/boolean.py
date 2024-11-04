"""
This file defines basic boolean classes:
* Inverse
* Union
* Inverse

These are result of boolean operation between other things
"""

from typing import Any, Iterable, Tuple

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


class Inverse(IBoolean2D):
    """
    Inverse container of an object
    """

    def __init__(self, object: IObject2D):
        if not isinstance(object, IObject2D):
            raise TypeError
        self.object = object

    def __eq__(self, other: IObject2D) -> bool:
        print(f"Inv: comparing {self} with {other}")
        selff = expand(self)
        other = expand(other)
        if type(selff) is not type(other):
            return False
        if not isinstance(selff, Inverse):
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


class Union(IBoolean2D):
    """
    Union container of some objects
    """

    def __init__(self, objects: Iterable[IObject2D]):
        objects = tuple(objects)
        for object in objects:
            if not isinstance(object, IObject2D):
                raise TypeError
        self.__objects = objects

    def __eq__(self, other: IObject2D) -> bool:
        print(f"Uni: comparing {self} with {other}")
        selff = expand(self)
        other = expand(other)
        if type(selff) is not type(other):
            return False
        if not isinstance(selff, Union):
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


class Intersection(IBoolean2D):
    """
    Intersection container of some objects
    """

    def __init__(self, objects: Iterable[IObject2D]):
        objects = tuple(objects)
        for object in objects:
            if not isinstance(object, IObject2D):
                raise TypeError
        self.__objects = objects

    def __eq__(self, other: IObject2D) -> bool:
        print(f"Int: comparing {self} with {other}")
        selff = expand(self)
        print("selff = ")
        print(selff)
        other = expand(other)
        if type(selff) is not type(other):
            return False
        if not isinstance(self, Intersection):
            return selff == other
        selfobjs = tuple(selff)
        print(selfobjs)
        otheobjs = list(other)
        print(otheobjs)
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
    return object.object if isinstance(object, Inverse) else Inverse(object)


def union(*objects: IObject2D) -> IObject2D:
    """
    Unites some objects
    """
    for object in objects:
        if not isinstance(object, IObject2D):
            raise TypeError
    return flatten(Union(objects))


def intersection(*objects: IObject2D) -> IObject2D:
    """
    Intersect some objects
    """
    for object in objects:
        if not isinstance(object, IObject2D):
            raise TypeError
    return flatten(Intersection(objects))


def flatten(object: IObject2D) -> IObject2D:
    """
    Flat the object, doing:

    or[or[A, B], C] = or[A, B, C]
    and[and[A, B], C] = and[A, B, C]
    """
    if not isinstance(object, (Union, Intersection)):
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
    if not isinstance(object, (Inverse, Union, Intersection)):
        return object
    if isinstance(object, Inverse):
        if not isinstance(object.object, (Union, Intersection)):
            return object
        invobj = flatten(object.object)
        if isinstance(object.object, Union):
            object = intersection(*map(invert, invobj))
        elif isinstance(object.object, Intersection):
            object = union(*map(invert, invobj))
        return expand(object)
    object = flatten(object)
    if len(object) == 1:
        return object[0]
    if isinstance(object, Union):
        return object
    subobjs = tuple(object)
    sizes = [1] * len(subobjs)
    for i, subobj in enumerate(subobjs):
        if isinstance(subobj, Union):
            sizes[i] = len(subobj)
    subinters = []
    for indexs in permutations(*sizes):
        subitems = [subobjs[i] for i in indexs]
        subinters.append(Intersection(subitems))
    return expand(Union(subinters))


def simplify(object: IObject2D) -> IObject2D:
    if not isinstance(object, IObject2D):
        raise TypeError
    if not isinstance(object, (Inverse, Union, Intersection)):
        return object
    object = expand(object)
    if isinstance(object, (Union, Intersection)):
        object = object.__class__(map(simplify, object))
    if isinstance(object, Union):
        if any(isinstance(subobj, Whole) for subobj in object):
            return Whole()
        subobjs = tuple(sub for sub in object if not isinstance(sub, Empty))
        if len(subobjs) == 0:
            return Empty()
        return object.__class__(subobjs)
    if isinstance(object, Intersection):
        print(tuple(object))
        if any(isinstance(subobj, Empty) for subobj in object):
            return Empty()
        print(">..")
        subobjs = tuple(sub for sub in object if not isinstance(sub, Whole))
        if len(subobjs) == 0:
            return Whole()
        return object.__class__(subobjs)
    return object
