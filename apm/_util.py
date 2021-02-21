import inspect
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


def invoke(func, args: Union[Mapping, Iterable]):
    code: CodeType = func.__code__
    argcount = code.co_argcount
    actual_args = []
    if isinstance(args, Mapping):
        for _, name in zip(range(0, argcount), code.co_varnames):
            arg = args[name] if name in args else None
            actual_args.append(arg)
    else:
        for _, arg in zip(range(0, argcount), chain(args, repeat(None))):
            actual_args.append(arg)

    return func(*actual_args)
