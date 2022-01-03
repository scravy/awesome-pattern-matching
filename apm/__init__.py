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
    Remainder, \
    Some, \
    Strict, \
    String, \
    StringPattern, \
    Value, \
    _
from .error import MatchError
from .guarded import guarded
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
    Object, \
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

Remaining = Some
Many = Some

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
    'Remainder',
    'Remaining',
    'Some',
    'Strict',
    'String',
    'StringPattern',
    'Value',

    '_',

    'case',
    'match',
    'guarded',
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
