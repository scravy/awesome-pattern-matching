from . import agg
from .__pkginfo__ import __version__
from .case_of import case
from .core import \
    AllOf, \
    Capture, \
    Either, \
    MatchContext, \
    MatchResult, \
    Not, \
    OneOf, \
    Pattern, \
    Many, \
    Strict, \
    String, \
    StringPattern, \
    Value, \
    _
from .error import MatchError
from .match import match
from .overload import case_distinction, Match
from .patterns import \
    Arguments, \
    At, \
    Attrs, \
    Between, \
    Check, \
    Contains, \
    Each, \
    EachItem, \
    InstanceOf, \
    IsNumber, \
    IsString, \
    IsTruish, \
    Length, \
    Maybe, \
    NoneOf, \
    Items, \
    Regex, \
    Returns, \
    SubclassOf, \
    Transformed
from .try_match import Case, Default
from .typefoo import \
    Parameters, \
    KwArgs, \
    VarArgs

Remaining = Many
Some = Many

Object = Items

__all__ = [
    'agg',

    'AllOf',
    'Capture',
    'Either',
    'Many',
    'MatchContext',
    'MatchResult',
    'Not',
    'OneOf',
    'Pattern',
    'Remaining',
    'Some',
    'Strict',
    'String',
    'StringPattern',
    'Value',

    '_',

    'case',
    'match',
    'case_distinction',
    'Match',
    'MatchError',
    'Case',
    'Default',

    'Arguments',
    'At',
    'Attrs',
    'Between',
    'Check',
    'Contains',
    'Each',
    'EachItem',
    'InstanceOf',
    'IsNumber',
    'IsString',
    'IsTruish',
    'Items',
    'Length',
    'Maybe',
    'NoneOf',
    'Object',
    'Regex',
    'Returns',
    'SubclassOf',
    'Transformed',

    'Parameters',
    'KwArgs',
    'VarArgs',
]
