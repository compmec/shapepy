from __future__ import annotations

from ..abc import IClosedCurve, IJordanCurve
from .curve import PolygonClosedCurve


class JordanPolygon(PolygonClosedCurve, IJordanCurve):
    @property
    def param_curve(self) -> PolygonClosedCurve:
        return self

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (IClosedCurve, IJordanCurve)):
            return False
        if self.area != other.area:
            return False
        if abs(self.lenght - other.lenght) > 1e-9:
            return False
        if len(self.vertices) != len(other.vertices):
            return False
        index = 0
        for j, vertj in enumerate(other.vertices):
            if vertj == self.vertices[0]:
                index = j
                break
        nverts = len(self.vertices)
        for i, verti in enumerate(self.vertices):
            vertj = other.vertices[(index + i) % nverts]
            if verti != vertj:
                return False
        return True

    def __str__(self) -> str:
        return f"JordanPolygon({self.area}, {self.lenght})"

    def __repr__(self) -> str:
        return self.__str__()

    def __invert__(self) -> JordanPolygon:
        newvertices = tuple(self.vertices[::-1])
        return self.__class__(newvertices)
