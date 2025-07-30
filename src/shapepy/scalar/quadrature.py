"""
Defines the functions used to numerical integration
"""

from functools import lru_cache
from typing import Callable, Iterable, Tuple

import numpy as np

from ..tools import Is, To
from .angle import Angle
from .reals import Math, Rational, Real
from .reals import to_rational as frac


def inner(vectora: Iterable[Real], vectorb: Iterable[Real]) -> Real:
    """Returns the inner product of two vectors"""
    if not Is.iterable(vectora) or not Is.iterable(vectorb):
        raise TypeError("Expected two iterables")
    vectora = tuple(vectora)
    vectorb = tuple(vectorb)
    result = vectora[0] * vectorb[0]
    return sum((a * b for a, b in zip(vectora[1:], vectorb[1:])), start=result)


@lru_cache(maxsize=None)
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


def find_polynomial_weights(nodes: Iterable[Real]) -> Iterable[Real]:
    """
    Finds the weights to integrate a polynomial curve in the interval [0, 1]
    """
    nodes = tuple(map(To.finite, nodes))
    degree = len(nodes) - 1
    matrix = [[0] * len(nodes) for _ in nodes]
    for k, uk in enumerate(nodes):
        for i in range(degree + 1):
            matrix[i][k] = (
                Math.binom(degree, i) * (uk**i) * (1 - uk) ** (degree - i)
            )
    return (sum(line) / len(nodes) for line in invert_matrix(matrix))


def invert_matrix(matrix):
    """
    Uses gaussian elimination to compute the inverse of the matrix
    """

    side = len(matrix)
    inverse = np.eye(side, dtype="object")
    matrix = np.column_stack((matrix, inverse))

    # Eliminate lower triangle
    for k in range(side):
        # Swap pivos
        if matrix[k, k] == 0:
            for i in range(k + 1, side):
                if matrix[i, k] != 0:
                    matrix[[k, i]] = matrix[[i, k]]
                    break
        # Eliminate lines bellow the pivo
        if matrix[k, k] < 0:
            matrix[k] *= -1
        for i in range(k + 1, side):
            matrix[i] = matrix[i] * matrix[k, k] - matrix[k] * matrix[i, k]

    # Eliminate upper triangle
    for k in range(side - 1, 0, -1):
        for i in range(k - 1, -1, -1):
            matrix[i] = matrix[i] * matrix[k, k] - matrix[k] * matrix[i, k]

    diagonal = list(np.diag(matrix[:, :side]))
    inverse = tuple(
        tuple(line / diag) for line, diag in zip(matrix[:, side:], diagonal)
    )
    return inverse


class DirectIntegrator:
    """
    Defines an integrator, to integrate a scalar function in a given interval
    """

    def __init__(self, nodes: Iterable[Real], weights: Iterable[Real]):
        self.__nodes = tuple(map(To.finite, nodes))
        self.__weights = tuple(map(To.finite, weights))
        if len(self.nodes) != len(self.weights):
            raise ValueError(
                f"Invalid {len(self.nodes)} != {len(self.weights)}"
            )

    @property
    def nodes(self) -> Tuple[Real, ...]:
        """Get the nodes used by the integrator"""
        return self.__nodes

    @property
    def weights(self) -> Tuple[Real, ...]:
        """Get the weights used by the integrator"""
        return self.__weights

    def __str__(self) -> str:
        return str({"nodes": self.nodes, "weights": self.weights})

    def __repr__(self) -> str:
        return str(self)

    def integrate(
        self, function: Callable[[Real], Real], interval: Tuple[Real, Real]
    ) -> Real:
        """Computes the integral of func in [a, b]"""
        if not Is.callable(function):
            raise ValueError
        if not (
            Is.real(interval[0])
            and Is.real(interval[1])
            and interval[0] < interval[1]
        ):
            raise ValueError
        diff = interval[1] - interval[0]
        points = tuple(interval[0] + diff * node for node in self.nodes)
        fvalues = tuple(map(function, points))
        inn = inner(self.weights, fvalues)
        return To.real(diff * inn)


class NodeSampleFactory:
    """
    Functions to get node samples
    """

    @lru_cache(maxsize=None)
    @staticmethod
    def open_newton_cotes(npts: int) -> Iterable[Real]:
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

    @lru_cache(maxsize=None)
    @staticmethod
    def custom_open_formula(npts: int) -> Iterable[Real]:
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

    @lru_cache(maxsize=None)
    @staticmethod
    def chebyshev(npts: int) -> Iterable[Real]:
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
            Angle.turns(num / 4)
            for num in NodeSampleFactory.custom_open_formula(npts)
        )
        return tuple(angle.sin() ** 2 for angle in angles)


class IntegratorFactory:
    """
    Defines methods that creates Direct Integrators
    """

    open_newton_cotes_weights = {
        1: (frac(1),),
        2: (frac(1, 2), frac(1, 2)),
        3: (frac(2, 3), frac(-1, 3), frac(2, 3)),
        4: (frac(11, 24), frac(1, 24), frac(1, 24), frac(11, 24)),
        5: (
            frac(11, 20),
            frac(-14, 20),
            frac(26, 20),
            frac(-14, 20),
            frac(11, 20),
        ),
    }

    custom_open_formula_weights = {
        1: (frac(1),),
        2: (frac(1, 2), frac(1, 2)),
        3: (frac(3, 8), frac(1, 4), frac(3, 8)),
        4: (
            frac(13, 48),
            frac(11, 48),
            frac(11, 48),
            frac(13, 48),
        ),
        5: (
            frac(275, 1152),
            frac(100, 1152),
            frac(402, 1152),
            frac(100, 1152),
            frac(275, 1152),
        ),
    }

    clenshaw_curtis_weights = {
        1: (frac(1),),
        2: (frac(1, 2), frac(1, 2)),
        3: (frac(2, 9), frac(5, 9), frac(2, 9)),
        4: (
            (3 - Math.sqrt(2)) / 12,
            (3 + Math.sqrt(2)) / 12,
            (3 + Math.sqrt(2)) / 12,
            (3 - Math.sqrt(2)) / 12,
        ),
        5: (
            (13 - 3 * Math.sqrt(5)) / 75,
            (13 + 3 * Math.sqrt(5)) / 75,
            frac(23, 75),
            (13 + 3 * Math.sqrt(5)) / 75,
            (13 - 3 * Math.sqrt(5)) / 75,
        ),
        6: (
            (14 - 5 * Math.sqrt(3)) / 90,
            frac(17, 90),
            (14 + 5 * Math.sqrt(3)) / 90,
            (14 + 5 * Math.sqrt(3)) / 90,
            frac(17, 90),
            (14 - 5 * Math.sqrt(3)) / 90,
        ),
    }

    @staticmethod
    def open_newton_cotes(
        npts: int, convert: type = To.rational
    ) -> DirectIntegrator:
        """
        Gives a set of numbers in interval (0, 1)

        Example
        -------
        >>> open_newton_cotes(1)
        {"nodes": (1/2, ),
         "weights": (1, )}
        >>> open_newton_cotes(2)
        {"nodes": (1/3, 2/3),
         "weights": (1/2, 1/2)}
        >>> open_newton_cotes(3)
        {"nodes": (1/4, 2/4, 3/4),
         "weights": (2/3, -1/3, 2/3)}
        >>> open_newton_cotes(4)
        {"nodes": (1/5, 2/5, 3/5, 4/5),
         "weights": (11/24, 1/24, 1/24, 11/24)}
        >>> open_newton_cotes(5)
        {"nodes": (1/6, 2/6, 3/6, 4/6, 5/6),
         "weights": (11/20, -14/20, 26/20, -14/20, 11/20)}
        """
        nodes = tuple(NodeSampleFactory.open_newton_cotes(npts))
        if npts in IntegratorFactory.open_newton_cotes_weights:
            weights = IntegratorFactory.open_newton_cotes_weights[npts]
        else:
            weights = tuple(find_polynomial_weights(nodes))
            IntegratorFactory.open_newton_cotes_weights[npts] = weights
        return DirectIntegrator(map(convert, nodes), map(convert, weights))

    @lru_cache(maxsize=None)
    @staticmethod
    def custom_open_formula(
        npts: int, convert: type = To.rational
    ) -> DirectIntegrator:
        """
        Gives a set of numbers in interval (0, 1)

        Example
        -------
        >>> custom_open_formula(1)
        {"nodes": (1/2, ),
         "weights": (1, )}
        >>> custom_open_formula(2)
        {"nodes": (1/4, 3/4),
         "weights": (1/2, 1/2)}
        >>> custom_open_formula(3)
        {"nodes": (1/6, 3/6, 5/6),
         "weights": (3/8, 1/4, 3/8)}
        >>> custom_open_formula(4)
        {"nodes": (1/8, 3/8, 5/8, 7/8),
         "weights": (13/48, 11/48, 11/48, 13/48)}
        >>> custom_open_formula(5)
        {"nodes": (1/10, 3/10, 5/10, 7/10, 9/10),
         "weights": (275/1152, 25/288, 67/192, 25/288, 275/1152)}

        """
        nodes = tuple(NodeSampleFactory.custom_open_formula(npts))
        if npts in IntegratorFactory.custom_open_formula_weights:
            weights = IntegratorFactory.custom_open_formula_weights[npts]
        else:
            weights = tuple(find_polynomial_weights(nodes))
            IntegratorFactory.custom_open_formula_weights[npts] = weights
        return DirectIntegrator(map(convert, nodes), map(convert, weights))

    @lru_cache(maxsize=None)
    @staticmethod
    def clenshaw_curtis(
        npts: int, convert: type = To.finite
    ) -> DirectIntegrator:
        """
        Gives a set of numbers in interval (0, 1)

        Example
        -------
        >>> clenshaw_curtis(1)
        {"nodes": (0.5, ),
         "weights": (1.0, )}
        >>> clenshaw_curtis(2)
        {"nodes": (0.14645, 0.85355),
         "weights": (0.5, 0.5)}
        >>> clenshaw_curtis(3)
        {"nodes": (0.06699, 0.5, 0.93301),
         "weights": (0.22222, 0.55556, 0.22222)}
        >>> clenshaw_curtis(4)
        {"nodes": (0.03806, 0.30866, 0.69134, 0.96194),
         "weights": (0.13215, 0.36785, 0.36785, 0.13215)}
        >>> clenshaw_curtis(5)
        {"nodes": (0.02447, 0.20611, 0.5, 0.79389, 0.97553),
         "weights": (0.08389, 0.26278, 0.30667, 0.26278, 0.08389)}
        """
        if not Is.integer(npts) or npts < 1:
            raise ValueError("npts must be integer > 0")
        nodes = tuple(NodeSampleFactory.chebyshev(npts))
        if npts in IntegratorFactory.clenshaw_curtis_weights:
            weights = IntegratorFactory.clenshaw_curtis_weights[npts]
        else:
            weights = tuple(find_polynomial_weights(nodes))
            IntegratorFactory.clenshaw_curtis_weights[npts] = weights
        return DirectIntegrator(map(convert, nodes), map(convert, weights))


class AdaptativeIntegrator:
    """
    Defines an adaptative integrator that uses the open newton-cotes formula
    to compute the integral of a function.
    """

    def __init__(
        self,
        integrator: DirectIntegrator,
        tolerance: Real = 1e-9,
        maxdepth: int = 12,
    ):
        self.__integrator = integrator
        self.__tolerance = tolerance
        self.__maxdepth = maxdepth

    @property
    def integrator(self) -> DirectIntegrator:
        """
        The direct integrator used to calculate the integral
        """
        return self.__integrator

    @property
    def tolerance(self) -> Real:
        """
        The tolerance to know when to stop the adaptative quadrature
        """
        return self.__tolerance

    @property
    def maxdepth(self) -> Real:
        """
        The maximal depth to stop the quadrature when it does not converge
        """
        return self.__maxdepth

    @integrator.setter
    def integrator(self, value: DirectIntegrator):
        if not Is.instance(value, DirectIntegrator):
            raise TypeError(f"Needs a Direct Integrator: {type(value)}")
        self.__maxdepth = value

    @tolerance.setter
    def tolerance(self, value: Real):
        if not Is.finite(value) or value <= 0:
            raise ValueError(f"Invalid tolerance: {value}")
        self.__tolerance = value

    @maxdepth.setter
    def maxdepth(self, value: int):
        if not Is.integer(value) or value < 0:
            raise ValueError(f"Invalid maxdepth: {value}")
        self.__maxdepth = value

    def integrate(
        self, function: Callable[[Real], Real], interval: Tuple[Real, Real]
    ) -> Real:
        """Computes the integral of func in [a, b]"""

        @lru_cache(maxsize=None)
        def cfunc(node: Real) -> Real:
            return function(node)

        @lru_cache(maxsize=None)
        def cdirect(left: Real, right: Real) -> Real:
            return self.integrator.integrate(function, (left, right))

        def recursive(
            lknot: Real, rknot: Real, tolerance: Real, depth: int
        ) -> Real:
            mknot = (lknot + rknot) / 2
            mvalue = cdirect(lknot, rknot)
            lvalue = cdirect(lknot, mknot)
            rvalue = cdirect(mknot, rknot)
            if (
                depth < self.maxdepth
                and abs(lvalue + rvalue - mvalue) > tolerance
            ):
                lvalue = recursive(lknot, mknot, tolerance / 2, depth + 1)
                rvalue = recursive(mknot, rknot, tolerance / 2, depth + 1)
            return lvalue + rvalue

        result = recursive(interval[0], interval[1], self.tolerance, 0)
        cfunc.cache_clear()
        cdirect.cache_clear()
        return result
