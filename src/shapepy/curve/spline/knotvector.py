"""
File that defines the KnotVector class

It's used to compute the Spline basis functions
"""
from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Optional

from ...core import Parameter


class KnotVector(tuple):
    """
    Defines the knotvector, to store knots, degree of the curve, etc
    """

    def __new__(
        cls, knotvector: Iterable[Parameter], degree: Optional[int] = None
    ):
        if isinstance(knotvector, cls):
            return knotvector
        return super(KnotVector, cls).__new__(cls, tuple(knotvector))

    def __init__(
        self, knotvector: Iterable[Parameter], degree: Optional[int] = None
    ):
        knotvector = list(knotvector)
        if degree is None:
            degree = max(
                sum(val == knot for val in knotvector) - 1
                for knot in sorted(set(knotvector))
            )
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
        """
        Gives the polynomial degree of the related spline
        """
        return self.__degree

    @property
    def npts(self) -> int:
        """
        Gives the quantity of control points used to define the spline
        """
        return self.__npts

    @property
    def knots(self) -> Iterable[Parameter]:
        """
        Gives the knots of subdivision of the interval

        Parameters
        ----------
        return: Iterable[Parameter]
            The knots values

        Examples
        --------
        >>> knotvector = KnotVector([0, 0, 1, 2, 2], 1)
        >>> knotvector.knots
        (0, 1, 2)
        >>> knotvector = KnotVector([0, 0, 0, 1, 1, 2, 2, 2], 2)
        >>> knotvector.knots
        (0, 1, 2)
        """
        return self.__knots

    @property
    def spans(self) -> Iterable[Parameter]:
        """
        Gives the last index of the knotvector, such is equal to the knots

        Parameters
        ----------
        return: Iterable[Parameter]
            The spans values

        Examples
        --------
        >>> knotvector = KnotVector([0, 0, 0, 1, 1, 2, 2, 2], 2)
        >>> knotvector.knots
        (0, 1, 2)
        >>> knotvector.spans
        (2, 4)
        """
        return self.__spans
