import decimal
import operator as ops
import re
from typing import Callable, Optional, Dict, Any

from ._util import get_arg_types, get_return_type, get_kwarg_types
from .core import Pattern, MatchContext, MatchResult, StringPattern, OneOf


class Check(Pattern):
    def __init__(self, condition):
        self._condition = condition

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match_if(self._condition(value))


class Regex(Pattern, StringPattern):
    def __init__(self, regex):
        self._regex: re.Pattern = re.compile(regex)

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match_if(bool(self._regex.fullmatch(value)))

    def string_match(self, remaining, *, ctx: MatchContext) -> Optional[str]:
        result = self._regex.match(remaining)
        if result:
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
    def __init__(self, length=None, at_least: int = None, at_most: int = None):
        if length is not None:
            if at_least is not None or at_most is not None:
                raise ValueError("If length is given, 'at_least' or 'at_most' must not be given.")
            self._at_least = length
            self._at_most = length
        else:
            self._at_least = at_least
            self._at_most = at_most

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        length = len(value)
        return ctx.match_if((self._at_least is None or length >= self._at_least)
                            and (self._at_most is None or length <= self._at_most))


class Contains(Pattern):
    def __init__(self, needle):
        self._needle = needle

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match_if(self._needle in value)


class Transformed(Pattern):
    def __init__(self, f: Callable, pattern):
        self._f = f
        self._pattern = pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        # noinspection PyBroadException
        try:
            transformed = self._f(value)
        except Exception:
            return ctx.no_match()
        return ctx.match(transformed, self._pattern)


class Arguments(Pattern):
    def __init__(self, *arg_patterns, **kwargs):
        self._pattern = list(arg_patterns)
        self._kwargs: Dict[str, Any] = kwargs

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        if self._pattern:
            result = ctx.match(get_arg_types(value), self._pattern)
            if not result:
                return result
        return ctx.match(get_kwarg_types(value), self._kwargs, strict)


class Returns(Pattern):
    def __init__(self, pattern):
        self._pattern = pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match(get_return_type(value), self._pattern)


class Each(Pattern):
    def __init__(self, pattern, *, at_least: int = 0):
        self._pattern = pattern
        self._at_least = at_least

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        count = 0
        for item in value:
            result = ctx.match(item, self._pattern)
            if not result:
                return result
            count += 1
        return ctx.match_if(count >= self._at_least)


class EachItem(Pattern):
    def __init__(self, key_pattern, value_pattern):
        self._key_pattern = key_pattern
        self._value_pattern = value_pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        for k, v in value.items():
            result = ctx.match(k, self._key_pattern)
            if not result:
                return result
            result = ctx.match(v, self._value_pattern)
            if not result:
                return result
        return ctx.matches()


class At(Pattern):
    def __init__(self, path, pattern):
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


class Object(Pattern):
    def __init__(self, **kwargs):
        self._items = kwargs

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match(value, self._items, strict=strict)


class _IsTruish(Pattern):
    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match_if(value)


IsTruish = _IsTruish()


# noinspection PyPep8Naming
def NoneOf(*args) -> Pattern:
    return ~OneOf(args)


# noinspection PyPep8Naming
def Maybe(pattern) -> Pattern:
    return OneOf(pattern, ...)


IsNumber = (InstanceOf(int) & ~InstanceOf(bool)) | InstanceOf(float) | InstanceOf(decimal.Decimal)
IsString = InstanceOf(str)
