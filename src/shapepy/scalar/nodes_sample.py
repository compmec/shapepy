"""
Defines the NodeSampleFactory
"""

from functools import cache
from typing import Tuple

from ..tools import Is, To
from .angle import Angle
from .reals import Rational, Real


class NodeSampleFactory:
    """
    Functions to get node samples
    """

    @staticmethod
    @cache
    def closed_linspace(npts: int) -> Tuple[Rational, ...]:
        """
        Gives a set of numbers in interval [0, 1]

        Example
        -------
        >>> closed_linspace(2)
        (0, 1)
        >>> closed_linspace(3)
        (0, 0.5, 1)
        >>> closed_linspace(4)
        (0, 0.33, 0.66, 1)
        >>> closed_linspace(5)
        (0, 0.25, 0.5, 0.75, 1)
        """
        if not Is.integer(npts) or npts < 2:
            raise ValueError("npts must be integer >= 2")
        return tuple(To.rational(num, npts - 1) for num in range(npts))

    @staticmethod
    @cache
    def closed_newton_cotes(npts: int) -> Tuple[Real]:
        """
        Gives a set of numbers in interval [0, 1]

        Example
        -------
        >>> closed_newton_cotes(2)
        (0, 1)
        >>> closed_newton_cotes(3)
        (0, 1/2, 1)
        >>> closed_newton_cotes(4)
        (0, 1/3, 2/3, 1)
        >>> closed_newton_cotes(5)
        (0, 1/4, 2/4, 3/4, 1)
        """
        if not Is.integer(npts) or npts < 2:
            raise ValueError("npts must be integer >= 2")
        return tuple(To.rational(num, npts - 1) for num in range(npts))

    @staticmethod
    @cache
    def open_newton_cotes(npts: int) -> Tuple[Real]:
        """
        Gives a set of numbers in interval (0, 1)

        Example
        -------
        >>> open_newton_cotes(1)
        (1/2, )
        >>> open_newton_cotes(2)
        (1/3, 2/3)
        >>> open_newton_cotes(3)
        (1/4, 2/4, 3/4)
        >>> open_newton_cotes(4)
        (1/5, 2/5, 3/5, 4/5)
        """
        if not Is.integer(npts) or npts < 1:
            raise ValueError("npts must be integer >= 1")
        return tuple(To.rational(num, npts + 1) for num in range(1, npts + 1))

    @staticmethod
    @cache
    def custom_open_formula(npts: int) -> Tuple[Real]:
        """
        Gives a set of numbers in interval (0, 1)

        Example
        -------
        >>> custom_open_formula(1)
        (1/2, )
        >>> custom_open_formula(2)
        (1/4, 3/4)
        >>> custom_open_formula(3)
        (1/6, 3/6, 5/6)
        >>> custom_open_formula(4)
        (1/8, 3/8, 5/8, 7/8)
        """
        if not Is.integer(npts) or npts < 1:
            raise ValueError("npts must be integer >= 1")
        return tuple(
            To.rational(num, 2 * npts) for num in range(1, 2 * npts, 2)
        )

    @staticmethod
    @cache
    def chebyshev(npts: int) -> Tuple[Real]:
        """
        Gives a set of numbers in interval (0, 1)

        Example
        -------
        >>> custom_open_formula(1)
        (0.5, )
        >>> custom_open_formula(2)
        (0.14645, 0.85355)
        >>> custom_open_formula(3)
        (0.06699, 0.5, 0.93301)
        >>> custom_open_formula(4)
        (0.03806, 0.30866, 0.69134, 0.96194)
        >>> custom_open_formula(4)
        (0.02447, 0.20611, 0.5, 0.79389, 0.97553)
        """
        angles = (
            Angle.turns(num / 2)
            for num in NodeSampleFactory.custom_open_formula(npts)[::-1]
        )
        return tuple(To.rational(1, 2) + angle.cos() / 2 for angle in angles)
