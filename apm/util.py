from inspect import CO_VARARGS
from types import CodeType
from typing import List, Optional, Type


def get_arg_types(obj) -> List[Optional[Type]]:
    code: CodeType = obj.__code__
    args = []
    argcount = code.co_argcount
    if code.co_flags & CO_VARARGS:
        argcount += 1
    for ix, name in zip(range(0, argcount), code.co_varnames):
        args.append(obj.__annotations__[name] if name in obj.__annotations__ else None)
    return args


def get_result_type(obj) -> Optional[Type]:
    if 'return' in obj.__annotations__:
        return obj.__annotations__['return']
    return None
