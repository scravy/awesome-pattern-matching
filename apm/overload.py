import inspect
from typing import Callable, Dict, List

import typing

from apm.match import match


class Match:
    def __init__(self, pattern):
        self._pattern = pattern

    @property
    def pattern(self):
        return self._pattern

    def __call__(self):
        return self


class NoMatchError(Exception):
    pass


# noinspection PyDefaultArgument
def overload(fn: Callable, func_map: Dict[str, List[Callable]] = {}):
    qualified_name = fn.__qualname__
    if qualified_name not in func_map:
        func_map[qualified_name] = []
    cases = func_map[qualified_name]
    cases.append(fn)

    def wrapper(*args, **kwargs):
        for func in func_map[qualified_name]:
            sig: inspect.Signature = inspect.signature(func)
            try:
                bound: inspect.BoundArguments = sig.bind(*args, **kwargs)
            except TypeError:
                continue
            matches = True
            type_hints = typing.get_type_hints(func)
            for name, value in bound.arguments.items():
                if name not in type_hints:
                    continue
                annotation = type_hints[name]
                if isinstance(annotation, Match):
                    if not match(value, annotation.pattern):
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
        raise NoMatchError

    return wrapper


def case_distinction(f):
    return overload(f)
