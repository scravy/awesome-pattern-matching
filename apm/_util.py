from inspect import CO_VARARGS  # pylint: disable=no-name-in-module
from types import CodeType
from typing import List, Optional, Type, get_type_hints


def get_arg_types(obj) -> List[Optional[Type]]:
    code: CodeType = obj.__code__
    args = []
    argcount = code.co_argcount
    if code.co_flags & CO_VARARGS:
        argcount += 1
    type_hints = get_type_hints(obj)
    for ix, name in zip(range(0, argcount), code.co_varnames):
        args.append(type_hints[name] if name in type_hints else None)
    return args


def get_return_type(obj) -> Optional[Type]:
    type_hints = get_type_hints(obj)
    if 'return' in type_hints:
        return type_hints['return']
    return None
