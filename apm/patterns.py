import operator as ops
import re
from typing import Callable, Optional

from ._util import get_arg_types, get_return_type
from .core import Pattern, MatchContext, MatchResult, StringPattern


class Check(Pattern):
    def __init__(self, condition, /):
        self._condition = condition

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match_if(self._condition(value))


class Regex(Pattern, StringPattern):
    def __init__(self, regex, /):
        self._regex: re.Pattern = re.compile(regex)

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        if self._regex.fullmatch(value):
            return ctx.matches()
        else:
            return ctx.no_match()

    def string_match(self, remaining, *, ctx: MatchContext) -> Optional[str]:
        if result := self._regex.match(remaining):
            return result.group(0)
        return None

    @property
    def regex(self) -> re.Pattern:
        return self._regex


class InstanceOf(Pattern):
    def __init__(self, *type_: type):
        self._type = type_

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match_if(isinstance(value, self._type))


class SubclassOf(Pattern):
    def __init__(self, *type_: type):
        self._type = type_

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match_if(issubclass(value, self._type))


class Between(Pattern):
    def __init__(self, lower, upper, *, lower_bound_exclusive=False, upper_bound_exclusive=False):
        self.lower = lower
        self.upper = upper
        self.op_lower = ops.gt if lower_bound_exclusive else ops.ge
        self.op_upper = ops.lt if upper_bound_exclusive else ops.le

    def match(self, value, *, ctx: MatchContext, strict=False) -> MatchResult:
        return ctx.match_if(self.op_lower(value, self.lower) and self.op_upper(value, self.upper))


class Length(Pattern):
    def __init__(self, length, /):
        self._length = length

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match_if(len(value) == self._length)


class Truish(Pattern):
    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match_if(value)


class Contains(Pattern):
    def __init__(self, needle):
        self._needle = needle

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match_if(self._needle in value)


class Transformed(Pattern):
    def __init__(self, f: Callable, pattern, /):
        self._f = f
        self._pattern = pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match(self._f(value), self._pattern)


class Arguments(Pattern):
    def __init__(self, *arg_patterns):
        self._pattern = list(arg_patterns)

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match(get_arg_types(value), self._pattern)


class Returns(Pattern):
    def __init__(self, pattern, /):
        self._pattern = pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match(get_return_type(value), self._pattern)


class Each(Pattern):
    def __init__(self, pattern, /, *, at_least: int = 0):
        self._pattern = pattern
        self._at_least = at_least

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        count = 0
        for item in value:
            if not (result := ctx.match(item, self._pattern)):
                return result
            count += 1
        return ctx.match_if(count >= self._at_least)


class EachItem(Pattern):
    def __init__(self, key_pattern, value_pattern, /):
        self._key_pattern = key_pattern
        self._value_pattern = value_pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        for k, v in value.items():
            if not (result := ctx.match(k, self._key_pattern)):
                return result
            if not (result := ctx.match(v, self._value_pattern)):
                return result
        return ctx.matches()


class At(Pattern):
    def __init__(self, path, pattern, /):
        if isinstance(path, str):
            self._path = path.split(".")
        else:
            self._path = list(path)
        self._pattern = pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        for k in self._path:
            try:
                value = value[k]
            except KeyError:
                return ctx.no_match()
        return ctx.match(value, self._pattern)
