from itertools import chain
from typing import Union, Any

from .core import MatchResult, MatchContext
from .try_match import TryMatch


class AttributesAdapter:
    def __init__(self, base):
        self._base = base

    def __bool__(self):
        return bool(self._base)

    def __getattr__(self, item):
        try:
            return self._base[item]
        except KeyError as err:
            raise AttributeError(*err.args)


class NoValue:
    pass


def match(value, pattern=NoValue, *extra, multimatch=True, strict=False, argresult=False) -> Union[MatchResult, Any]:
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
    if argresult:
        result = AttributesAdapter(result)
    return result
