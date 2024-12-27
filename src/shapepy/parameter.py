from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Tuple, Union

Parameter = Union[int, float, Fraction]


def general_interval(
    start: Parameter, end: Parameter
) -> Union[EmptyParameter, WholeParameter, Parameter, ParamInterval]:
    if start < end:
        if start == BaseParameter.botinf and end == BaseParameter.topinf:
            return WholeParameter()
        return ParamInterval(start, end)
    if start == end:
        return start
    return EmptyParameter()


def select_intervals(
    knots: Iterable[Parameter], insiders: Iterable[bool]
) -> Iterable[ParamInterval]:
    knots = tuple(knots)
    intervals = []
    sta = None
    for i, inside in enumerate(insiders):
        if inside:
            if not sta:
                sta = i
        elif sta:
            interval = general_interval(knots[sta], knots[i])
            intervals.append(interval)
            sta = None
    if sta is not None:
        interval = general_interval(knots[sta], knots[-1])
        intervals.append(interval)
    return intervals


def unite_intervals(
    intervals: Iterable[ParamInterval],
) -> Union[WholeParameter, DisjointParameters, ParamInterval]:
    knots = {BaseParameter.botinf, BaseParameter.topinf}
    for interval in intervals:
        if not isinstance(interval, ParamInterval):
            raise TypeError
        knots.add(interval[0])
        knots.add(interval[1])
    knots = tuple(sorted(knots))
    insiders = [False] * (len(knots) - 1)
    midknots = list((a + b) / 2 for a, b in zip(knots, knots[1:]))
    midknots[0] = knots[1] - 1
    midknots[-1] = knots[-2] + 1
    for i, midknot in enumerate(midknots):
        insiders[i] = any(seg[0] <= midknot <= seg[1] for seg in intervals)
    if all(insiders):
        return WholeParameter()
    intervals = tuple(select_intervals(knots, insiders))
    if len(intervals) == 1:
        return intervals[0]
    return DisjointParameters(intervals)


def inters_intervals(
    intervals: Iterable[ParamInterval],
) -> Union[EmptyParameter, ParamInterval, ParamInterval]:
    knots = {BaseParameter.botinf, BaseParameter.topinf}
    for interval in intervals:
        if not isinstance(interval, ParamInterval):
            raise TypeError
        knots.add(interval[0])
        knots.add(interval[1])
    knots = tuple(sorted(knots))
    inside_knots = []
    for knot in knots:
        if all(seg[0] <= knot <= seg[1] for seg in intervals):
            inside_knots.append(knot)
    if len(inside_knots) == 0:
        return EmptyParameter()
    return general_interval(inside_knots[0], inside_knots[-1])


def extract_nodes_intervals(
    items: Iterable[BaseParameter],
) -> Tuple[Iterable[Parameter], Iterable[ParamInterval]]:
    nodes = []
    intervals = []
    for item in items:
        if isinstance(item, DisjointParameters):
            intervals += list(item.intervals)
            nodes += list(item.nodes)
        elif isinstance(item, ParamInterval):
            intervals.append(item)
        else:
            nodes.append(item)
    return nodes, intervals


def unite_parameters(*items: BaseParameter) -> BaseParameter:
    items = tuple(i for i in items if not isinstance(i, EmptyParameter))
    if len(items) == 0:
        return EmptyParameter()
    if any(isinstance(i, WholeParameter) for i in items):
        return WholeParameter()
    if len(items) == 1:
        return items[0]
    nodes, intervals = extract_nodes_intervals(items)
    union = unite_intervals(intervals)
    if isinstance(union, WholeParameter):
        return union
    nodes = tuple(node for node in nodes if node not in union)
    if isinstance(union, DisjointParameters):
        intervals = tuple(union)
    elif isinstance(union, ParamInterval):
        intervals = (union,)
    else:
        raise NotImplementedError
    items = intervals + nodes
    if len(items) == 1:
        return items[0]
    return DisjointParameters(items)


def inters_parameters(*items: BaseParameter) -> BaseParameter:
    items = tuple(i for i in items if not isinstance(i, WholeParameter))
    if len(items) == 0:
        return WholeParameter()
    if any(isinstance(i, EmptyParameter) for i in items):
        return EmptyParameter()
    if len(items) == 1:
        return items[0]
    nodes, intervals = extract_nodes_intervals(items)
    inters = inters_intervals(intervals)
    if len(nodes) == 0:
        return inters
    nodes = set(nodes)
    if len(nodes) > 1:
        return EmptyParameter()
    node = tuple(nodes)[0]
    return node if node in inters else EmptyParameter()


class BaseParameter(object):
    topinf = float("inf")
    botinf = -float("inf")

    def __or__(self, value):
        return unite_parameters(self, value)

    def __and__(self, value):
        return inters_parameters(self, value)

    def __ror__(self, value):
        return self.__or__(value)

    def __rand__(self, value):
        return self.__and__(value)

    def __repr__(self):
        return self.__str__()


class EmptyParameter(BaseParameter):
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __contains__(self, other) -> bool:
        return other is self

    def __and__(self, _):
        return self

    def __or__(self, value):
        return value

    def __str__(self):
        return r"{}"

    def __eq__(self, value):
        return self is value


class WholeParameter(BaseParameter):
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __contains__(self, _) -> bool:
        return True

    def __and__(self, other):
        return other

    def __or__(self, _):
        return self

    def __str__(self):
        return "(-inf, inf)"

    def __eq__(self, value):
        return self is value


class ParamInterval(BaseParameter):
    def __init__(self, start: Parameter, end: Parameter):
        if end <= start:
            raise ValueError("Cannot be interveted")
        if start == self.botinf and end == self.topinf:
            raise ValueError("Use Whole")
        self.__start = start
        self.__end = end

    def __and__(self, value):
        if not isinstance(value, BaseParameter):
            return inters_parameters(self, value)
        if isinstance(
            value, (EmptyParameter, WholeParameter, DisjointParameters)
        ):
            return value & self
        if not isinstance(value, ParamInterval):
            raise TypeError
        sta = max(self[0], value[0])
        end = min(self[1], value[1])
        return general_interval(sta, end)

    def __or__(self, value):
        if not isinstance(value, BaseParameter):
            return unite_parameters(self, value)
        if isinstance(
            value, (EmptyParameter, WholeParameter, DisjointParameters)
        ):
            return value | self
        if not isinstance(value, ParamInterval):
            raise TypeError
        if value[1] < self[0] or self[1] < value[0]:
            return DisjointParameters([self, value])
        sta = min(self[0], value[0])
        end = max(self[1], value[1])
        return general_interval(sta, end)

    def __getitem__(self, index):
        return self.__end if index else self.__start

    def __contains__(self, other):
        if isinstance(other, EmptyParameter):
            return True
        if isinstance(other, WholeParameter):
            return False
        if isinstance(other, ParamInterval):
            return self[0] <= other[0] and other[1] <= self[1]
        if isinstance(other, DisjointParameters):
            return all(sub in self for sub in other)
        return self[0] <= other <= self[1]

    def __eq__(self, value):
        if not isinstance(value, ParamInterval):
            return False
        return self[0] == value[0] and self[1] == value[1]

    def __str__(self):
        msg = "[" if self[0] != self.botinf else "("
        msg += str(self[0]) + ", " + str(self[1])
        msg += "]" if self[1] != self.topinf else ")"
        return msg


class DisjointParameters(BaseParameter):
    def __init__(self, items: Iterable[Union[Parameter, ParamInterval]]):
        items = tuple(items)
        if len(items) < 2:
            raise ValueError("Less than 2 items!")
        if any(
            isinstance(
                item, (EmptyParameter, WholeParameter, DisjointParameters)
            )
            for item in items
        ):
            raise ValueError("Received wrong")

        weights = (
            i if not isinstance(i, ParamInterval) else (i[0] + i[1]) / 2
            for i in items
        )
        items = tuple(i for _, i in sorted(zip(weights, items)))
        self.__items = items

    @property
    def nodes(self) -> Iterable[Parameter]:
        return (i for i in self if not isinstance(i, ParamInterval))

    @property
    def intervals(self) -> Iterable[ParamInterval]:
        return (i for i in self if isinstance(i, ParamInterval))

    def __len__(self):
        return len(self.__items)

    def __getitem__(self, index):
        return self.__items[index]

    def __iter__(self):
        yield from self.__items

    def __contains__(self, other):
        if isinstance(other, DisjointParameters):
            return all(sub in self for sub in other)
        if isinstance(other, ParamInterval):
            return other[0] in self and other[1] in self
        return any(other in sub for sub in self)

    def __str__(self) -> str:
        msgs = []
        nodes = []
        for sub in self:
            if isinstance(sub, ParamInterval):
                if nodes:
                    msgs.append("{" + ", ".join(map(str, nodes)) + "}")
                    nodes = []
                msgs.append(str(sub))
            else:
                nodes.append(sub)
        if nodes:
            msgs.append("{" + ", ".join(map(str, nodes)) + "}")
        return " U ".join(msgs)

    def __eq__(self, value):
        if not isinstance(value, DisjointParameters):
            return False
        if len(self) != len(value):
            return False
        for subself, subvalu in zip(self, value):
            if subself != subvalu:
                return False
        return True
