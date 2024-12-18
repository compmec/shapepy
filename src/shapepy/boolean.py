"""
This file defines basic boolean classes:
* Inverse
* Union
* Inverse

These are result of boolean operation between other things
"""

from typing import Iterable

from .core import Empty, IBoolean2D, IObject2D, Whole


class BoolNot(IBoolean2D):
    """
    Inverse container of an object
    """

    @property
    def ndim(self) -> int:
        return 2

    def __init__(self, obje: IObject2D):
        if not isinstance(obje, IObject2D):
            raise TypeError
        if isinstance(obje, (Empty, Whole)):
            raise TypeError
        self.obje = obje

    def __eq__(self, other: IObject2D) -> bool:
        if not isinstance(other, IObject2D):
            raise TypeError
        if type(self) is not type(other):
            return False
        return self.obje == other.obje

    def __str__(self) -> str:
        return f"NOT[{str(self.obje)}]"

    def __repr__(self) -> str:
        return f"NOT[{repr(self.obje)}]"

    def __invert__(self) -> IObject2D:
        return self.obje


class BoolOr(IBoolean2D):
    """
    Union container of some objects
    """

    @property
    def ndim(self) -> int:
        return max(sub.ndim for sub in self)

    def __init__(self, objects: Iterable[IObject2D]):
        objects = tuple(objects)
        for obje in objects:
            if not isinstance(obje, IObject2D):
                raise TypeError
            if isinstance(obje, (Empty, Whole)):
                raise TypeError
        if len(objects) < 2:
            raise ValueError(f"Cannot init a BoolOr with {len(objects)} objs")
        self.__objects = objects

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IObject2D):
            raise TypeError
        if type(self) is not type(other):
            return False
        selfobjs = tuple(self)
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


class BoolAnd(IBoolean2D):
    """
    Intersection container of some objects
    """

    @property
    def ndim(self) -> int:
        return min(sub.ndim for sub in self)

    def __init__(self, objects: Iterable[IObject2D]):
        objects = tuple(objects)
        for obje in objects:
            if not isinstance(obje, IObject2D):
                raise TypeError
            if isinstance(obje, (Empty, Whole)):
                raise TypeError
        if len(objects) < 2:
            raise ValueError(f"Cannot init a BoolOr with {len(objects)} objs")
        self.__objects = objects

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IObject2D):
            raise TypeError
        if type(self) is not type(other):
            return False
        if not isinstance(self, BoolAnd):
            return self == other
        selfobjs = tuple(self)
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

    def __contains__(self, other):
        return all(other in sub for sub in self)
