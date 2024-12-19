"""
This file defines basic boolean classes:
* Inverse
* Union
* Inverse

These are result of boolean operation between other things
"""
from __future__ import annotations

from typing import Iterable, Tuple

from .core import Empty, IBoolean2D, IObject2D, Scalar, Whole


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

    def move(self, vector: Tuple[Scalar, Scalar]) -> BoolOr:
        """
        Moves the object in the plane by the given vector

        Parameters
        ----------
        vector: Point
            The pair (x, y) that must be added to the coordinates
        """
        return self.__class__(self.obje.move(vector))

    def scale(self, xscale: Scalar, yscale: Scalar) -> BoolOr:
        """
        Scales the object in the X and Y directions

        Parameters
        ----------
        xscale: Scalar
            The amount to be scaled in the X direction
        yscale: Scalar
            The amount to be scaled in the Y direction
        """
        return self.__class__(self.obje.scale(xscale, yscale))

    def rotate(self, uangle: Scalar, degrees: bool = False) -> BoolOr:
        """
        Rotates the object around the origin.

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
        return self.__class__(self.obje.rotate(uangle, degrees))


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

    def __len__(self) -> int:
        return len(self.__objects)

    def move(self, vector: Tuple[Scalar, Scalar]) -> BoolOr:
        """
        Moves the object in the plane by the given vector

        Parameters
        ----------
        vector: Point
            The pair (x, y) that must be added to the coordinates
        """
        return self.__class__(sub.move(vector) for sub in self)

    def scale(self, xscale: Scalar, yscale: Scalar) -> BoolOr:
        """
        Scales the object in the X and Y directions

        Parameters
        ----------
        xscale: Scalar
            The amount to be scaled in the X direction
        yscale: Scalar
            The amount to be scaled in the Y direction
        """
        return self.__class__(sub.scale(xscale, yscale) for sub in self)

    def rotate(self, uangle: Scalar, degrees: bool = False) -> BoolOr:
        """
        Rotates the object around the origin.

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
        return self.__class__(sub.rotate(uangle, degrees) for sub in self)


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

    def __len__(self) -> int:
        return len(self.__objects)

    def __contains__(self, other):
        return all(other in sub for sub in self)

    def move(self, vector: Tuple[Scalar, Scalar]) -> BoolAnd:
        """
        Moves the object in the plane by the given vector

        Parameters
        ----------
        vector: Point
            The pair (x, y) that must be added to the coordinates
        """
        return self.__class__(sub.move(vector) for sub in self)

    def scale(self, xscale: Scalar, yscale: Scalar) -> BoolOr:
        """
        Scales the object in the X and Y directions

        Parameters
        ----------
        xscale: Scalar
            The amount to be scaled in the X direction
        yscale: Scalar
            The amount to be scaled in the Y direction
        """
        return self.__class__(sub.scale(xscale, yscale) for sub in self)

    def rotate(self, uangle: Scalar, degrees: bool = False) -> BoolOr:
        """
        Rotates the object around the origin.

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
        return self.__class__(sub.rotate(uangle, degrees) for sub in self)
