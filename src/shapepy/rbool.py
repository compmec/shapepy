"""Wraps the rbool library and add some useful functions for this package"""

from typing import Any, Callable, Iterator, Type

import rbool

EmptyR1: Type = rbool.Empty
IntervalR1: Type = rbool.Interval
SingleR1: Type = rbool.SingleValue
SubSetR1: Type = rbool.SubSetR1
WholeR1: Type = rbool.Whole
extract_knots: Callable[[Any], Iterator[Any]] = rbool.extract_knots
from_any: Callable[[Any], object] = rbool.from_any
shift = rbool.move
scale = rbool.scale
unite = rbool.unite
