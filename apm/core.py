from __future__ import annotations

from copy import copy
from dataclasses import is_dataclass
from itertools import chain
from typing import Optional, List, Dict, Union, Tuple, Callable, Mapping

from .generic import AutoEqHash, AutoRepr


class WildcardMatch:
    def __init__(self, index):
        self.index = index
        self.value = None

    def set(self, value):
        self.value = value

    def get(self):
        return self.value


class MatchContext:
    def __init__(self, *, multimatch: bool, strict: bool):
        self.groups = {}
        self.wildcards: Dict[int, WildcardMatch] = {}
        self.multimatch = multimatch
        self.strict = strict
        self._off_the_record = []
        self._most_recent_record = {}
        self._match_stack = []

    def __setitem__(self, key, value):
        groups = self.groups
        if self._off_the_record:
            groups = self._off_the_record[-1]
        if self.multimatch:
            if key not in groups:
                groups[key] = []
            groups[key].append(value)
        else:
            groups[key] = value

    def __getitem__(self, item):
        return self.groups[item]

    def __contains__(self, item):
        return item in self.groups

    def keep(self):
        for k, v in self._most_recent_record.items():
            self[k] = v

    def _pop_most_recent_record(self):
        self._most_recent_record = self._off_the_record.pop()

    def match(self, value, pattern, strict=False, off_the_record=False) -> MatchResult:
        deferred: List[Callable] = []
        self._match_stack.append((value, pattern))
        deferred.append(lambda: self._match_stack.pop())
        if off_the_record:
            self._off_the_record.append({})
            deferred.append(self._pop_most_recent_record)

        try:
            strict = strict or self.strict

            if pattern is Ellipsis:
                return self.matches()

            if isinstance(pattern, Pattern):
                return pattern.match(value, ctx=self, strict=strict)

            if is_dataclass(value):
                if is_dataclass(pattern):
                    pattern_type = type(pattern)
                    pattern_dict = pattern.__dict__
                elif isinstance(pattern, Dataclass):
                    pattern_type = pattern.type
                    pattern_dict = pattern.dict
                else:
                    return self.no_match()

                if not issubclass(type(value), pattern_type):
                    return self.no_match()
                return _match_mapping(value.__dict__, pattern_dict, ctx=self, strict=strict)

            if type(pattern) == dict:
                return _match_mapping(value, pattern, ctx=self, strict=strict)

            if type(pattern) == tuple:
                if not isinstance(value, tuple) or strict and type(value) != tuple:
                    return self.no_match()
                return _match_sequence(value, pattern, ctx=self)

            if type(pattern) == list:
                if strict and type(value) != list:
                    return self.no_match()
                return _match_sequence(value, pattern, ctx=self)

            if type(pattern) == range:
                if strict and type(value) != range:
                    return self.no_match()
                return _match_sequence(value, pattern, ctx=self)

            if pattern == value:
                if strict:
                    return self.match_if(type(pattern) == type(value))
                return self.matches()

            return self.no_match()
        finally:
            for finalizer in deferred:
                finalizer()

    def matches(self) -> MatchResult:
        return MatchResult(matches=True, context=self, match_stack=copy(self._match_stack))

    def no_match(self) -> MatchResult:
        return MatchResult(matches=False, context=self, match_stack=copy(self._match_stack))

    def match_if(self, condition: bool) -> MatchResult:
        return MatchResult(matches=bool(condition), context=self, match_stack=copy(self._match_stack))

    def record(self, for_pattern, value):
        id_ = id(for_pattern)
        if id_ not in self.wildcards:
            self.wildcards[id_] = WildcardMatch(len(self.wildcards))
        self.wildcards[id_].set(value)

    def get_wildcard_matches(self) -> List:
        wildcard_matches: List = [None] * len(self.wildcards)

        for wildcard_match in self.wildcards.values():
            wildcard_matches[wildcard_match.index] = wildcard_match.get()
        return wildcard_matches


class MatchResult(Mapping):
    def __init__(self, *, matches: bool, context: MatchContext, match_stack: List[Tuple]):
        self._matches: bool = matches
        self._context: MatchContext = context
        self._match_stack: List[Tuple] = match_stack

    def __bool__(self):
        return self._matches

    def __getitem__(self, item):
        return self._context[item]

    def __getattr__(self, item):
        return self._context[item]

    def __contains__(self, item):
        return item in self._context

    def __repr__(self):
        return f"MatchResult(matches={self._matches}, groups={self._context.groups})"

    def __iter__(self):
        return iter(self._context.groups)

    def __len__(self):
        return len(self._context.groups)

    def items(self):
        return self._context.groups.items()

    def groups(self) -> Dict:
        return self._context.groups

    def wildcard_matches(self) -> List:
        return self._context.get_wildcard_matches()

    def bind(self, target) -> MatchResult:
        for k, v in self.items():
            target[k] = v
        return self

    def explain(self, *, short: bool = False) -> str:
        if self._matches:
            return "The pattern matches the given value."
        if not self._match_stack:
            return "Don't really know why this pattern did not match." \
                   " Please report an issue about this at https://github.com/scravy/awesome-pattern-matching/issues"
        reasons = []
        match_stack: List[Tuple] = self._match_stack
        if short:
            match_stack = [match_stack[-1]]
        for v, p in match_stack:
            reasons.append(f"{v}\n...did not match the pattern:\n{repr(p)}")
        return "\n...because:\n".join(reasons)


class Capturable:
    def __rshift__(self, other):
        return Capture(self, name=other)

    def __rmatmul__(self, other):
        return Capture(self, name=other)


class Nested:
    def descend(self, f):
        raise NotImplementedError


class Dataclass(Nested):
    def __init__(self, type_: type, dict_: dict):
        self.type = type_
        self.dict = dict_

    def descend(self, f):
        dict_ = {}
        for k, v in self.dict.items():
            dict_[k] = f(v)
        return Dataclass(self.type, dict_)


def transform(pattern, f):
    def rf(p):
        return transform(p, f)

    if is_dataclass(pattern):
        pattern = Dataclass(type(pattern), pattern.__dict__)

    if isinstance(pattern, Nested):
        return f(pattern.descend(rf))
    if isinstance(pattern, dict):
        kvs = {}
        for k, v in pattern.items():
            kvs[rf(k)] = rf(v)
        return f(kvs)
    if isinstance(pattern, tuple):
        return f(tuple(rf(i) for i in pattern))
    if isinstance(pattern, list):
        return f(list(rf(i) for i in pattern))
    return f(pattern)


class Pattern(Capturable, AutoEqHash, AutoRepr):
    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        raise NotImplementedError

    def __and__(self, other):
        return AllOf(self, other)

    def __or__(self, other):
        return OneOf(self, other)

    def __xor__(self, other):
        return Either(self, other)

    def __invert__(self):
        return Not(self)


class StringPattern:
    """Experimental"""

    def string_match(self, remaining, *, ctx: MatchContext) -> Optional[str]:
        raise NotImplementedError


class String(Pattern, Nested):
    """Experimental"""

    def __init__(self, *patterns):
        self._patterns = patterns

    @staticmethod
    def match_pattern(*, remaining, pattern, ctx: MatchContext) -> Optional[str]:
        captures = []
        if isinstance(pattern, Capture):
            captures, pattern = pattern.get_capture_pattern_chain()
        if isinstance(pattern, str):
            if remaining[:len(pattern)] == pattern:
                for capture in captures:
                    capture.capture(pattern, ctx=ctx)
                return pattern
        elif isinstance(pattern, StringPattern):
            result = pattern.string_match(remaining, ctx=ctx)
            if result is not None:
                for capture in captures:
                    capture.capture(result, ctx=ctx)
                return result
        return None

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        remaining = value
        for p in self._patterns:
            matched = self.match_pattern(remaining=remaining, pattern=p, ctx=ctx)
            if matched is not None:
                remaining = remaining[len(matched):]
            else:
                return ctx.no_match()
        return ctx.match_if(not remaining)

    def descend(self, f):
        return String(*(f(p) for p in self._patterns))


class Capture(Pattern, Nested):
    def __init__(self, pattern, *, name, target=None):
        self._pattern = pattern
        self._name = name
        self._target = target

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        result = ctx.match(value, self._pattern, strict=strict)
        if result:
            self.capture(value, ctx=ctx)
            return result
        return ctx.no_match()

    def capture(self, value, *, ctx: MatchContext):
        target = ctx if self._target is None else self._target
        target[self._name] = value

    def get_capture_pattern_chain(self) -> Tuple[List[Capture], Pattern]:
        patterns = [self]
        pattern = self._pattern
        while isinstance(pattern, Capture):
            patterns.append(pattern)
            pattern = pattern.pattern
        return patterns, pattern

    def descend(self, f):
        return Capture(pattern=f(self._pattern), name=self._name)

    @property
    def pattern(self):
        return self._pattern


class Many(Capturable, Nested, AutoEqHash, AutoRepr):
    def __init__(self, pattern, *,
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

    def __eq__(self, other):
        return type(self) == type(other) and self.__dict__ == other.__dict__

    def count_ok_wrt_at_most(self, count):
        if self.at_most:
            return count <= self.at_most
        return True

    def count_ok_wrt_at_least(self, count):
        if self.at_least:
            return count >= self.at_least
        return True

    def descend(self, f):
        return Many(pattern=f(self.pattern), at_least=self.at_least, at_most=self.at_most)


class Strict(Pattern, Nested):
    def __init__(self, pattern):
        self._pattern = pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        return ctx.match(value, self._pattern, strict=True)

    def descend(self, f):
        return Strict(pattern=f(self._pattern))


class Value(Pattern):
    def __init__(self, value):
        self._value = value

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        if strict:
            if type(self._value) != type(value):
                return ctx.no_match()
        return ctx.match_if(self._value == value)


class OneOf(Pattern, StringPattern, Nested):
    def __init__(self, *patterns):
        self._patterns = patterns

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        for pattern in self._patterns:
            result = ctx.match(value, pattern)
            if result:
                return result
        return ctx.no_match()

    def string_match(self, remaining, *, ctx: MatchContext) -> Optional[str]:
        for p in self._patterns:
            result = String.match_pattern(remaining=remaining, pattern=p, ctx=ctx)
            if result is not None:
                return result
        return None

    def descend(self, f):
        return OneOf(*(f(p) for p in self._patterns))


class AllOf(Pattern, Nested):
    def __init__(self, *patterns):
        self._patterns = patterns

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        for pattern in self._patterns:
            result = ctx.match(value, pattern)
            if not result:
                return result
        return ctx.matches()

    def descend(self, f):
        return AllOf(*(f(p) for p in self._patterns))


class Either(Pattern, Nested):
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        match_left = ctx.match(value, self._left, strict=strict)
        match_right = ctx.match(value, self._right, strict=strict)
        return ctx.match_if(bool(match_left) != bool(match_right))

    def descend(self, f):
        return Either(f(self._left), f(self._right))


class Not(Pattern, Nested):
    def __init__(self, pattern):
        self._pattern = pattern

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        if ctx.match(value, self._pattern, strict=False):
            return ctx.no_match()
        return ctx.matches()

    def descend(self, f):
        return Not(pattern=f(self._pattern))


def _match_mapping(value, pattern: dict, *, ctx: MatchContext, strict: bool) -> MatchResult:
    to_be_matched = {}
    try:
        items = value.items()
    except (AttributeError, TypeError):
        return ctx.no_match()
    for key, val in items:
        to_be_matched[key] = val
    patterns = []
    for key, val_pattern in pattern.items():
        if isinstance(key, Pattern):
            patterns.append((key, val_pattern))
            continue
        try:
            val = to_be_matched[key]
        except KeyError:
            return ctx.no_match()
        result = ctx.match(val, val_pattern)
        if not result:
            return result
        del to_be_matched[key]
    possibly_mismatching_keys = set()
    for key_pattern, val_pattern in patterns:
        keys_to_remove = []
        for key, val in to_be_matched.items():
            if ctx.match(key, key_pattern):
                if ctx.match(val, val_pattern):
                    keys_to_remove.append(key)
                    if key in possibly_mismatching_keys:
                        possibly_mismatching_keys.remove(key)
                else:
                    if isinstance(key_pattern, Capture):
                        _, p = key_pattern.get_capture_pattern_chain()
                    else:
                        p = key_pattern
                    if not isinstance(p, Underscore):
                        possibly_mismatching_keys.add(key)
        for key in keys_to_remove:
            del to_be_matched[key]
    return ctx.match_if(not possibly_mismatching_keys and (not strict or not to_be_matched))


def _match_sequence(value, pattern: Union[tuple, list], *, ctx: MatchContext) -> MatchResult:
    try:
        it = iter(value)
    except TypeError:
        return ctx.no_match()
    item_queued = False
    for current_pattern, next_pattern in zip(pattern, chain(pattern[1:], [Not(...)])):
        captures: List[Capture] = []
        if isinstance(current_pattern, Capture):
            ps, p = current_pattern.get_capture_pattern_chain()
            if isinstance(p, Many):
                current_pattern = p
                captures = ps
        if isinstance(current_pattern, Many):
            count = 0
            result_value = []
            while current_pattern.count_ok_wrt_at_most(count + 1):
                try:
                    item = next(it)
                except StopIteration:
                    break
                if ctx.match(item, next_pattern, off_the_record=True):
                    item_queued = True
                    break
                if not ctx.match(item, current_pattern.pattern, off_the_record=True):
                    item_queued = True
                    break
                ctx.keep()
                if captures:
                    result_value.append(item)
                count += 1
            if not current_pattern.count_ok_wrt_at_least(count):
                return ctx.no_match()
            for capture in captures:
                capture.capture(result_value, ctx=ctx)
            continue
        try:
            if item_queued:
                item_queued = False
            else:
                item = next(it)
        except StopIteration:
            return ctx.no_match()
        # noinspection PyUnboundLocalVariable
        result = ctx.match(item, current_pattern)
        if not result:
            return result
    try:
        next(it)
        return ctx.no_match()
    except StopIteration:
        return ctx.match_if(not item_queued)


class Underscore(Pattern):
    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        ctx.record(self, value)
        return ctx.matches()


_ = Underscore()
