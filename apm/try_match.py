import sys

from .core import MatchContext


class Default(BaseException):
    pass


class TryMatch(Default):
    def __init__(self, value, *, ctx: MatchContext):
        self.value = value
        self.context = ctx
        self.result = None

    def __getitem__(self, item):
        return self.result[item]  # pylint: disable=unsubscriptable-object

    def __contains__(self, item):
        return item in self.result  # pylint: disable=unsupported-membership-test

    def __iter__(self):
        return iter(self.result)


class NoMatch(BaseException):
    pass


# noinspection PyPep8Naming
def Case(pattern):
    _, exc, _ = sys.exc_info()

    if not isinstance(exc, TryMatch):
        raise TypeError

    result = exc.context.match(exc.value, pattern)
    if result:
        exc.result = result
        return TryMatch
    return NoMatch
