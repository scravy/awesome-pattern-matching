from __future__ import annotations

import collections.abc as abc
import dataclasses
from abc import abstractmethod, ABC
from copy import copy
from dataclasses import is_dataclass
from itertools import chain
from typing import Optional, List, Dict, Union, Tuple, Callable, Generic, TypeVar, Hashable, Iterable, Type

from ._util import SeqIterator, call
from .generic import AutoEqHash, AutoRepr
from .no_value import NoValue


def apply(func, result: MatchResult):
    return call(func, *result.wildcard_matches(), **result.groups())


class WildcardMatch:
    def __init__(self, index):
        self.index = index
        self.value = None

    def set(self, value):
        self.value = value

    def get(self):
        return self.value


@dataclasses.dataclass(frozen=True)
class MatchContextProperties:
    multimatch: bool
    strict: bool


class MatchContext:
    def __init__(self, *, multimatch: bool = False, strict: bool = False, _copy_from: Optional[MatchContext] = None):
        if _copy_from is None:
            self.groups = {}
            self.wildcards: Dict[int, WildcardMatch] = {}
            self.properties = MatchContextProperties(
                multimatch=multimatch,
                strict=strict,
            )
            self._match_stack = []
        else:
            self.groups = {**_copy_from.groups}
            self.wildcards = {**_copy_from.wildcards}
            self.properties = _copy_from.properties
            self._match_stack = [*_copy_from._match_stack]

    def __setitem__(self, key, value):
        groups = self.groups
        if self.properties.multimatch:
            if key not in groups:
                groups[key] = []
            groups[key].append(value)
        else:
            groups[key] = value

    def __getitem__(self, item):
        return self.groups[item]

    def __contains__(self, item):
        return item in self.groups

    def match(self, value, pattern, strict=False) -> MatchResult:
        deferred: List[Callable] = []
        self._match_stack.append((value, pattern))
        deferred.append(lambda: self._match_stack.pop())

        try:
            strict = strict or self.properties.strict

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

            if type(pattern) in (dict, Remainder):
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

    def fork(self) -> MatchContext:
        return MatchContext(_copy_from=self)

    def merge(self, other: MatchContext):
        assert self.properties is other.properties
        self.groups.update(other.groups)
        self.wildcards.update(other.wildcards)
        self._match_stack = [*other._match_stack]


class MatchResult(abc.Mapping):
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

    def get(self, key, default=None):
        return self._context.groups.get(key, default)

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
    def __capture(self, other: Union[str, Aggregation]):
        if isinstance(other, Aggregation):
            return Capture(self, name=other.name, agg=other)
        return Capture(self, name=other)

    def __rshift__(self, other: Union[str, Aggregation]):
        return self.__capture(other)

    def __rmatmul__(self, other: Union[str, Aggregation]):
        return self.__capture(other)


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

    if is_dataclass(pattern) and not isinstance(pattern, type):
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


T = TypeVar('T')


class Aggregation(Generic[T], ABC):
    def __init__(self, name: Optional[str] = None):
        self._name = name
        self._value = NoValue

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def value(self):
        if self._value is NoValue:
            return self.new()
        return self._value

    @abstractmethod
    def new(self) -> T:
        raise NotImplementedError

    @abstractmethod
    def _add(self, aggregate: T, value) -> T:
        raise NotImplementedError

    def add(self, aggregate: T, value) -> T:
        self._value = self._add(aggregate, value)
        return self._value


class Capture(Pattern, Nested):
    def __init__(self, pattern, *, name: Hashable, target=None, agg: Optional[Aggregation] = None):
        self._pattern = pattern
        self._name: Hashable = name
        self._target = target
        self._aggregation: Aggregation = agg

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        result = ctx.match(value, self._pattern, strict=strict)
        if result:
            self.capture(value, ctx=ctx)
            return result
        return ctx.no_match()

    def capture(self, value, *, ctx: MatchContext):
        target = ctx if self._target is None else self._target
        if self._aggregation:
            if self._name not in target:
                target[self._name] = self._aggregation.new()
            target[self._name] = self._aggregation.add(target[self._name], value)
        else:
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


class SomePatternCompatibilityArgumentsError(ValueError):
    """
    v0.23.0 introduced the capability for Some() to match subsequences. Previously it would only match individual items.
    As a consequence the pattern-argument became an *args. For backwards compatibility one can still specify pattern=
    when constructing a Some(pattern=...). If there are patterns given via *args as well as via keyword pattern= this
    exception is raised.

    See also https://github.com/scravy/awesome-pattern-matching/issues/8
    """

    def __init__(self):
        super().__init__('Both kwargs-style "patterns" as well as old-style "pattern" specified.')


class Some(Capturable, Nested, AutoEqHash, AutoRepr):
    """
    Matches subsequences in a sequence, also known by the names Many and Remaining. Can only be used within sequences
    (tuples, list, ranges, ...).

    Some can roughly be thought of as Quantification in most regular expression engines:
    - `0(12)*3` is like `[0, Some(1, 2), 3]`
    - `0(12)+3` is like `[0, Some(1, 2, at_least=1), 3]`
    - `01*2` is like `[0, Some(1), 2]`

    When invoked with no arguments is the same as `Some(...)` (like `.*` in regex).

    Examples:
        >>> match([0, 1, 2, 1, 2, 3], [0, Some(1, 2), 3]))
        MatchResult(matches=True, groups={})

        >>> match(range(0, 10), ['123' @ Many(Between(0, 3)), 'xs' @ Remaining()])
        MatchResult(matches=True, groups={'123': [0, 1, 2, 3], 'xs': [4, 5, 6, 7, 8, 9]})


    Args:
        at_least (int, optional): No default, which is effectively a default of zero.
        at_most (int, optional): No default.
        exactly (int, optional): No default.
        greedy (bool): Whether the match should be greedy. Default: False. This is not the same notion of greediness
            as in most regular expression engines – it is more greedy than that. The default behavior of Some() is that
            it will stop looking for matches if it can match the pattern following the Some(). Enabling greediness will
            make it go on as long as the current pattern matches.
    """

    def __init__(self, *patterns,
                 pattern=None,  # for backwards compatibility, see docstring of SomePatternCompatibilityArgumentsError
                 at_least: Optional[int] = None,
                 at_most: Optional[int] = None,
                 exactly: Optional[int] = None,
                 greedy: bool = False):

        if pattern is not None:
            if patterns:
                raise SomePatternCompatibilityArgumentsError
            patterns = [pattern]
        if not patterns:
            patterns = (...,)
        if at_most and at_least and at_most < at_least:
            raise ValueError(f"conflicting spec: at_most={at_most} < at_least={at_least}")
        if exactly and at_most:
            raise ValueError(f"conflicting spec: exactly and at_most set at the same_time")
        if exactly and at_least:
            raise ValueError(f"conflicting spec: exactly and at_least set at the same_time")
        if exactly:
            at_least = exactly
            at_most = exactly

        self.patterns = patterns
        self.at_least: Optional[int] = at_least
        self.at_most: Optional[int] = at_most
        self.greedy = greedy

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
        return Some(*(f(p) for p in self.patterns), at_least=self.at_least, at_most=self.at_most)


class Remainder(Nested, AutoEqHash, AutoRepr):
    def __init__(self, pattern):
        self.pattern = pattern
        self.left = NoValue

    def descend(self, f):
        r = Remainder(f(self.pattern))
        r.left = f(self.left)
        return r

    def __rpow__(self, left):
        self.left = left
        return self


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


def _is_a(pattern, type_) -> bool:
    if isinstance(pattern, type_):
        return True
    if isinstance(pattern, Capture):
        _, p = pattern.get_capture_pattern_chain()
        if isinstance(p, type_):
            return True
    return False


def _get_as(pattern, type_: Type[T]) -> T:
    if isinstance(pattern, type_):
        return pattern
    if isinstance(pattern, Capture):
        _, p = pattern.get_capture_pattern_chain()
        if isinstance(p, type_):
            return p
    assert False, f'requested {type_}, but pattern is of type {type(pattern)}'


def _get_captures(pattern) -> List[Capture]:
    if isinstance(pattern, Capture):
        ps, _ = pattern.get_capture_pattern_chain()
        return ps
    return []


def _match_mapping(value, pattern: Union[dict, Remainder], *, ctx: MatchContext, strict: bool) -> MatchResult:
    remainder = NoValue
    if isinstance(pattern, Remainder):
        remainder = pattern
        pattern = pattern.left
    to_be_matched = {}
    matched = set()
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
        matched.add(key)
        del to_be_matched[key]
    possibly_mismatching_keys = set()
    for key_pattern, val_pattern in patterns:
        keys_to_remove = []
        if _is_a(key_pattern, Underscore):
            matches = False
            for key, val in to_be_matched.items():
                if ctx.match(key, key_pattern):
                    if ctx.match(val, val_pattern):
                        matches = True
                        keys_to_remove.append(key)
                        if key in possibly_mismatching_keys:
                            possibly_mismatching_keys.remove(key)
                        break
            if not matches:
                return ctx.no_match()
        else:
            for key, val in to_be_matched.items():
                if ctx.match(key, key_pattern):
                    if ctx.match(val, val_pattern):
                        keys_to_remove.append(key)
                        if key in possibly_mismatching_keys:
                            possibly_mismatching_keys.remove(key)
                    else:
                        possibly_mismatching_keys.add(key)
        for key in keys_to_remove:
            matched.add(key)
            del to_be_matched[key]
    if possibly_mismatching_keys or (strict and to_be_matched):
        return ctx.no_match()
    if remainder is not NoValue:
        remaining = {k: v for k, v in items if k not in matched}
        if not ctx.match(remaining, remainder.pattern, strict=strict):
            return ctx.no_match()
    return ctx.matches()


@dataclasses.dataclass
class MatchSomeResult:
    it: SeqIterator
    ctx: MatchContext
    matches: List

    def merge(self, it: SeqIterator, ctx: MatchContext):
        it.merge(self.it)
        ctx.merge(self.ctx)


def _match_some(it: SeqIterator, current_pattern, *,
                terminators: List, ctx: MatchContext) -> Optional[MatchSomeResult]:
    forked_it = it.fork()
    forked_ctx = ctx.fork()
    result = _match_subsequence(forked_it, current_pattern, terminators, ctx=forked_ctx)
    if result is not None:
        return MatchSomeResult(forked_it, forked_ctx, result)


def _match_subsequence(it: SeqIterator, pattern, terminators: List,
                       *, ctx: MatchContext) -> Optional[List]:
    count: int = 0
    captures: List[Capture] = _get_captures(pattern)
    pattern: Some = _get_as(pattern, Some)
    matches = []
    try:
        while pattern.count_ok_wrt_at_most(count + 1):
            subsequence = []
            ps = pattern.patterns
            for ix, (current_pattern, next_pattern) in enumerate(zip(ps, chain(ps[1:], [ps[0]]))):
                item = next(it)  # may raise StopIteration
                if ix == 0 and not pattern.greedy:
                    for terminator in reversed(terminators):
                        if ctx.match(item, terminator):
                            it.rewind()
                            raise StopIteration
                if _is_a(current_pattern, Some):
                    it.rewind()
                    r = _match_some(it, current_pattern, terminators=[next_pattern, *terminators], ctx=ctx)
                    if r is None:
                        raise StopIteration
                    r.merge(it, ctx)
                    subsequence.extend(r.matches)
                    continue
                if ctx.match(item, current_pattern):
                    subsequence.append(item)
                    continue
                it.rewind()
                raise StopIteration
            matches.append(subsequence[0] if len(subsequence) == 1 else subsequence)
            count += 1
    except StopIteration:
        pass
    if not pattern.count_ok_wrt_at_least(count):
        return None
    for capture in captures:
        capture.capture(matches, ctx=ctx)
    return matches


def _match_sequence(value, pattern: Union[tuple, list, Iterable], *, ctx: MatchContext) -> MatchResult:
    try:
        it = SeqIterator(value)
    except TypeError:
        return ctx.no_match()
    for current_pattern, next_pattern in zip(pattern, chain(pattern[1:], [Not(...)])):
        if _is_a(current_pattern, Some):
            r = _match_some(it, current_pattern, terminators=[next_pattern], ctx=ctx)
            if r is None:
                return ctx.no_match()
            r.merge(it, ctx)
            continue
        try:
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
        return ctx.matches()


class Underscore(Pattern):
    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        ctx.record(self, value)
        return ctx.matches()


_ = Underscore()
