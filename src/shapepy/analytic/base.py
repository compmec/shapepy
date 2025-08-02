"""
Defines the IAnalytic class to serve as base for other
analytic functions, such as Polynomial, Bezier, Trigonometric, etc
"""

from abc import ABC, abstractmethod

from ..scalar.reals import Real


# pylint: disable=too-few-public-methods
class IAnalytic(ABC):
    """
    Class parent of Analytic classes
    """

    @abstractmethod
    def __call__(self, node: Real) -> Real:
        raise NotImplementedError
