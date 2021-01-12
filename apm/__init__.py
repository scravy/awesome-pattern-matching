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
    Remaining, \
    Some, \
    Strict, \
    String, \
    StringPattern, \
    Value, \
    _
from .match import match
from .overload import case_distinction, Match
from .patterns import \
    Arguments, \
    At, \
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
    Regex, \
    Returns, \
    Transformed
from .try_match import Case, Default

__all__ = [
    'AllOf',
    'Capture',
    'Either',
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
    'Case',
    'Default',

    'Arguments',
    'At',
    'Between',
    'Check',
    'Contains',
    'Each',
    'EachItem',
    'InstanceOf',
    'IsNumber',
    'IsString',
    'IsTruish',
    'Length',
    'Maybe',
    'NoneOf',
    'Object',
    'Regex',
    'Returns',
    'Transformed',
]
