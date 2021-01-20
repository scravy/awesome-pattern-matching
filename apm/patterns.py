import decimal
import operator as ops
import re
from typing import Callable, Optional, Dict, Any

from ._util import get_arg_types, get_return_type, get_kwarg_types
from .core import Pattern, MatchContext, MatchResult, StringPattern, OneOf, Nested, Underscore


class Check(Pattern):
    def __init__(self, condition):
        self._condition = condition

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match_if(self._condition(value))


class Regex(Pattern, StringPattern):
    def __init__(self, regex, *, bind_groups: bool = True, capture_wildcards: bool = False):
        self._regex: re.Pattern = re.compile(regex)
        self._bind_groups = bind_groups
        if capture_wildcards:
            self._wildcards = tuple(Underscore() for _i in range(0, self._regex.groups))
        else:
            self._wildcards = tuple([])

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        try:
            result = self._regex.fullmatch(value)
        except TypeError:
            return ctx.no_match()
        if not result:
            return ctx.no_match()
        if self._bind_groups:
            for k, v in result.groupdict().items():
                ctx[k] = v
        for ix, wc in enumerate(self._wildcards):
            ctx.record(wc, result.group(ix + 1))
        return ctx.matches()

    def string_match(self, remaining, *, ctx: MatchContext) -> Optional[str]:
        result = self._regex.match(remaining)
        if not result:
            return None
        if self._bind_groups:
            for k, v in result.groupdict().items():
                ctx[k] = v
        return result.group(0)


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
    def __init__(self, *, exactly: int = None, at_least: int = None, at_most: int = None):
        if exactly is not None:
            if at_least is not None or at_most is not None:
                raise ValueError("If length is given, 'at_least' or 'at_most' must not be given.")
            self._at_least = exactly
            self._at_most = exactly
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


class Transformed(Pattern, Nested):
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

    def descend(self, f):
        return Transformed(f=self._f, pattern=f(self._pattern))


class Arguments(Pattern, Nested):
    def __init__(self, *arg_patterns, **kwargs):
        self._pattern = list(arg_patterns)
        self._kwargs: Dict[str, Any] = kwargs

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        if not callable(value):
            return ctx.no_match()
        if self._pattern:
            result = ctx.match(get_arg_types(value), self._pattern)
            if not result:
                return result
        return ctx.match(get_kwarg_types(value), self._kwargs, strict)

    def descend(self, f):
        t_pattern = list(f(p) for p in self._pattern)
        t_kwargs = {}
        for k, v in self._kwargs.items():
            t_kwargs[k] = f(v)
        return Arguments(*t_pattern, **t_kwargs)


class Returns(Pattern, Nested):
    def __init__(self, pattern):
        self._pattern = pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        if not callable(value):
            return ctx.no_match()
        return ctx.match(get_return_type(value), self._pattern)

    def descend(self, f):
        return Returns(pattern=f(self._pattern))


class Each(Pattern, Nested):
    def __init__(self, pattern, *, at_least: int = 0):
        self._pattern = pattern
        self._at_least = at_least

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        count = 0
        try:
            it = iter(value)
        except TypeError:
            return ctx.no_match()
        for item in it:
            result = ctx.match(item, self._pattern)
            if not result:
                return result
            count += 1
        return ctx.match_if(count >= self._at_least)

    def descend(self, f):
        return Each(pattern=f(self._pattern), at_least=self._at_least)


class EachItem(Pattern, Nested):
    def __init__(self, key_pattern, value_pattern):
        self._key_pattern = key_pattern
        self._value_pattern = value_pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        try:
            items = value.items()
        except AttributeError:
            return ctx.no_match()
        for k, v in items:
            result = ctx.match(k, self._key_pattern)
            if not result:
                return result
            result = ctx.match(v, self._value_pattern)
            if not result:
                return result
        return ctx.matches()

    def descend(self, f):
        return EachItem(key_pattern=f(self._key_pattern), value_pattern=f(self._value_pattern))


class At(Pattern, Nested):
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
            except (TypeError, KeyError):
                return ctx.no_match()
        return ctx.match(value, self._pattern)

    def descend(self, f):
        return At(path=self._path, pattern=f(self._pattern))


class Items(Pattern, Nested):
    def __init__(self, **kwargs):
        self._items = kwargs

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match(value, self._items, strict=strict)

    def descend(self, f):
        items = {}
        for k, v in self._items.items():
            items[k] = f(v)
        return Items(**items)


class Attrs(Pattern, Nested):
    def __init__(self, **kwargs):
        self._items = kwargs

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        try:
            attrs = value.__dict__
        except AttributeError:
            return ctx.no_match()
        return ctx.match(attrs, self._items, strict=strict)

    def descend(self, f):
        items = {}
        for k, v in self._items.items():
            items[k] = f(v)
        return Attrs(**items)


# noinspection PyPep8Naming
def NoneOf(*args) -> Pattern:
    return ~OneOf(args)


# noinspection PyPep8Naming
def Maybe(pattern) -> Pattern:
    return OneOf(pattern, ...)


IsTruish = Check(lambda x: bool(x))
IsNumber = (InstanceOf(int) & ~InstanceOf(bool)) | InstanceOf(float) | InstanceOf(decimal.Decimal)
IsString = InstanceOf(str)
