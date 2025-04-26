"""
Defines the Quadrature class and some functions
that creates some known quadrature rules.

It's used to compute numerically the definite integral
"""

from __future__ import annotations

from numbers import Real
from typing import Callable, Iterable, Tuple

from . import default
from .logger import debug


class Quadrature:
    """
    Stores a quadrature rule to integrate over the interval [0, 1]
    """

    def __init__(self, nodes: Iterable[Real], weights: Iterable[Real]):
        self.__nodes = tuple(nodes)
        self.__weights = tuple(weights)

    def __str__(self):
        return f"Quadrature({self.nodes}, {self.weights})"

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        yield from zip(self.nodes, self.weights)

    @property
    def nodes(self) -> Tuple[Real, ...]:
        """
        Gives the integration nodes in the interval [0, 1]

        :getter: Returns the t_i values used to evaluate at f(t_i)
        :type: Tuple[Real, ...]
        """
        return self.__nodes

    @property
    def weights(self) -> Tuple[Real, ...]:
        """
        Gives the integration weights used to numerical integration

        :getter: Returns the w_i values used to evaluate at sum w_i * f(t_i)
        :type: Tuple[Real, ...]
        """
        return self.__weights

    def direct(
        self, function: Callable[[Real], Real], sta: Real, end: Real
    ) -> Real:
        """
        Computes the definite integral using an the stored rule

            I = int_a^b f(t) dt = sum_i w_i * f(t_i)

        Where t_i are some points in the interval [a, b]

        Parameters
        ----------
        function: Callable[[Real], Real]
            The function to be integrated
        sta: Real
            The starting point of the definite integral
        end: Real
            The ending point of the definite integral

        Return
        ------
        Real
            The value 'I' of the definite integral

        """
        diff = end - sta
        return diff * sum(
            weig * function(sta + node * diff) for node, weig in self
        )

    def adaptative(
        self,
        function: Callable[[Real], Real],
        sta_node: Real,
        end_node: Real,
        tolerance: Real = 1e-9,
    ) -> Real:
        """
        Computes the definite integral using an adaptative rule

            I = int_a^b f(t) dt

        Parameters
        ----------
        function: Callable[[Real], Real]
            The function to be integrated
        sta_node: Real
            The starting point of the definite integral
        end_node: Real
            The ending point of the definite integral
        tolerance: Real
            The numerical tolerance to decide when stop the integral

        Return
        ------
        Real
            The value 'I' of the definite integral

        """
        mid_node = (sta_node + end_node) / 2
        mid_inte = self.direct(function, sta_node, end_node)
        lef_inte = self.direct(function, sta_node, mid_node)
        rig_inte = self.direct(function, mid_node, end_node)
        tolsat = abs(lef_inte + rig_inte - mid_inte) >= tolerance
        if tolsat:
            lef_inte = self.adaptative(
                function,
                sta_node,
                mid_node,
                tolerance / 2,
            )
            rig_inte = self.adaptative(
                function,
                mid_node,
                end_node,
                tolerance / 2,
            )
        return lef_inte + rig_inte


@debug("shapepy.analytic.quadrature")
def closed_newton(npts: int) -> Quadrature:
    """Closed newton cotes formula

    Parameters
    ----------
    npts: int
        The number of points to use gauss integration.
        Must be at least 2

    Return
    ------
    Quadrature
        The quadrature on the interval [0, 1]
    """
    if not default.isinteger(npts) or npts < 2:
        raise ValueError(f"Invalid npts: {npts}")
    nodes = (default.rational(i, npts - 1) for i in range(npts))
    if npts == 2:
        weights = (default.rational(1, 2), default.rational(1, 2))
    elif npts == 3:
        weights = (
            default.rational(1, 6),
            default.rational(2, 3),
            default.rational(1, 6),
        )
    elif npts == 4:
        weights = (
            default.rational(1, 8),
            default.rational(3, 8),
            default.rational(3, 8),
            default.rational(1, 8),
        )
    elif npts == 5:
        weights = (
            default.rational(7, 90),
            default.rational(16, 45),
            default.rational(2, 15),
            default.rational(16, 45),
            default.rational(7, 90),
        )
    else:
        raise NotImplementedError(f"Not closed Newton for {npts}")

    nodes = map(default.finite, nodes)
    weights = map(default.finite, weights)
    return Quadrature(nodes, weights)


@debug("shapepy.analytic.quadrature")
def open_newton(npts: int) -> Quadrature:
    """Open newton cotes formula

    Parameters
    ----------
    npts: int
        The number of points to use gauss integration.
        Must be at least 2

    Return
    ------
    Quadrature
        The quadrature on the interval [0, 1]
    """
    if not default.isinteger(npts) or npts < 1:
        raise ValueError(f"Invalid npts: {npts}")
    nodes = tuple(default.rational(i + 1, npts + 1) for i in range(npts))
    if npts == 1:
        weights = (1,)
    elif npts == 2:
        weights = (default.rational(1, 2), default.rational(1, 2))
    elif npts == 3:
        weights = (
            default.rational(2, 3),
            default.rational(-1, 3),
            default.rational(2, 3),
        )
    else:
        raise NotImplementedError(f"Not open Newton for {npts}")

    nodes = map(default.finite, nodes)
    weights = map(default.finite, weights)
    return Quadrature(nodes, weights)


@debug("shapepy.analytic.quadrature")
def chebyshev(npts: int) -> Quadrature:
    """Chebyshev quadrature

    Parameters
    ----------
    npts: int
        The number of points to use chebyshev integration.
        Must be at least 1

    Return
    ------
    Quadrature
        The quadrature on the interval [0, 1]
    """
    if not default.isinteger(npts) or npts < 1:
        raise ValueError(f"Invalid npts: {npts}")
    nodes = (
        default.tursin(default.rational(num, 8 * npts)) ** 2
        for num in range(1, 2 * npts, 2)
    )
    if npts == 1:
        weights = (1,)
    elif npts == 2:
        weights = (default.rational(1, 2), default.rational(1, 2))
    elif npts == 3:
        weights = (
            default.rational(2, 9),
            default.rational(5, 9),
            default.rational(2, 9),
        )
    elif npts == 4:
        root2 = default.sqrt(2)
        weights = (
            (3 - root2) / 12,
            (3 + root2) / 12,
            (3 + root2) / 12,
            (3 - root2) / 12,
        )
    elif npts == 5:
        root5 = default.sqrt(5)
        weights = (
            (13 - 3 * root5) / 75,
            (13 + 3 * root5) / 75,
            default.rational(23, 75),
            (13 + 3 * root5) / 75,
            (13 - 3 * root5) / 75,
        )
    else:
        raise NotImplementedError(f"Not chebyshev for {npts}")

    nodes = map(default.finite, nodes)
    weights = map(default.finite, weights)
    return Quadrature(nodes, weights)


@debug("shapepy.analytic.quadrature")
def gauss(npts: int) -> Quadrature:
    """Gauss quadrature

    Parameters
    ----------
    npts: int
        The number of points to use gauss integration.
        Must be at least 1

    Return
    ------
    Quadrature
        The quadrature on the interval [0, 1]
    """
    if not default.isinteger(npts) or npts < 1:
        raise ValueError(f"Invalid npts: {npts}")
    import numpy as np  # pylint: disable=import-outside-toplevel

    nodes, weights = np.polynomial.legendre.leggauss(npts)
    nodes = ((1 + default.finite(node)) / 2 for node in nodes)
    weights = (default.finite(weight) / 2 for weight in weights)
    return Quadrature(nodes, weights)
