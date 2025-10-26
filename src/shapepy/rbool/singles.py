"""
Defines some basic types of boolean 1D
"""

from __future__ import annotations

from numbers import Real
from typing import Iterable, List, Set, Tuple, Union

from ..scalar.reals import Math
from ..tools import Is, NotExpectedError, To
from .base import EmptyR1, Future, SubSetR1


def lower(number: Real, closed: bool = True) -> IntervalR1:
    """
    Gives the interval such points are lower than given number

    Parameters
    ----------
    number : Real
        The finite number
    closed : bool, default = True
        If the interval is closed on the right end

    Return
    ------
    IntervalR1
        The IntervalR1 such is lower than the given `number`

    Example
    -------
    >>> lower(0)
    (-inf, 0]
    >>> lower(0, False)
    (-inf, 0)
    >>> lower(10, True)
    (-inf, 10]
    """
    return IntervalR1(Math.NEGINF, To.finite(number), False, closed)


def bigger(finite: Real, closed: bool = True) -> IntervalR1:
    """
    Gives the interval such points are bigger than given number

    Parameters
    ----------
    number : Real
        The finite number
    closed : bool, default = True
        If the interval is closed on the left end

    Return
    ------
    IntervalR1
        The IntervalR1 such is bigger than the given `number`

    Example
    -------
    >>> bigger(0)
    [0, +inf)
    >>> bigger(0, False)
    (0, +inf)
    >>> bigger(10, True)
    [10, +inf)
    """
    return IntervalR1(finite, Math.POSINF, closed, False)


class SingleR1(SubSetR1):
    """
    SingleR1 stores only one value, being a subset of the real line

    Only finite values are acceptable
    """

    def __init__(self, value: Real):
        self.__internal = To.finite(value)

    @property
    def internal(self) -> Real:
        """
        Gives the internal real value of the SingleR1

        :getter: Returns the internal value of the SubSetR1
        :type: Real
        """
        return self.__internal

    def __str__(self) -> str:
        return "{" + str(self.__internal) + "}"

    def __repr__(self):
        return f"SingleR1({self.__internal})"

    def __contains__(self, other):
        if Is.infinity(other):
            return False
        other = Future.convert(other)
        return isinstance(other, EmptyR1) or self == other

    def __eq__(self, other):
        other = Future.convert(other)
        return (
            isinstance(other, self.__class__)
            and self.internal == other.internal
        )

    def __invert__(self):
        return DisjointR1(
            [
                lower(self.internal, False),
                bigger(self.internal, False),
            ]
        )

    def __and__(self, other: SubSetR1):
        other = Future.convert(other)
        return self if other.__contains__(self) else EmptyR1()

    def __hash__(self):
        return hash(self.internal)


class IntervalR1(SubSetR1):
    """
    IntervalR1 stores a continuous set of points on R1


    """

    def __init__(
        self, start: Real, end: Real, left: bool = True, right: bool = True
    ):
        start = To.real(start)
        end = To.real(end)
        if end <= start:
            raise ValueError(
                "Received interval [{start}, {end}], but {end} <= {start}"
            )
        if Is.infinity(start) and Is.infinity(end):
            raise ValueError("Received interval (-inf, +inf), use WholeR1")
        if start == Math.NEGINF:
            left = False
        if end == Math.POSINF:
            right = False
        self.__start = start
        self.__end = end
        self.__left = left
        self.__right = right

    # pylint: disable=too-many-return-statements
    def __contains__(self, other):
        if Is.infinity(other):
            return other in (self[0], self[1])
        other = Future.convert(other)
        if isinstance(other, SingleR1):
            other = other.internal
            if other < self[0] or self[1] < other:
                return False
            if self[0] < other < self[1]:
                return True
            return self.closed_left if self[0] == other else self.closed_right
        if isinstance(other, IntervalR1):
            if other[0] < self[0] or self[1] < other[1]:
                return False
            if self[0] < other[0] and other[1] < self[1]:
                return True
            if self[0] == other[0] and (self.closed_left ^ other.closed_left):
                return False
            if self[1] == other[1] and (
                self.closed_right ^ other.closed_right
            ):
                return False
            return True
        if isinstance(other, DisjointR1):
            return all(map(self.__contains__, other))
        return isinstance(other, EmptyR1)

    def __invert__(self):
        if self[0] == Math.NEGINF:
            return bigger(self[1], not self.closed_right)
        if self[1] == Math.POSINF:
            return lower(self[0], not self.closed_left)
        return DisjointR1(
            [
                lower(self[0], not self.closed_left),
                bigger(self[1], not self.closed_right),
            ]
        )

    def __getitem__(self, index):
        return self.__end if index else self.__start

    def __eq__(self, other):
        other = Future.convert(other)
        return (
            isinstance(other, IntervalR1)
            and self[0] == other[0]
            and self[1] == other[1]
            and self.closed_left == other.closed_left
            and self.closed_right == other.closed_right
        )

    def __str__(self):
        msg = "[" if self.closed_left else "("
        msg += str(self[0]) + ", " + str(self[1])
        msg += "]" if self.closed_right else ")"
        return msg

    @property
    def closed_left(self) -> bool:
        """
        Tells if the interval is closed on the left side

        :getter: Returns a boolean that tells if interval is bounded on bot
        :type: bool
        """
        return self.__left

    @property
    def closed_right(self) -> bool:
        """
        Tells if the interval is closed on the right side

        :getter: Returns a boolean that tells if interval is bounded on top
        :type: bool
        """
        return self.__right

    def __hash__(self):
        return hash((self[0], self[1]))


class DisjointR1(SubSetR1):
    """
    Stores the union of SingleR1 and IntervalR1 which are not connected

    The direct constructor should not be used.
    This object should be constructed by the standard boolean operations
    of the some SingleR1 and IntervalR1
    """

    def __init__(self, items: Iterable[Union[SingleR1, IntervalR1]]):
        items = tuple(items)
        if len(items) < 2:
            raise ValueError("Less than 2 items!")

        knots: Set[Real] = set()
        singles: List[SingleR1] = []
        intervs: List[IntervalR1] = []
        for item in items:
            if isinstance(item, SingleR1):
                singles.append(item)
                knots.add(item.internal)
            elif isinstance(item, IntervalR1):
                intervs.append(item)
                if isinstance(item[0], Real):
                    knots.add(item[0])
                if isinstance(item[1], Real):
                    knots.add(item[1])
            else:
                raise TypeError("Received wrong type!")

        weights = tuple(single.internal for single in singles)
        self.__singles = tuple(
            s for _, s in sorted(zip(weights, singles), key=lambda x: x[0])
        )
        weights = tuple((interv[0] + interv[1]) / 2 for interv in intervs)
        self.__intervs = tuple(
            i for _, i in sorted(zip(weights, intervs), key=lambda x: x[0])
        )

    @property
    def singles(self) -> Tuple[SingleR1, ...]:
        """
        Gives all the isolated nodes that are inside the DisjointR1

        :getter: Returns all the isolated points
        :type: Tuple[SingleR1, ...]
        """
        return self.__singles

    @property
    def intervals(self) -> Tuple[IntervalR1, ...]:
        """
        Gives all the non-connected intervals that are inside the DisjointR1

        :getter: Returns all the non-connected intervals
        :type: Tuple[SingleR1, ...]
        """
        return self.__intervs

    def __iter__(self):
        yield from self.__singles
        yield from self.__intervs

    def __contains__(self, other):
        if Is.infinity(other):
            return any(other in sub for sub in self)
        other = Future.convert(other)
        if isinstance(other, DisjointR1):
            return all(sub in self for sub in other)
        return any(other in sub for sub in self)

    # pylint: disable=too-many-branches, too-many-statements
    def __str__(self) -> str:
        ssize = len(self.singles)
        isize = len(self.intervals)
        if ssize == 0:
            return " U ".join(map(str, self.intervals))
        if isize == 0:
            return (
                "{"
                + ", ".join(str(single.internal) for single in self.singles)
                + "}"
            )

        msgs: List[str] = []
        first: bool = True
        flag: bool = False
        i, s = 0, 0
        if self.intervals[0][0] == Math.NEGINF:
            msgs.append(str(self.intervals[0]))
            i += 1
            first = False
        while i < isize and s < ssize:
            if self.singles[s].internal < self.intervals[i][0]:
                if not flag:
                    if not first:
                        msgs.append(" U ")
                    msgs.append("{")
                    first = False
                    flag = True
                else:
                    msgs.append(", ")
                msgs.append(str(self.singles[s].internal))
                s += 1
            else:
                if flag:
                    msgs.append("}")
                    flag = False
                if not first:
                    msgs.append(" U ")
                first = False
                msgs.append(str(self.intervals[i]))
                i += 1
        if s < ssize:
            if not flag:
                if not first:
                    msgs.append(" U ")
                msgs.append("{")
                first = False
                flag = True
            else:
                # msgs.append(", ")
                raise NotExpectedError("Not expected get here")
            msgs.append(str(self.singles[s].internal))
            s += 1
            while s < ssize:
                msgs.append(", ")
                msgs.append(str(self.singles[s].internal))
                s += 1
        if flag:
            msgs.append("}")
        while i < isize:
            msgs.append(" U ")
            msgs.append(str(self.intervals[i]))
            i += 1
        return "".join(msgs)

    def __eq__(self, other):
        other = Future.convert(other)
        if not isinstance(other, DisjointR1):
            return False
        if len(self.singles) != len(other.singles) or len(
            self.intervals
        ) != len(other.intervals):
            return False
        return all(subs == subo for subs, subo in zip(self, other))

    def __hash__(self):
        return hash(tuple(map(hash, self)))
