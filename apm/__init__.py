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
    Length, \
    Regex, \
    Returns, \
    Transformed, \
    Truish
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
    'Length',
    'Regex',
    'Returns',
    'Transformed',
    'Truish',
]
