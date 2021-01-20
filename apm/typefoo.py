import inspect
import typing
from dataclasses import dataclass
from itertools import chain
from typing import List, Optional, Union, Dict, Any

from . import MatchContext, MatchResult
from .case_of import case
from .core import Pattern, Nested, Many, transform
from .no_value import NoValue

try:
    from typing import get_origin
except ImportError:
    def get_origin():
        print("WARNING: typing.get_origin() is only available from python 3.8+")
        return None

try:
    from typing import get_args
except ImportError:
    def get_args():
        print("WARNING: typing.get_args() is only available from python 3.8+")
        return ()


@dataclass
class Parameter:
    index: Optional[int]
    name: Optional[str]
    type_hint: Any
    kind: 'typing.Literal["", "*", "**"]' = ""

    @property
    def is_positional(self):
        return self.index is not None

    @property
    def is_keyword_only(self):
        return self.index is None and self.name is not None

    @property
    def is_varargs(self):
        return self.kind == '*'

    @property
    def is_kwargs(self):
        return self.kind == '**'


class ParamPattern(Pattern):

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        if not isinstance(value, Parameter):
            return ctx.no_match()
        return self.match_parameter(value, ctx)

    def match_parameter(self, param: Parameter, ctx: MatchContext) -> MatchResult:
        raise NotImplementedError


class ParamType(ParamPattern):
    def __init__(self, type_=...):
        self._type = type_

    def match_parameter(self, param: Parameter, ctx: MatchContext) -> MatchResult:
        return ctx.match(param.type_hint, self._type)


class VarArgs(ParamPattern):
    def __init__(self, type_=...):
        self._type = type_

    def match_parameter(self, param: Parameter, ctx: MatchContext) -> MatchResult:
        if not param.is_varargs:
            return ctx.no_match()
        return ctx.match(param.type_hint, self._type)


class KwArgs(ParamPattern):
    def match_parameter(self, param: Parameter, ctx: MatchContext) -> MatchResult:
        return ctx.match_if(param.is_kwargs)


def mk_pattern(p) -> Union[Pattern, Many]:
    if isinstance(p, type) and issubclass(p, ParamPattern):
        return p()
    if not isinstance(p, (Pattern, Many)):
        return ParamType(p)
    return p


class Parameters(Pattern, Nested):

    def __init__(self, *positional, **kwargs):
        self._params: List[Union[Pattern, Many]] = []
        for p in positional:
            pp = transform(p, mk_pattern)
            self._params.append(pp)
        self._kwargs: Dict[str, Union[Pattern, Many]] = {}
        for k, p in kwargs.items():
            pp = transform(p, mk_pattern)
            self._kwargs[k] = pp

    def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
        try:
            params = describe_parameters(value)
        except TypeError:
            return ctx.no_match()

        positional_params = list(chain(
            filter(lambda p: p.is_positional, params),
            filter(lambda p: p.is_varargs, params),
            filter(lambda p: p.is_kwargs, params),
        ))

        kwargs = {}
        for param in params:
            if param.is_keyword_only:
                kwargs[param.name] = param

        result = ctx.match(positional_params, self._params)
        if not result:
            return result
        result = ctx.match(kwargs, self._kwargs, strict=strict)
        if not result:
            return result

        return ctx.matches()

    def descend(self, f):
        t_params = list(f(p) for p in self._params)
        t_kwargs = {}
        for k, v in self._kwargs.items():
            t_kwargs[k] = f(v)
        return Parameters(*t_params, **t_kwargs)


def describe_parameters(func) -> List[Parameter]:
    type_hints = typing.get_type_hints(func)
    sig: inspect.Signature = inspect.signature(func)
    index = 0
    parameters = []
    for name, parameter in sig.parameters.items():
        type_hint = type_hints[name] if name in type_hints else NoValue
        parameter = case(parameter.kind) \
            .of(inspect.Parameter.POSITIONAL_OR_KEYWORD, lambda: Parameter(index, name, type_hint)) \
            .of(inspect.Parameter.POSITIONAL_ONLY, lambda: Parameter(index, None, type_hint)) \
            .of(inspect.Parameter.KEYWORD_ONLY, lambda: Parameter(None, name, type_hint)) \
            .of(inspect.Parameter.VAR_POSITIONAL, lambda: Parameter(None, None, type_hint, '*')) \
            .of(inspect.Parameter.VAR_KEYWORD, lambda: Parameter(None, None, type_hint, '**')) \
            .otherwise(...)
        parameters.append(parameter)
        index += 1
    return parameters
