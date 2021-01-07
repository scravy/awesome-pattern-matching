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


class _NoValue:
    pass


def match(value, pattern=_NoValue, *, multimatch=True, strict=False, argresult=False) -> MatchResult:
    ctx = MatchContext(
        multimatch=multimatch,
        strict=strict,
    )
    if pattern is _NoValue:
        raise TryMatch(value, ctx=ctx)
    result = ctx.match(value, pattern, strict=strict)
    if argresult:
        result = AttributesAdapter(result)
    return result
