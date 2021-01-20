import re
from itertools import chain
from typing import Union, Any, Optional

from ._util import invoke
from .core import MatchResult, MatchContext, transform, _, Underscore, Capture
from .error import MatchError
from .no_value import NoValue
from .patterns import InstanceOf, Regex
from .try_match import TryMatch


def _autopattern(pattern):
    if isinstance(pattern, type):
        return InstanceOf(pattern) & Underscore()
    if isinstance(pattern, re.Pattern):
        return Regex(pattern, capture_wildcards=True, bind_groups=False)
    if pattern is _:
        # this turns every underscore into a distinct object with it's own id - important
        # for recording wildcard matches via MatchContext.record
        return Underscore()
    return pattern


def match(value, pattern=NoValue, *extra,
          multimatch: bool = False,
          strict: bool = False,
          captureall: Optional[dict] = None) -> Union[MatchResult, Any]:
    """Matches the given value. Three different call styles are possible:

    (1) match(value, pattern, **kwargs)

    The so-called "simple" style which matches the given value against the given pattern, taking into account
    any options given as keyword-arguments and returns a MatchResult.

    (2) match(value)

    The "statement" style, to be used in a try...except block. This will actually raise a TryMatch Exception
    which is then caught by the matchers in the following except branches.

    (3) match(value, pattern1, action1, pattern2, action2, ...)

    The "terse" style. Every two arguments denote a pair of pattern and action. If pattern matches the value
    the corresponding action is invoked. If the action is actually callable it is called and it's return value
    is returned. It the action is a value then that value is simply returned.

    The "terse" style has a number of tweaks which are different from the matching in all other styles:

    - If a type is given as a pattern, the value is checked against that type using 'InstanceOf'. Each match
      is captured.
    - If a regular expression pattern ('re.Pattern', result of 're.compile') is given, then the value is checked
      against that regular expression and all capturing groups are captured.

    The captures are passed to the callable action.

    :param value: The value to be matched.
    :param pattern: The pattern to be matched against (if the "simple" style is used).
    :param multimatch: Whether to capture multiple matches per capture or keep the latest only (defaults to False).
    :param strict: Whether to perform strict matches (defaults to False).
    :param captureall: Capture all patterns into the given dictionary
    :return:
    """
    ctx = MatchContext(
        multimatch=multimatch,
        strict=strict,
    )
    if pattern is NoValue:
        raise TryMatch(value, ctx=ctx)
    elif extra:
        acc = []
        for p in chain((pattern,), extra):
            acc.append(transform(p, _autopattern))
            if len(acc) == 2:
                condition, action = acc
                result = match(value, condition)
                if result:
                    if callable(action):
                        return invoke(action, result.wildcard_matches())
                    return action
                acc = []
        if len(acc) == 1:
            if callable(acc[0]):
                return invoke(acc[0], [])
            return acc[0]
        raise MatchError(value)

    if isinstance(captureall, dict):
        count = 0

        def generate_name():
            nonlocal count
            count += 1
            return f"n{count}"

        pattern = transform(pattern, lambda x: Capture(x, name=generate_name(), target=captureall))

    result = ctx.match(value, pattern, strict=strict)
    return result
