from __future__ import annotations


class MatchContext:
    def __init__(self):
        self.groups = {}

    def __setitem__(self, key, value):
        self.groups[key] = value

    def __getitem__(self, item):
        return self.groups[item]

    def __contains__(self, item):
        return item in self.groups

    def matches(self) -> MatchResult:
        return MatchResult(matches=True, context=self)

    def no_match(self) -> MatchResult:
        return MatchResult(matches=False, context=self)

    def match_if(self, condition: bool) -> MatchResult:
        return MatchResult(matches=condition, context=self)


class MatchResult:
    def __init__(self, *, matches: bool, context: MatchContext):
        self._matches: bool = matches
        self._context: MatchContext = context

    def __bool__(self):
        return self._matches

    def __getitem__(self, item):
        return self._context[item]

    def __contains__(self, item):
        return item in self._context

    def __repr__(self):
        return f"MatchResult(matches={self._matches}, groups={self._context.groups})"


class Pattern:
    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        raise NotImplementedError()

    def __and__(self, other):
        return AllOf(self, other)

    def __or__(self, other):
        return OneOf(self, other)

    def __xor__(self, other):
        return Either(self, other)

    def __invert__(self):
        return Not(self)


class Capture(Pattern):
    def __init__(self, pattern, /, *, name: str):
        self._pattern = pattern
        self._name: str = name

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        if result := _match(value, self._pattern, ctx=ctx):
            ctx[self._name] = value
            return result
        return ctx.no_match()

    @property
    def pattern(self):
        if isinstance(self._pattern, Remaining):
            return self._pattern.pattern
        return self._pattern

    @property
    def name(self):
        return self._name

    @property
    def at_least(self):
        return self._pattern.at_least


class RemainingMeta(type):

    def __instancecheck__(self, instance):
        if isinstance(instance, Capture):
            # noinspection PyProtectedMember
            if isinstance(instance._pattern, Remaining):
                return True
        return issubclass(type(instance), Remaining)


class Remaining(metaclass=RemainingMeta):
    def __init__(self, pattern, /, *, at_least: int = 0):
        self.pattern = pattern
        self.at_least = at_least
        self.name = ""

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return _match(value, self.pattern, ctx=ctx, strict=strict)


class Each(Pattern):
    def __init__(self, pattern, /, *, at_least: int = 0):
        self._pattern = pattern
        self._at_least = at_least

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        count = 0
        for item in value:
            if not (result := _match(item, self._pattern, ctx=ctx)):
                return result
            count += 1
        return ctx.match_if(count >= self._at_least)


class Strict(Pattern):
    def __init__(self, pattern, /):
        self._pattern = pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return _match(value, self._pattern, ctx=ctx, strict=True)


class OneOf(Pattern):
    def __init__(self, *patterns):
        self._patterns = patterns

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        for pattern in self._patterns:
            if result := _match(value, pattern, ctx=ctx):
                return result
        return ctx.no_match()


class AllOf(Pattern):
    def __init__(self, *patterns):
        self._patterns = patterns

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        for pattern in self._patterns:
            if not (result := _match(value, pattern, ctx=ctx)):
                return result
        return ctx.matches()


class Either(Pattern):
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        match_left = _match(value, self._left, ctx=ctx, strict=strict)
        match_right = _match(value, self._right, ctx=ctx, strict=strict)
        return ctx.match_if(bool(match_left) != bool(match_right))


class Not(Pattern):
    def __init__(self, pattern, /):
        self._pattern = pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        if _match(value, self._pattern, ctx=ctx, strict=False):
            return ctx.no_match()
        return ctx.matches()


def _match(value, pattern, *, ctx: MatchContext, strict: bool = False) -> MatchResult:
    if pattern == value:
        return ctx.matches()

    if pattern is Ellipsis:
        return ctx.matches()

    if isinstance(pattern, Pattern):
        return pattern.match(value, ctx=ctx, strict=strict)

    if isinstance(pattern, dict):
        try:
            items = value.items()
        except (AttributeError, TypeError):
            return ctx.no_match()
        matched_keys = set()
        for key, value in items:
            if key in pattern:
                if not (result := _match(value, pattern[key], ctx=ctx)):
                    return result
                matched_keys.add(key)
            else:
                if strict:
                    return ctx.no_match()
        for key in pattern:
            if key not in matched_keys:
                return ctx.no_match()
        return ctx.matches()

    if isinstance(pattern, list):
        if pattern and isinstance(pattern[-1], Remaining):
            remaining: Remaining = pattern[-1]
            it = iter(value)
            for p in pattern[:-1]:
                try:
                    v = next(it)
                except StopIteration:
                    return ctx.no_match()
                if not (result := _match(v, p, ctx=ctx)):
                    return result
            count = 0
            result_value = []
            for v in it:
                count += 1
                if not (result := _match(v, remaining.pattern, ctx=ctx)):
                    return result
                if remaining.name:
                    result_value.append(v)
            if remaining.name:
                ctx[remaining.name] = result_value
            return ctx.match_if(count >= remaining.at_least)
        count = 0
        for p, v in zip(pattern, value):
            count += 1
            if not (result := _match(v, p, ctx=ctx)):
                return result
        return ctx.match_if(count == len(pattern))

    return ctx.no_match()


def match(value, pattern) -> MatchResult:
    return _match(value, pattern, ctx=MatchContext())
