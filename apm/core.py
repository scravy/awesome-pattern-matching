from __future__ import annotations

import re
from itertools import chain
from typing import Optional


class MatchContext:
    def __init__(self):
        self.groups = {}

    def __setitem__(self, key, value):
        self.groups[key] = value

    def __getitem__(self, item):
        return self.groups[item]

    def __contains__(self, item):
        return item in self.groups

    def match(self, value, pattern, strict=False) -> MatchResult:
        return _match(value, pattern, ctx=self, strict=strict)

    def matches(self) -> MatchResult:
        return MatchResult(matches=True, context=self)

    def no_match(self) -> MatchResult:
        return MatchResult(matches=False, context=self)

    def match_if(self, condition: bool) -> MatchResult:
        return MatchResult(matches=bool(condition), context=self)


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

    def __iter__(self):
        return iter(self._context.groups)

    def items(self):
        return self._context.groups.items()


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
    def __init__(self, pattern, /, *, name):
        self._pattern = pattern
        self._name = name

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        if result := ctx.match(value, self._pattern):
            ctx[self._name] = value
            return result
        return ctx.no_match()

    @property
    def pattern(self):
        return self._pattern

    @property
    def name(self):
        return self._name


class Some:
    def __init__(self, pattern, /, *,
                 at_least: Optional[int] = None,
                 at_most: Optional[int] = None,
                 exactly: Optional[int] = None):

        if at_most and at_least and at_most < at_least:
            raise ValueError(f"conflicting spec: at_most={at_most} < at_least={at_least}")
        if exactly and at_most:
            raise ValueError(f"conflicting spec: exactly and at_most set at the same_time")
        if exactly and at_least:
            raise ValueError(f"conflicting spec: exactly and at_least set at the same_time")
        if exactly:
            at_least = exactly
            at_most = exactly

        self.pattern = pattern
        self.at_least: Optional[int] = at_least
        self.at_most: Optional[int] = at_most

    def count_ok_wrt_at_most(self, count):
        if self.at_most:
            return count <= self.at_most
        return True

    def count_ok_wrt_at_least(self, count):
        if self.at_least:
            return count >= self.at_least
        return True


class Remaining(Some):
    pass


class Strict(Pattern):
    def __init__(self, pattern, /):
        self._pattern = pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match(value, self._pattern, strict=True)


class OneOf(Pattern):
    def __init__(self, *patterns):
        self._patterns = patterns

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        for pattern in self._patterns:
            if result := ctx.match(value, pattern):
                return result
        return ctx.no_match()


class AllOf(Pattern):
    def __init__(self, *patterns):
        self._patterns = patterns

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        for pattern in self._patterns:
            if not (result := ctx.match(value, pattern)):
                return result
        return ctx.matches()


class Either(Pattern):
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        match_left = ctx.match(value, self._left, strict=strict)
        match_right = ctx.match(value, self._right, strict=strict)
        return ctx.match_if(bool(match_left) != bool(match_right))


class Not(Pattern):
    def __init__(self, pattern, /):
        self._pattern = pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        if ctx.match(value, self._pattern, strict=False):
            return ctx.no_match()
        return ctx.matches()


def _match_dict(value, pattern, *, ctx: MatchContext, strict: bool) -> MatchResult:
    try:
        items = value.items()
    except (AttributeError, TypeError):
        return ctx.no_match()
    matched_keys = set()
    for key, value in items:
        if key in pattern:
            if not (result := ctx.match(value, pattern[key])):
                return result
            matched_keys.add(key)
        else:
            if strict:
                return ctx.no_match()
    for key in pattern:
        if key not in matched_keys:
            return ctx.no_match()
    return ctx.matches()


def _match_tuple(value, pattern, *, ctx: MatchContext, strict: bool) -> MatchResult:
    if strict and type(value) != tuple:
        return ctx.no_match()
    if not isinstance(value, tuple) or len(pattern) != len(value):
        return ctx.no_match()
    for p, v in zip(pattern, value):
        if not (result := ctx.match(v, p)):
            return result
    return ctx.matches()


def _match_list(value, pattern, *, ctx: MatchContext, strict: bool) -> MatchResult:
    if strict and type(value) != list:
        return ctx.no_match()
    try:
        it = iter(value)
    except TypeError:
        return ctx.no_match()
    item_queued = False
    for current_pattern, next_pattern in zip(pattern, chain(pattern[1:], [Not(...)])):
        name = None
        if isinstance(current_pattern, Capture) and isinstance(current_pattern.pattern, Some):
            name = current_pattern.name
            current_pattern = current_pattern.pattern
        if isinstance(current_pattern, Some):
            count = 0
            result_value = []
            while current_pattern.count_ok_wrt_at_most(count + 1):
                try:
                    if item_queued:
                        item_queued = False
                    else:
                        item = next(it)
                except StopIteration:
                    break
                # noinspection PyUnboundLocalVariable
                if ctx.match(item, next_pattern):
                    item_queued = True
                    break
                # noinspection PyUnboundLocalVariable
                if not ctx.match(item, current_pattern.pattern):
                    item_queued = True
                    break
                if name:
                    result_value.append(item)
                count += 1
            if not current_pattern.count_ok_wrt_at_least(count):
                return ctx.no_match()
            if name:
                ctx[name] = result_value
            continue
        try:
            if item_queued:
                item_queued = False
            else:
                item = next(it)
        except StopIteration:
            return ctx.no_match()
        if not (result := ctx.match(item, current_pattern)):
            return result
    try:
        next(it)
        return ctx.no_match()
    except StopIteration:
        return ctx.match_if(not item_queued)


def _match(value, pattern, *, ctx: MatchContext, strict: bool = False) -> MatchResult:
    if pattern == value:
        if strict:
            return ctx.match_if(type(pattern) == type(value))
        return ctx.matches()

    if pattern is Ellipsis:
        return ctx.matches()

    if isinstance(pattern, Pattern):
        return pattern.match(value, ctx=ctx, strict=strict)

    if isinstance(pattern, dict):
        return _match_dict(value, pattern, ctx=ctx, strict=strict)

    if isinstance(pattern, tuple):
        return _match_tuple(value, pattern, ctx=ctx, strict=strict)

    if isinstance(pattern, list):
        return _match_list(value, pattern, ctx=ctx, strict=strict)

    return ctx.no_match()


def match(value, pattern) -> MatchResult:
    return _match(value, pattern, ctx=MatchContext())
