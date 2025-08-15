"""Defines methods that are common for the entire package"""

from copy import deepcopy
from typing import Any, Tuple

from .scalar.angle import Angle
from .scalar.reals import Real


def move(obj: Any, vector: Tuple[Real, Real]) -> Any:
    """
    Moves/translate 2D object in the plane

    Parameters
    ----------

    point : Point2D
        The amount to move

    :return: The same instance
    :rtype: SubSetR2

    Example use
    -----------
    >>> from shapepy import Primitive
    >>> circle = Primitive.circle()
    >>> circle.move((1, 2))

    """
    return deepcopy(obj).move(vector)


def scale(obj: Any, amount: Tuple[Real, Tuple[Real, Real]]) -> Any:
    """
    Moves/translate 2D object in the plane

    Parameters
    ----------

    point : Point2D
        The amount to move

    :return: The same instance
    :rtype: SubSetR2

    Example use
    -----------
    >>> from shapepy import Primitive
    >>> circle = Primitive.circle()
    >>> circle.scale((1, 2))

    """
    return deepcopy(obj).scale(amount)


def rotate(obj: Any, angle: Angle) -> Any:
    """
    Moves/translate 2D object in the plane

    Parameters
    ----------

    point : Point2D
        The amount to move

    :return: The same instance
    :rtype: SubSetR2

    Example use
    -----------
    >>> from shapepy import Primitive
    >>> circle = Primitive.circle()
    >>> circle.move(1, 2)

    """
    return deepcopy(obj).rotate(angle)


def clean(obj: Any) -> Any:
    """
    Cleans the object, removing the unecessary data
    """
    return deepcopy(obj).clean()
