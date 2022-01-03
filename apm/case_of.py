from __future__ import annotations

from ._util import call
from .core import apply
from .guarded import Guarded, NoGuardSucceeded
from .match import match


class CaseExpr:
    def __init__(self, value, **kwargs):
        self._value = value
        self._kwargs = kwargs

    def of(self, pattern, then, when=None, **kwargs) -> CaseExpr:
        result = match(self._value, pattern, **{**self._kwargs, **kwargs})
        if result:
            if callable(when) and not apply(when, result):
                return self
            if isinstance(then, Guarded):
                try:
                    return CaseExprEnd(then.evaluate(result))
                except NoGuardSucceeded:
                    return self
            if callable(then):
                return CaseExprEnd(apply(then, result))
            else:
                return CaseExprEnd(then)
        else:
            return self

    def otherwise(self, then):
        if callable(then):
            return call(then)
        else:
            return then


class CaseExprEnd(CaseExpr):

    def of(self, pattern, then, **kwargs) -> CaseExpr:
        return self

    def otherwise(self, then):
        return self._value


def case(value) -> CaseExpr:
    return CaseExpr(value)
