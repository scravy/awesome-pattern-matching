from .core import MatchResult, apply


class NoGuardSucceeded(Exception):
    pass


class Guarded:
    def __init__(self, *args):
        self._args = args

    def evaluate(self, result: MatchResult):
        acc = []
        for arg in self._args:
            acc.append(arg)
            if len(acc) == 2:
                condition, action = acc
                acc.clear()
                if callable(condition):
                    ok = apply(condition, result)
                else:
                    ok = action
                if not ok:
                    continue
                if callable(action):
                    return apply(action, result)
                return action
        raise NoGuardSucceeded


def guarded(*args):
    return Guarded(*args)
