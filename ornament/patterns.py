import operator as ops
import re

from . import Pattern, MatchContext, MatchResult


class Regex(Pattern):
    def __init__(self, regex, /):
        self._regex = re.compile(regex)

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        if self._regex.fullmatch(value):
            return ctx.matches()
        else:
            return ctx.no_match()


class InstanceOf(Pattern):
    def __init__(self, *type_: type):
        self._type = type_

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match_if(isinstance(value, self._type))


class Between(Pattern):
    def __init__(self, lower, upper, *, lower_bound_exclusive=False, upper_bound_exclusive=False):
        self.lower = lower
        self.upper = upper
        self.op_lower = ops.gt if lower_bound_exclusive else ops.ge
        self.op_upper = ops.lt if upper_bound_exclusive else ops.le

    def match(self, value, *, ctx: MatchContext, strict=False) -> MatchResult:
        return ctx.match_if(self.op_lower(value, self.lower) and self.op_upper(value, self.upper))
