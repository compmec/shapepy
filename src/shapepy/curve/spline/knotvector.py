from __future__ import annotations

from fractions import Fraction
from typing import Optional, Tuple

from ...core import Parameter


class KnotVector(tuple):

    def __new__(
        cls, knotvector: Tuple[Parameter, ...], degree: Optional[int] = None
    ):
        if isinstance(knotvector, cls):
            return knotvector
        return super(KnotVector, cls).__new__(cls, tuple(knotvector))

    def __init__(
        self, knotvector: Tuple[Parameter, ...], degree: Optional[int] = None
    ):
        if degree is None:
            degree = max(
                sum(val == knot for val in knotvector) - 1
                for knot in sorted(set(knotvector))
            )
        knotvector = list(knotvector)
        for i, value in enumerate(knotvector):
            if isinstance(value, int):
                knotvector[i] = Fraction(value)
        npts = len(knotvector) - degree - 1
        if npts <= degree:
            raise ValueError
        slic = slice(degree, npts + 1)
        knots = tuple(sorted(set(knotvector[slic])))
        spans = tuple(
            max(i for i, v in enumerate(knotvector) if v == k)
            for k in knots[:-1]
        )

        self.__degree = degree
        self.__npts = npts
        self.__knots = knots
        self.__spans = spans

    @property
    def degree(self) -> int:
        return self.__degree

    @property
    def npts(self) -> int:
        return self.__npts

    @property
    def knots(self) -> Tuple[Parameter, ...]:
        return self.__knots

    @property
    def spans(self) -> Tuple[Parameter, ...]:
        return self.__spans
