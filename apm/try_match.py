import sys

from .core import MatchContext, MatchResult, apply


class Default(BaseException):
    pass


class TryMatch(Default, MatchResult):
    def __init__(self, value, *, ctx: MatchContext):
        MatchResult.__init__(self, matches=False, context=ctx, match_stack=[])
        self.value = value
        self.context = ctx


class NoMatch(BaseException):
    pass


# noinspection PyPep8Naming
def Case(pattern, when=None):
    _, exc, _ = sys.exc_info()

    if not isinstance(exc, TryMatch):
        raise TypeError

    result = exc.context.match(exc.value, pattern)
    if result and (when is None or (callable(when) and apply(when, result))):
        exc._matches = True
        # no need to fill in match_stack as well: It is only relevant if there is no match, in which case the
        # result object will not be accessible as we will only have it in an `except ... as result` statement
        return TryMatch
    return NoMatch
