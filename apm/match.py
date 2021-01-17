from itertools import chain
from typing import Union, Any

from .core import MatchResult, MatchContext, transform, _, Underscore, AllOf
from .no_value import NoValue
from .patterns import InstanceOf
from .try_match import TryMatch


def _autopattern(pattern):
    if isinstance(pattern, type):
        return InstanceOf(pattern) & Underscore()
    if pattern is _:
        return Underscore()
    return pattern


class MatchError(Exception):
    pass


def match(value, pattern=NoValue, *extra, multimatch=False, strict=False) -> Union[MatchResult, Any]:
    ctx = MatchContext(
        multimatch=multimatch,
        strict=strict,
    )
    if pattern is NoValue:
        raise TryMatch(value, ctx=ctx)
    elif extra:
        acc = []
        for p in chain((pattern,), extra):
            acc.append(transform(p, _autopattern))
            if len(acc) == 2:
                condition, action = acc
                result = match(value, condition)
                if result:
                    if callable(action):
                        return action(*result.wildcard_matches())
                    return action
                acc = []
        if len(acc) == 1:
            return acc[0]
        raise MatchError(value)
    result = ctx.match(value, pattern, strict=strict)
    return result
