from itertools import chain
from typing import Union, Any

from .core import MatchResult, MatchContext
from .try_match import TryMatch


class NoValue:
    pass


def match(value, pattern=NoValue, *extra, multimatch=True, strict=False) -> Union[MatchResult, Any]:
    ctx = MatchContext(
        multimatch=multimatch,
        strict=strict,
    )
    if pattern is NoValue:
        raise TryMatch(value, ctx=ctx)
    elif extra:
        acc = []
        for p in chain((pattern,), extra):
            acc.append(p)
            if len(acc) == 2:
                condition, action = acc
                result = match(value, condition)
                if result:
                    if callable(action):
                        return action(*result.wildcard_matches())
                    return action
                acc = []
    result = ctx.match(value, pattern, strict=strict)
    return result
