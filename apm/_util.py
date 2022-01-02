from __future__ import annotations

import inspect

try:
    from collections.abc import Iterator
except ImportError:
    from collections import Iterator
from inspect import CO_VARARGS  # pylint: disable=no-name-in-module
from itertools import chain, repeat
from types import CodeType
from typing import List, Optional, Type, get_type_hints, Dict, Union, Mapping, Iterable


def get_arg_types(obj) -> List[Optional[Type]]:
    code: CodeType = obj.__code__
    args = []
    argcount = code.co_argcount
    if code.co_flags & CO_VARARGS:
        argcount += 1
    type_hints = get_type_hints(obj)
    for ix, name in zip(range(0, argcount), code.co_varnames):
        args.append(type_hints.get(name, None))
    return args


def is_keyword_parameter(p: inspect.Parameter) -> bool:
    if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
        return True
    if p.kind == inspect.Parameter.KEYWORD_ONLY:
        return True
    return False


def get_kwarg_types(obj) -> Dict[str, type]:
    sig: inspect.Signature = inspect.signature(obj)
    type_hints = get_type_hints(obj)
    result = {}
    for name, parameter in sig.parameters.items():
        if not is_keyword_parameter(parameter):
            continue
        result[parameter.name] = type_hints.get(parameter.name, None)
    return result


def get_return_type(obj) -> Optional[Type]:
    type_hints = get_type_hints(obj)
    return type_hints.get('return', None)


def call(func, *args, **kwargs):
    code: CodeType = func.__code__
    final_args = []
    final_kwargs = {}
    for ix, name in zip(range(0, code.co_argcount), code.co_varnames):
        if name in kwargs:
            final_args.append(kwargs[name])
        elif ix < len(args):
            final_args.append(args[ix])
        else:
            final_args.append(None)
    for ix, name in zip(range(0, code.co_kwonlyargcount), code.co_varnames[code.co_argcount:]):
        if name in kwargs:
            final_kwargs[name] = kwargs[name]
        else:
            final_kwargs[name] = None
    return func(*final_args, **final_kwargs)


class MemoIterator:
    __slots__ = ('_it', '_elements')

    def __init__(self, it: Iterable):
        if isinstance(it, (list, tuple)):
            self._it = iter(tuple())
            self._elements = it
        else:
            self._it = iter(it)
            self._elements = []

    def at(self, ix: int):
        while ix >= len(self._elements):
            elem = next(self._it)  # will raise StopIterator if empty – expected as part of the contract of this method
            self._elements.append(elem)
        return self._elements[ix]


class SeqIterator(Iterator):
    __slots__ = ('_it', '_ix')

    def __init__(self, seq: Union[Iterable, MemoIterator], *, from_index: int = 0):
        self._it = seq if isinstance(seq, MemoIterator) else MemoIterator(seq)
        self._ix = from_index

    def __next__(self):
        elem = self._it.at(self._ix)
        self._ix += 1
        return elem

    def __iter__(self) -> SeqIterator:
        return SeqIterator(self._it, from_index=self._ix)

    def fork(self) -> SeqIterator:
        return self.__iter__()

    def merge(self, other: SeqIterator):
        assert self._it is other._it
        self._ix = other._ix

    def rewind(self, steps: int = 1):
        self._ix = max(0, self._ix - steps)
