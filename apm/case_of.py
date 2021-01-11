from __future__ import annotations

from ._util import invoke
from .match import match


class CaseExpr:
    def __init__(self, value):
        self._value = value

    def of(self, pattern, then) -> CaseExpr:
        result = match(self._value, pattern)
        if result:
            if callable(then):
                return CaseExprEnd(invoke(then, result))
            else:
                return CaseExprEnd(then)
        else:
            return self

    def otherwise(self, then):
        if callable(then):
            return invoke(then, {})
        else:
            return then


class CaseExprEnd(CaseExpr):

    def of(self, pattern, then) -> CaseExpr:
        return self

    def otherwise(self, then):
        return self._value


def case(value) -> CaseExpr:
    return CaseExpr(value)
