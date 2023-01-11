from __future__ import annotations

import functools
import inspect
import typing
from typing import Callable, Dict, List

from .core import MatchResult, apply
from .error import MatchError
from .match import match


class Match:
    def __init__(self, pattern, *, when: typing.Optional[Callable] = None, **kwargs):
        self._pattern = pattern
        self._kwargs = kwargs
        self.when = when

    def __call__(self, value):
        # typing.get_type_hints requires annotations to be callable, otherwise it bombs out with a TypeError
        return match(value, self._pattern, **self._kwargs)


# noinspection PyDefaultArgument
def overload(fn: Callable, func_map: Dict[str, List[Callable]] = {}):
    qualified_name = fn.__qualname__
    if qualified_name not in func_map:
        func_map[qualified_name] = []
    cases = func_map[qualified_name]
    cases.append(fn)

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        for func in func_map[qualified_name]:
            sig: inspect.Signature = inspect.signature(func)
            try:
                bound: inspect.BoundArguments = sig.bind(*args, **kwargs)
            except TypeError:
                continue
            matches = True
            # resolve the annotations which are strings as per __future__
            type_hints = typing.get_type_hints(func)
            for name, value in bound.arguments.items():
                if name not in type_hints:
                    continue
                annotation = type_hints[name]
                if isinstance(annotation, Match):
                    result: MatchResult = annotation(value)
                    if not result:
                        matches = False
                        break
                    if callable(annotation.when) and not apply(annotation.when, result):
                        matches = False
                        break
                try:
                    # noinspection PyTypeHints
                    if not isinstance(value, annotation):
                        matches = False
                        break
                except TypeError:
                    pass
            if not matches:
                continue

            return func(*bound.args, **bound.kwargs)
        raise MatchError(f"No match(args={repr(args)}, kwargs={repr(kwargs)})")

    return wrapper


def case_distinction(f):
    return overload(f)
