"""
Defines the basis structure to store subsets of real line.
The main purpose of this module is to be returned from analytics roots
or when concatenating piecewise curves

Here we define 5 classes:
* EmptyR1 : Represents an empty set {} of the real line R1
* WholeR1 : Represents the entire real line R1
* SingleValueR1 : Represents a subset of R1 with only one finite element
* IntervalR1 : Represents a subset of R1 with continuous points
* DisjointR1 : Represents the union of some SingleValueR1 and IntervalR1

With them, we can verify if one subset contains another subset
It's possible to make the standard boolean operations, like union,
intersection, inversion, xor and so on
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from numbers import Real
from typing import Any, Callable, Dict, Iterable, List, Set, Tuple, Union

from . import default
from .error import NotExpectedError
from .logger import debug


@debug("shapepy.bool1d")
def extract_knots(obj: SubSetR1) -> Iterable[Real]:
    """
    Extract all the knots from the SubSetR1.

    If it's a SingleValueR1, gives the internal value
    If it's a IntervalR1, gives the extremities
    If it's a DisjointR1, use recursion
    """
    if isinstance(obj, SingleValueR1):
        yield obj.internal
    if isinstance(obj, IntervalR1):
        if default.isfinite(obj[0]):
            yield obj[0]
        if default.isfinite(obj[1]):
            yield obj[1]
    if isinstance(obj, DisjointR1):
        for sub in obj:
            yield from extract_knots(sub)


@debug("shapepy.bool1d")
def general_doer(
    subsets: Iterable[SubSetR1], function: Callable[[Real], bool]
) -> SubSetR1:
    """
    Receives a group of SubSetR1 and makes the union, the intersection,
    or the inversion depending on the given function.

    This is an internal function and should not be used careless
    """
    subsets = tuple(map(ConverterR1.from_any, subsets))
    if not all(isinstance(subset, SubSetR1) for subset in subsets):
        raise TypeError
    set_all_knots: Set[Real] = set()
    for subset in subsets:
        set_all_knots |= set(extract_knots(subset))
    all_knots: List[Real] = sorted(set_all_knots)
    set_all_knots.add(all_knots[0] - 1)
    set_all_knots.add(all_knots[-1] + 1)
    for knota, knotb in zip(all_knots, all_knots[1:]):
        set_all_knots.add((knota + knotb) / 2)
    eval_knots = sorted(set_all_knots)
    return general_subset(all_knots, map(function, eval_knots))


@debug("shapepy.bool1d")
def general_subset(knots: Iterable[Real], insides: Iterable[bool]) -> SubSetR1:
    """
    Transforms the knots real values and the vector of insides into a SubSetR1

    Basically it gets all the knots from a group of subsets:
    * internal value of SingleValueR1
    * start and end of an IntervalR1
    * knots of the internals for case DisjointR1
    and then mark the middle points from the

    Then, this function walks from left to right, deciding which SingleValueR1
    or IntervalR1 should be gotten to make the return SubSetR1.

    This is an internal function and should not be used careless
    """
    insides = tuple(insides)
    knots = tuple(knots)
    if len(insides) != 2 * len(knots) + 1:
        raise ValueError(f"Invalid: knots = {knots}, insides = {insides}")
    if all(insides):
        return WholeR1()
    if not any(insides):
        return EmptyR1()

    items: List[Union[SingleValueR1, IntervalR1]] = []
    start: Union[None, Real] = None
    close: bool = False
    for i, knot in enumerate(knots):
        left = insides[2 * i]
        midd = insides[2 * i + 1]
        righ = insides[2 * i + 2]
        if left == midd == righ:
            continue
        if not left and not righ:
            items.append(SingleValueR1(knot))
            continue
        if left:  # Finish interval
            if start is None:
                newinterv = IntervalR1.lower(knot, midd)
            else:
                newinterv = IntervalR1(start, knot, close, midd)
            items.append(newinterv)
            start = None
        if righ:
            start = knot
            close = midd
    if start is not None:
        newinterv = IntervalR1.bigger(start, close)
        items.append(newinterv)

    if len(items) == 1:
        return items[0]

    return DisjointR1(items)


def unite(*subsets: SubSetR1) -> SubSetR1:
    """
    Unites a group of subsets

    Parameters
    ----------
    subsets : Iterable[SubSetR1]
        The subsets of R1 to be united

    Return
    ------
    SubSetR1
        The result of the union of the given subsets

    Example
    -------
    >>> unite({10}, [-10, 5])
    [-10, 5] U {10}
    >>> unite((-10, 5), 5)
    (-10, 5]
    >>> unite(("-inf", 10), (-10, "inf"))
    (-inf, +inf)
    """

    def or_func(x):
        return any(x in sub for sub in subsets)

    return general_doer(subsets, or_func)


def intersect(*subsets: SubSetR1) -> SubSetR1:
    """
    Intersects a group of subsets

    Parameters
    ----------
    subsets : Iterable[SubSetR1]
        The subsets of R1 to be intersected

    Return
    ------
    SubSetR1
        The result of the union of the given subsets

    Example
    -------
    >>> intersect({-10}, [-10, 5])
    {-10}
    >>> intersect((-10, 5), [3, 10])
    [3, 5)
    >>> intersect((-10, 0), (0, 10))
    {}
    """

    def and_func(x):
        return all(x in sub for sub in subsets)

    return general_doer(subsets, and_func)


def invert(subset: SubSetR1) -> SubSetR1:
    """
    Computes the complementar / inversion of the given subset

    Parameters
    ----------
    subset : SubSetR1
        The subset of R1 to be inverted

    Return
    ------
    SubSetR1
        The inverted subset

    Example
    -------
    >>> invert({-10})
    (-inf, -10) U (-10, +inf)
    >>> invert((-10, 10))
    (-inf, -10] U [10, +inf)
    >>> invert(("-inf", 0))
    [0, +inf)
    """

    def inv_func(x):
        return x not in subset

    return general_doer((subset,), inv_func)


class SubSetR1(ABC):
    """
    General class to be parent of some others.

    It represents an arbitrary subset of R1.
    """

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __contains__(self, other):
        raise NotImplementedError

    @abstractmethod
    def shift(self, amount: Real) -> SubSetR1:
        """
        Translates the entire subset of R1 to the right by given amount

        new_set = {x + a for x in old_set}

        Parameters
        ----------
        amount : Real
            The quantity to be translated

        Return
        ------
        SubSetR1
            The translated subset

        """
        raise NotImplementedError

    @abstractmethod
    def scale(self, amount: Real) -> SubSetR1:
        """
        Scales the entire subset of R1 to the right by given amount

        new_set = {a * x for x in old_set}

        Negative values are valid.

        Parameters
        ----------
        amount : Real
            The quantity to be scaled. Cannot be zero.

        Return
        ------
        SubSetR1
            The scaled subset
        """
        raise NotImplementedError

    def __invert__(self):
        return invert(self)

    def __or__(self, other):
        return unite(self, ConverterR1.from_any(other))

    def __and__(self, other):
        return intersect(self, ConverterR1.from_any(other))

    def __ror__(self, other):
        return self.__or__(ConverterR1.from_any(other))

    def __rand__(self, other):
        return self.__and__(ConverterR1.from_any(other))

    def __xor__(self, other):
        other = ConverterR1.from_any(other)
        return (self & (~other)) | (other & (~self))

    def __sub__(self, other):
        return self & (~ConverterR1.from_any(other))

    def __rsub__(self, other):
        return (~self) & ConverterR1.from_any(other)

    def __rxor__(self, other):
        return self ^ ConverterR1.from_any(other)

    def __repr__(self):
        return self.__str__()

    def __ne__(self, other):
        return not self == other


class EmptyR1(SubSetR1):
    """
    EmptyR1 class is a singleton that represents an empty set

    It's equivalent to: EmptyR1 = {}
    """

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __contains__(self, other) -> bool:
        if default.isreal(other):
            return False
        return ConverterR1.from_any(other) is self

    def shift(self, amount: Real) -> SubSetR1:
        default.finite(amount)  # Checks if it's finite
        return self

    def scale(self, amount: Real) -> SubSetR1:
        default.finite(amount)  # Checks if it's finite
        return self

    def __invert__(self):
        return WholeR1()

    def __and__(self, other):
        ConverterR1.from_any(other)
        return self

    def __or__(self, other):
        return ConverterR1.from_any(other)

    def __rand__(self, other):
        ConverterR1.from_any(other)
        return self

    def __ror__(self, other):
        return ConverterR1.from_any(other)

    def __str__(self):
        return r"{}"

    def __repr__(self):
        return "EmptyR1"

    def __eq__(self, other):
        return self is ConverterR1.from_any(other)


class WholeR1(SubSetR1):
    """
    WholeR1 class is a singleton that represents the entire real line

    It's equivalent to: WholeR1 = (-inf, +inf)
    """

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __contains__(self, other) -> bool:
        if default.isreal(other):
            return True
        ConverterR1.from_any(other)
        return True

    def shift(self, amount: Real) -> SubSetR1:
        default.finite(amount)  # Checks if it's finite
        return self

    def scale(self, amount: Real) -> SubSetR1:
        default.finite(amount)  # Checks if it's finite
        return self

    def __invert__(self):
        return EmptyR1()

    def __and__(self, other):
        return ConverterR1.from_any(other)

    def __or__(self, other):
        ConverterR1.from_any(other)
        return self

    def __rand__(self, other):
        return ConverterR1.from_any(other)

    def __ror__(self, other):
        ConverterR1.from_any(other)
        return self

    def __str__(self):
        return "(" + str(default.NEGINF) + ", " + str(default.POSINF) + ")"

    def __repr__(self):
        return "WholeR1"

    def __eq__(self, other):
        return self is ConverterR1.from_any(other)


class SingleValueR1(SubSetR1):
    """
    SingleValueR1 stores only one value, being a subset of the real line

    Only finite values are acceptable
    """

    def __init__(self, value: Real):
        self.__internal = default.finite(value)

    @property
    def internal(self) -> Real:
        """
        Gives the internal real value of the SingleValueR1

        :getter: Returns the internal value of the SubSetR1
        :type: Real
        """
        return self.__internal

    def shift(self, amount: Real) -> SubSetR1:
        amount = default.finite(amount)
        return SingleValueR1(self.internal + amount)

    def scale(self, amount: Real) -> SubSetR1:
        amount = default.finite(amount)
        if amount == 0:
            raise ValueError("Cannot scale by zero")
        return SingleValueR1(self.internal * amount)

    def __str__(self) -> str:
        return "{" + str(self.__internal) + "}"

    def __repr__(self):
        return f"SingleValueR1({self.__internal})"

    def __contains__(self, other):
        if default.isinfinity(other):
            return False
        other = ConverterR1.from_any(other)
        return isinstance(other, EmptyR1) or self == other

    def __eq__(self, other):
        other = ConverterR1.from_any(other)
        return (
            isinstance(other, self.__class__)
            and self.internal == other.internal
        )

    def __invert__(self):
        return DisjointR1(
            [
                IntervalR1.lower(self.internal, False),
                IntervalR1.bigger(self.internal, False),
            ]
        )

    def __and__(self, other: SubSetR1):
        other = ConverterR1.from_any(other)
        return self if other.__contains__(self) else EmptyR1()


class IntervalR1(SubSetR1):
    """
    IntervalR1 stores a continuous set of points on R1


    """

    @classmethod
    def lower(cls, number: Real, closed: bool = True) -> IntervalR1:
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
        >>> IntervalR1.lower(0)
        (-inf, 0]
        >>> IntervalR1.lower(0, False)
        (-inf, 0)
        >>> IntervalR1.lower(10, True)
        (-inf, 10]
        """
        return cls(default.NEGINF, default.finite(number), False, closed)

    @classmethod
    def bigger(cls, finite: Real, closed: bool = True) -> IntervalR1:
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
        >>> IntervalR1.bigger(0)
        [0, +inf)
        >>> IntervalR1.bigger(0, False)
        (0, +inf)
        >>> IntervalR1.bigger(10, True)
        [10, +inf)
        """
        return cls(finite, default.POSINF, closed, False)

    def __init__(
        self, start: Real, end: Real, left: bool = True, right: bool = True
    ):
        start = default.real(start)
        end = default.real(end)
        if end <= start:
            raise ValueError(
                "Received interval [{start}, {end}], but {end} <= {start}"
            )
        if default.isinfinity(start) and default.isinfinity(end):
            raise ValueError("Received interval (-inf, +inf), use WholeR1")
        if start == default.NEGINF:
            left = False
        if end == default.POSINF:
            right = False
        self.__start = start
        self.__end = end
        self.__left = left
        self.__right = right

    # pylint: disable=too-many-return-statements
    @debug("shapepy.bool1d.interval")
    def __contains__(self, other):
        if default.isinfinity(other):
            return self[0] == other or other == self[1]
        other = ConverterR1.from_any(other)
        if isinstance(other, SingleValueR1):
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

    def shift(self, amount: Real) -> SubSetR1:
        amount = default.finite(amount)
        newlef = self[0] + amount
        newrig = self[1] + amount
        return IntervalR1(newlef, newrig, self.closed_left, self.closed_right)

    def scale(self, amount: Real) -> SubSetR1:
        amount = default.finite(amount)
        if amount == 0:
            raise ValueError("Cannot scale by zero")
        newlef = self[0] * amount
        newrig = self[1] * amount
        clolef = self.closed_left
        clorig = self.closed_right
        if amount < 0:
            newlef, newrig = newrig, newlef
            clolef, clorig = clorig, clolef
        return IntervalR1(newlef, newrig, clolef, clorig)

    def __invert__(self):
        if self[0] == default.NEGINF:
            return IntervalR1.bigger(self[1], not self.closed_right)
        if self[1] == default.POSINF:
            return IntervalR1.lower(self[0], not self.closed_left)
        return DisjointR1(
            [
                IntervalR1.lower(self[0], not self.closed_left),
                IntervalR1.bigger(self[1], not self.closed_right),
            ]
        )

    def __getitem__(self, index):
        return self.__end if index else self.__start

    def __eq__(self, other):
        other = ConverterR1.from_any(other)
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


class DisjointR1(SubSetR1):
    """
    Stores the union of SingleValueR1 and IntervalR1 which are not connected

    The direct constructor should not be used.
    This object should be constructed by the standard boolean operations
    of the some SingleValueR1 and IntervalR1
    """

    def __init__(self, items: Iterable[Union[SingleValueR1, IntervalR1]]):
        items = tuple(items)
        if len(items) < 2:
            raise ValueError("Less than 2 items!")

        knots: Set[Real] = set()
        singles: List[SingleValueR1] = []
        intervs: List[IntervalR1] = []
        for item in items:
            if isinstance(item, SingleValueR1):
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
    def singles(self) -> Tuple[SingleValueR1, ...]:
        """
        Gives all the isolated nodes that are inside the DisjointR1

        :getter: Returns all the isolated points
        :type: Tuple[SingleValueR1, ...]
        """
        return self.__singles

    @property
    def intervals(self) -> Tuple[IntervalR1, ...]:
        """
        Gives all the non-connected intervals that are inside the DisjointR1

        :getter: Returns all the non-connected intervals
        :type: Tuple[SingleValueR1, ...]
        """
        return self.__intervs

    def __iter__(self):
        yield from self.__singles
        yield from self.__intervs

    def __contains__(self, other):
        if default.isinfinity(other):
            return any(other in sub for sub in self)
        other = ConverterR1.from_any(other)
        if isinstance(other, DisjointR1):
            return all(sub in self for sub in other)
        return any(other in sub for sub in self)

    def shift(self, amount: Real) -> SubSetR1:
        amount = default.finite(amount)
        newiterable = (sub.shift(amount) for sub in self)
        return DisjointR1(newiterable)

    def scale(self, amount: Real) -> SubSetR1:
        amount = default.finite(amount)
        newiterable = (sub.scale(amount) for sub in self)
        return DisjointR1(newiterable)

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
        if self.intervals[0][0] == default.NEGINF:
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
                raise NotImplementedError("Not expected get here")
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
        other = ConverterR1.from_any(other)
        if not isinstance(other, DisjointR1):
            return False
        if len(self.singles) != len(other.singles) or len(
            self.intervals
        ) != len(other.intervals):
            return False
        return all(subs == subo for subs, subo in zip(self, other))


def infimum(subset: SubSetR1) -> Union[Real, None]:
    """
    Computes the infimum of the SubSetR1

    Parameters
    ----------
    subset: SubSetR1
        The subset to get the infimum

    Return
    ------
    Real | None
        The infimum value, or None if receives EmptyR1

    Example
    -------
    >>> infimum("{}")  # EmptyR1
    None
    >>> infimum("(-inf, +inf)")  # WholeR1
    -inf
    >>> infimum("{-10}")  # SingleValueR1
    -10
    >>> infimum("[-10, 10]")  # IntervalR1
    -10
    >>> infimum("(-10, 10)")  # IntervalR1
    -10
    >>> infimum("{0, 10, 20}")  # DisjointR1
    0
    """
    subset = ConverterR1.from_any(subset)
    if isinstance(subset, EmptyR1):
        return None
    if isinstance(subset, WholeR1):
        return default.NEGINF
    if isinstance(subset, SingleValueR1):
        return subset.internal
    if isinstance(subset, IntervalR1):
        return subset[0]
    if isinstance(subset, DisjointR1):
        return min(map(infimum, subset))
    raise NotExpectedError(f"Received {type(subset)}: {subset}")


def minimum(subset: SubSetR1) -> Union[Real, None]:
    """
    Computes the minimum of the SubSetR1

    Parameters
    ----------
    subset: SubSetR1
        The subset to get the minimum

    Return
    ------
    Real | None
        The minimum value or None

    Example
    -------
    >>> minimum("{}")  # EmptyR1
    None
    >>> minimum("(-inf, +inf)")  # WholeR1
    None
    >>> minimum("{-10}")  # SingleValueR1
    -10
    >>> minimum("[-10, 10]")  # IntervalR1
    -10
    >>> minimum("(-10, 10)")  # IntervalR1
    None
    >>> minimum("{0, 10, 20}")  # DisjointR1
    0
    """
    subset = ConverterR1.from_any(subset)
    if isinstance(subset, (EmptyR1, WholeR1)):
        return None
    if isinstance(subset, SingleValueR1):
        return subset.internal
    if isinstance(subset, IntervalR1):
        return (
            subset[0]
            if (default.isfinite(subset[0]) and subset.closed_left)
            else None
        )
    if isinstance(subset, DisjointR1):
        infval = default.POSINF
        global_minval = default.POSINF
        for sub in subset:
            infval = min(infval, infimum(sub))
            minval = minimum(sub)
            if minval is not None:
                global_minval = min(global_minval, minval)
        return infval if (global_minval == infval) else None
    raise NotExpectedError(f"Received {type(subset)}: {subset}")


def maximum(subset: SubSetR1) -> Union[Real, None]:
    """
    Computes the maximum of the SubSetR1

    Parameters
    ----------
    subset: SubSetR1
        The subset to get the maximum

    Return
    ------
    Real | None
        The maximum value of the subset

    Example
    -------
    >>> maximum("{}")  # EmptyR1
    None
    >>> maximum("(-inf, +inf)")  # WholeR1
    None
    >>> maximum("{-10}")  # SingleValueR1
    -10
    >>> maximum("[-10, 10]")  # IntervalR1
    10
    >>> maximum("(-10, 10)")  # IntervalR1
    None
    >>> maximum("{0, 10, 20}")  # DisjointR1
    20
    """
    subset = ConverterR1.from_any(subset)
    if isinstance(subset, (EmptyR1, WholeR1)):
        return None
    if isinstance(subset, SingleValueR1):
        return subset.internal
    if isinstance(subset, IntervalR1):
        return (
            subset[1]
            if (default.isfinite(subset[1]) and subset.closed_right)
            else None
        )
    if isinstance(subset, DisjointR1):
        supval = default.NEGINF
        global_maxval = default.NEGINF
        for sub in subset:
            supval = max(supval, supremum(sub))
            maxval = maximum(sub)
            if maxval is not None:
                global_maxval = max(global_maxval, maxval)
        return maxval if (global_maxval == supval) else None
    raise NotExpectedError(f"Received {type(subset)}: {subset}")


def supremum(subset: SubSetR1) -> Union[Real, None]:
    """
    Computes the supremum of the SubSetR1

    Parameters
    ----------
    subset: SubSetR1
        The subset to get the supremum

    Return
    ------
    Real | None
        The supremum value, or None if receives EmptyR1

    Example
    -------
    >>> supremum("{}")  # EmptyR1
    None
    >>> supremum("(-inf, +inf)")  # WholeR1
    +inf
    >>> supremum("{-10}")  # SingleValueR1
    -10
    >>> supremum("[-10, 10]")  # IntervalR1
    10
    >>> supremum("(-10, 10)")  # IntervalR1
    10
    >>> supremum("{0, 10, 20}")  # DisjointR1
    20
    """
    subset = ConverterR1.from_any(subset)
    if isinstance(subset, EmptyR1):
        return None
    if isinstance(subset, WholeR1):
        return default.POSINF
    if isinstance(subset, SingleValueR1):
        return subset.internal
    if isinstance(subset, IntervalR1):
        return subset[1]
    if isinstance(subset, DisjointR1):
        return max(map(supremum, subset))
    raise NotExpectedError(f"Received {type(subset)}: {subset}")


class ConverterR1:
    """
    Static class that contains only static methods responsible to convert
    some basic types into a SubSetR1.

    The easier example is from string:
    * "{}" represents a empty set, so returns the EmptyR1 instance
    * "(-inf, +inf)" represents the entire real line, returns WholeR1 instance
    """

    # pylint: disable=too-many-return-statements
    @staticmethod
    def from_any(obj: Any) -> SubSetR1:
        """
        Converts an arbitrary object into a SubSetR1 instance.
        If it's already a SubSetR1 instance, returns the object

        Example
        -------
        >>> ConverterR1.from_any("{}")
        {}
        >>> ConverterR1.from_any("(-inf, +inf)")
        (-inf, +inf)
        """
        if isinstance(obj, SubSetR1):
            return obj
        if isinstance(obj, Real):
            number = default.finite(obj)
            return SingleValueR1(number)
        if isinstance(obj, str):
            return ConverterR1.from_str(obj)
        if isinstance(obj, dict):
            return ConverterR1.from_dict(obj)
        if isinstance(obj, set):
            return ConverterR1.from_set(obj)
        if isinstance(obj, tuple):
            return ConverterR1.from_tuple(obj)
        if isinstance(obj, list):
            return ConverterR1.from_list(obj)
        raise NotExpectedError(f"Received object {type(obj)} = {obj}")

    @debug("shapepy.bool1d")
    @staticmethod
    def from_str(string: str) -> SubSetR1:
        """
        Converts a string into a SubSetR1 instance.

        Example
        -------
        >>> ConverterR1.from_str("{}")  # EmptyR1
        {}
        >>> ConverterR1.from_str("(-inf, +inf)")  # WholeR1
        (-inf, +inf)
        >>> ConverterR1.from_str("{10}")  # SingleValueR1
        {10}
        >>> ConverterR1.from_str("[-10, 0] U {5, 10}")  # DisjointR1
        [-10, 0] U {5, 10}
        """
        string = string.strip()
        if "U" in string:
            return unite(*map(ConverterR1.from_str, string.split("U")))
        if string[0] == "{" and string[-1] == "}":
            result = EmptyR1()
            for substr in string[1:-1].split(","):
                if not substr:  # Empty string
                    continue
                finite = default.finite(substr)
                result |= SingleValueR1(finite)
            return result
        if string[0] in "([" and string[-1] in ")]":
            stastr, endstr = string[1:-1].split(",")
            start = default.real(stastr)
            end = default.real(endstr)
            if start == default.NEGINF and end == default.POSINF:
                return WholeR1()
            left = string[0] == "["
            right = string[-1] == "]"
            return IntervalR1(start, end, left, right)
        raise ValueError(f"Cannot parse '{string}' into a SubSetR1 instance")

    @debug("shapepy.bool1d")
    @staticmethod
    def from_dict(dic: Dict) -> SubSetR1:
        """
        Converts a dictonary into a SubSetR1 instance

        Only accepts an empty dict, since it's the standard type of {}:

        Example
        -------
        >>> variable = {}
        >>> type(variable)
        <class 'dict'>
        >>> subset = ConverterR1.from_dict(variable)
        >>> subset
        {}
        >>> type(subset)
        <class 'EmptyR1'>
        """
        if not isinstance(dic, dict):
            raise TypeError
        result = EmptyR1()
        if len(dic) != 0:
            raise NotExpectedError
        return result

    @debug("shapepy.bool1d")
    @staticmethod
    def from_set(items: Set[object]) -> SubSetR1:
        """
        Converts a set into a SubSetR1 instance

        Example
        -------
        >>> variable = {-10, 5}
        >>> type(variable)
        <class 'set'>
        >>> subset = ConverterR1.from_set(variable)
        >>> subset
        {-10, 5}
        >>> type(subset)
        <class 'DisjointR1'>
        """
        if not isinstance(items, set):
            raise TypeError
        result = EmptyR1()
        for item in items:
            result |= default.finite(item)
        return result

    @debug("shapepy.bool1d")
    @staticmethod
    def from_tuple(pair: Tuple[object]) -> SubSetR1:
        """
        Converts a tuple of two values into a SubSetR1 instance

        It's the standard open interval, or the WholeR1

        Example
        -------
        >>> variable = (-10, 10)
        >>> type(variable)
        <class 'tuple'>
        >>> subset = ConverterR1.from_tuple(variable)
        >>> subset
        (-10, 10)
        >>> type(subset)
        <class 'IntervalR1'>
        >>> variable = ("-inf", "inf")
        >>> subset = ConverterR1.from_tuple(variable)
        >>> type(subset)
        <class 'WholeR1'>
        """
        if not isinstance(pair, tuple):
            raise TypeError
        if len(pair) != 2:
            raise ValueError
        sta = default.real(pair[0])
        end = default.real(pair[1])
        if sta == default.NEGINF and end == default.POSINF:
            return WholeR1()
        if sta == default.NEGINF:
            return IntervalR1.lower(end, False)
        if end == default.POSINF:
            return IntervalR1.bigger(sta, False)
        return IntervalR1(sta, end, False, False)

    @debug("shapepy.bool1d")
    @staticmethod
    def from_list(pair: List[object]) -> SubSetR1:
        """
        Converts a list of two values into a SubSetR1 instance

        It's the standard closed interval, or the WholeR1

        Example
        -------
        >>> variable = [-10, 10]
        >>> type(variable)
        <class 'list'>
        >>> subset = ConverterR1.from_list(variable)
        >>> subset
        [-10, 10]
        >>> type(subset)
        <class 'IntervalR1'>
        >>> variable = ["-inf", "inf"]
        >>> subset = ConverterR1.from_list(variable)
        >>> subset
        (-inf, +inf)
        >>> type(subset)
        <class 'WholeR1'>
        """
        if not isinstance(pair, list):
            raise TypeError
        if len(pair) != 2:
            raise ValueError
        sta = default.real(pair[0])
        end = default.real(pair[1])
        if sta == default.NEGINF and end == default.POSINF:
            return WholeR1()
        if sta == default.NEGINF:
            return IntervalR1.lower(end, True)
        if end == default.POSINF:
            return IntervalR1.bigger(sta, True)
        return IntervalR1(sta, end, True, True)


subsetR1 = ConverterR1.from_any
