# Awesome Pattern Matching (_apm_) for Python

[![Github Actions](https://github.com/scravy/awesome-pattern-matching/workflows/Python%20application/badge.svg)](https://github.com/scravy/awesome-pattern-matching/actions)
[![Downloads](https://pepy.tech/badge/awesome-pattern-matching)](https://pepy.tech/project/awesome-pattern-matching)
[![PyPI version](https://badge.fury.io/py/awesome-pattern-matching.svg)](https://pypi.org/project/awesome-pattern-matching/)

```bash
pip install awesome-pattern-matching
```

- Simple
- Powerful
- Extensible
- Composable
- Functional
- Python 3.7+, PyPy3.7+
- Typed (IDE friendly)
- Offers different styles (expression, declarative, statement, ...)

There's a ton of pattern matching libraries available for python, all with varying degrees of maintenance and usability;
also [there's a PEP on it's way for a match construct](https://www.python.org/dev/peps/pep-0634/). However, I wanted
something which works well and works now, so here we are.

_`apm`_ defines patterns as objects which are _composable_ and _reusable_. Pieces can be matched and captured into
variables, much like pattern matching in Haskell or Scala (a feature which most libraries actually lack, but which also
makes pattern matching useful in the first place - the capability to easily extract data). Here is an example:

```python
from apm import *

if result := match([1, 2, 3, 4, 5], [1, '2nd' @ _, '3rd' @ _, 'tail' @ Remaining(...)]):
    print(result['2nd'])  # 2
    print(result['3rd'])  # 3
    print(result['tail'])  # [4, 5]

# If you find it more readable, '>>' can be used instead of '@' to capture a variable
match([1, 2, 3, 4, 5], [1, _ >> '2nd', _ >> '3rd', Remaining(...) >> 'tail'])
```

Patterns can be composed using `&`, `|`, and `^`, or via their more explicit counterparts `AllOf`, `OneOf`, and `Either`
. Since patterns are objects, they can be stored in variables and be reused.

```python
positive_integer = InstanceOf(int) & Check(lambda x: x >= 0)
```

Some fancy matching patterns are available out of the box:

```python
from apm import *

def f(x: int, y: float) -> int:
    pass

if match(f, Arguments(int, float) & Returns(int)):
    print("Function satisfies required signature")
```

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Multiple Styles](#multiple-styles)
- [Nested pattern matches](#nested-pattern-matches)
- [Multimatch](#multimatch)
- [Strict vs non-strict matches](#strict-vs-non-strict-matches)
- [Match head and tail of a list](#match-head-and-tail-of-a-list)
- [Wildcard matches anything using `_`](#wildcard-matches-anything-using-_)
- [Wildcard matches anything using `...`](#wildcard-matches-anything-using-)
- [Support for dataclasses](#support-for-dataclasses)
- [The different styles in detail](#the-different-styles-in-detail)
  - [Simple style](#simple-style)
    - [pre `:=` version (Python 3.7)](#pre--version-python-37)
  - [Expression style](#expression-style)
  - [Statement style](#statement-style)
  - [Declarative style](#declarative-style)
    - [Nota bene: Overloading using `@case_distinction`](#nota-bene-overloading-using-case_distinction)
  - [Terse style](#terse-style)
- [Available patterns](#available-patterns)
  - [`Capture(pattern, name=<str>)`](#capturepattern-namestr)
  - [`Strict(pattern)`](#strictpattern)
  - [`OneOf(*pattern)`](#oneofpattern)
  - [`AllOf(*pattern)`](#allofpattern)
  - [`NoneOf(*pattern)`](#noneofpattern)
  - [`Not(pattern)`](#notpattern)
  - [`Each(pattern [, at_least=]`](#eachpattern--at_least)
  - [`EachItem(key_pattern, value_pattern)`](#eachitemkey_pattern-value_pattern)
  - [`Some(pattern)`](#somepattern)
  - [`Between(lower, upper)`](#betweenlower-upper)
  - [`Length(length)`](#lengthlength)
  - [`Contains(item)`](#containsitem)
  - [`Regex(regex_pattern, bind_groups: bool = True)`](#regexregex_pattern-bind_groups-bool--true)
  - [`Check(predicate)`](#checkpredicate)
  - [`InstanceOf(*types)`](#instanceoftypes)
  - [`SubclassOf(*types)`](#subclassoftypes)
  - [`Arguments(*types)`](#argumentstypes)
  - [`Returns(type)`](#returnstype)
  - [`Transformed(function, pattern)`](#transformedfunction-pattern)
  - [`At(path, pattern)`](#atpath-pattern)
  - [`Object(**kwargs))`](#objectkwargs)
- [Extensible](#extensible)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Multiple Styles

For matching and selecting from multiple cases, choose your style:

```python
from apm import *

value = 7

# The simple style
if match(value, Between(1, 10)):
    print("It's between 1 and 10")
elif match(value, Between(11, 20)):
    print("It's between 11 and 20")
else:
    print("It's not between 1 and 20")
    
# The expression style
case(value) \
    .of(Between(1, 10), lambda: print("It's between 1 and 10")) \
    .of(Between(11, 20), lambda: print("It's between 11 and 20")) \
    .otherwise(lambda: print("It's not between 1 and 20"))

# The statement style
try:
    match(value)
except Case(Between(1, 10)):
    print("It's between 1 and 10")
except Case(Between(11, 20)):
    print("It's between 11 and 20")
except Default:
    print("It's not between 1 and 20")

# The declarative style
@case_distinction
def f(n: Match(Between(1, 10))):
    print("It's between 1 and 10")

@case_distinction
def f(n: Match(Between(11, 20))):
    print("It's between 11 and 20")

@case_distinction
def f(n):
    print("It's not between 1 and 20")

f(value)

# The terse (pampy) style
match(value,
      Between( 1, 10), lambda: print("It's between 1 and 10"),
      Between(11, 20), lambda: print("It's between 11 and 20"),
      _,               lambda: print("It's not between 1 and 20"))
```


## Nested pattern matches

Patterns are applied recursively, such that nested structures can be matched arbitrarily deep.
This is super useful for extracting data from complicated structures:

```python
from apm import *

sample_k8s_response = {
    "containers": [
        {
            "args": [
                "--cert-dir=/tmp",
                "--secure-port=4443",
                "--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname",
                "--kubelet-use-node-status-port"
            ],
            "image": "k8s.gcr.io/metrics-server/metrics-server:v0.4.1",
            "imagePullPolicy": "IfNotPresent",
            "name": "metrics-server",
            "ports": [
                {
                    "containerPort": 4443,
                    "name": "https",
                    "protocol": "TCP"
                }
            ]
        }
    ]
}

if result := match(sample_k8s_response, {
        "containers": Each({
            "image": 'image' @ _,
            "name": 'name' @ _,
            "ports": Each({
                "containerPort": 'port' @ _
            }),
        })
    }):
    print(f"Image: {result['image']}, Name: {result['name']}, Port: {result['port']}")
```

The above will print

```
Image: k8s.gcr.io/metrics-server/metrics-server:v0.4.1, Name: metrics-server, Port: 4443
```


## Multimatch

By default `match` records only the last match for captures. If for example `'item' @ InstanceOf(int)` matches multiple times,
the last match will be recorded in `result['item']`. `match` can record all captures using the `multimatch=True` flag:

```python
if result := match([{'foo': 5}, 3, {'foo': 7, 'bar': 9}], Each(OneOf({'foo': 'item' @ _}, ...)), multimatch=True):
    print(result['item'])  # [5, 7]

# The default since v0.15.0 is multimatch=False
if result := match([{'foo': 5}, 3, {'foo': 7, 'bar': 9}], Each(OneOf({'foo': 'item' @ _}, ...))):
  print(result['item'])  # 7
```


## Strict vs non-strict matches

Any value which occurs verbatim in a pattern is matched verbatim (`int`, `str`, `list`, ...), except Dictionaries (
anything which has an `items()` actually).

Thus:

```python
some_very_complex_object = {
    "A": 1,
    "B": 2,
    "C": 3,
}
match(some_very_complex_object, {"C": 3})  # matches!
```

If you do not want unknown keys to be ignored, wrap the pattern in a `Strict`:

```python
# does not match, only matches exactly `{"C": 3}`
match(some_very_complex_object, Strict({"C": 3}))
```

Lists (anything iterable which does not have an `items()` actually) are also compared as they are, i.e.:

```python
ls = [1, 2, 3]
match(ls, [1, 2, 3])  # matches
match(ls, [1, 2])  # does not match
```


## Match head and tail of a list

It is possible to match the remainder of a list though:

```python
match(ls, [1, 2, Remaining(InstanceOf(int))])
```

And each item:

```python
match(ls, Each(InstanceOf(int)))
```

Patterns can be joined using `&`, `|`, and `^`:

```python
match(ls, Each(InstanceOf(int) & Between(1, 3)))
```

Wild-card matches are supported using Ellipsis (`...`):

```python
match(ls, [1, Remaining(..., at_least=2)])
```

The above example also showcases how `Remaining` can be made to match
`at_least` _n_ number of items (`Each` also has an `at_least` keyword argument).


## Wildcard matches anything using `_`

A wildcard pattern can be expressed using `_`. `_` is a `Pattern` and thus `>>` and `@` can be used with it.

```python
match([1, 2, 3, 4], [1, _, 3, _])
```


## Wildcard matches anything using `...`

The `Ellipsis` can be used as a wildcard match, too. It is however not a `Pattern` (so `|`, `&`, `@`, etc. can not
be used on it). If you actually want to match `Ellipsis`, wrap it using `Value(...)`.

Otherwise `...` is equivalent for most intents and purposes to `_`:

```python
match([1, 2, 3, 4], [1, ..., 3, ...])
```


## Support for dataclasses

```python
@dataclass
class User:
    first_name: str
    last_name: str

value = User("Jane", "Doe")

if match(value, User(_, "Doe")):
    print("Welcome, member of the Doe family!")
elif match(value, User(_, _)):
    print("Welcome, anyone!")
```


## The different styles in detail

### Simple style

- 💚 has access to result captures
- 💚 vanilla python
- 💔 can not return values (since it's a statement, not an expression)
- 🖤 a bit repetetive
- 💚 simplest and most easy to understand style

```python
from apm import *

value = {"a": 7, "b": "foo", "c": "bar"}

if result := match(value, EachItem(_, 'value' @ InstanceOf(str) | ...), multimatch=True):
    print(result['value'])  # ["foo", "bar"]
```

#### pre `:=` version (Python 3.7)

`bind()` can be used on a `MatchResult` to bind the matched items to an existing dictionary.

```python
from apm import *

value = {"a": 7, "b": "foo", "c": "bar"}

result = {}
if match(value, EachItem(_, 'value' @ InstanceOf(str) | ...)).bind(result):
    print(result['value'])  # ["foo", "bar"]
elif match(value, {"quux": _ >> 'quux'}).bind(result):
    print(result['quux'])
```

### Expression style

- 💚 has access to result captures
- 💚 vanilla python
- 💚 can return values
- 🖤 so terse that it is sometimes hard to read

The expression style is summarized:

```python
case(value).of(pattern, action) ... .otherwise(default_action)
```

...where action is either a value or a callable. The captures from the matching result are bound to the named
parameters of the given callable, i.e. `result['foo']` and `result['bar']` from `'foo' @ _` and `'bar' @ _` will be
bound to `foo` and `bar` respectively in `lambda foo, bar: ...`.

```python
from apm import *

display_name = case({'user': 'some-user-id', 'first_name': "Jane", 'last_name': "Doe"}) \
    .of({'first_name': 'first' @ _, 'last_name': 'last' @ _}, lambda first, last: f"{first}, {last}") \
    .of({'user': 'user_id' @ _}, lambda user_id: f"#{user_id}") \
    .otherwise("anonymous")
```

_Note: To return a value an `.otherwise(...)` case must always be present._


### Statement style

This is arguable the most hacky style in _`apm`_, as it re-uses the `try .. except`
mechanism. It is nevertheless quite readable.

- 💚 has access to result captures
- 💚 very readable
- 💔 can not return values (since it's a statement, not an expression)
- 🖤 misuse of the `try .. except` statement

```python
from apm import *

try:
    match({'user': 'some-user-id', 'first_name': "Jane", 'last_name': "Doe"})
except Case({'first_name': 'first' @ _, 'last_name': 'last' @ _}) as result:
    user = f"{result['first']} {result['last']}"
except Case({'user': 'user_id' @ _}) as result:
    user = f"#{result['user_id']}"
except Default:
    user = "anonymous"
    
print(user)  # "Jane Doe"
```


### Declarative style

- 💔 does not have access to result captures
- 💚 very readable
- 💚 can return values
- 🖤 the most bloated version of all styles

```python
from apm import *

@case_distinction
def fib(n: Match(OneOf(0, 1))):
   return n

@case_distinction
def fib(n):
    return fib(n - 2) + fib(n - 1)

for i in range(0, 6):
    print(fib(i))
```

#### Nota bene: Overloading using `@case_distinction`

If not for its pattern matching capabilities, `@case_distinction` can be used
to implement overloading. In fact, it can be imported as `@overload`.
The mechanism is aware of arity and argument types.

```python
from apm.overload import overload

@overload
def add(a: str, b: str):
    return "".join([a, b])

@overload
def add(a: int, b: int):
    return a + b

add("a", "b")
add(1, 2)
```

### Terse style

- 💚 has access to wildcard captures
- 💔 does not have access to named result captures
- 💚 very concise
- 💚 can return values
- 🖤 very readable when formatted nicely
- 🖤 not so well suited for larger match actions
- 🖤 does not work nicely with auto-formatting tools

As the name indicates the "terse" style is terse. It is inspired by the `pampy`
pattern matching library and mimics some of its behavior. Despite a slim surface
area it also comes with some simplifications:

- A type given as a pattern is matched against as if it was wrapped in an `InstanceOf`
- `re.Pattern` objects (result of `re.compile`) are matched against as if it was given via `Regex`
- Captures are passed to actions in the same order as they occur in the pattern (not by name)
  
```python
from apm import *

def fibonacci(n):
  return match(n,
               1, 1,
               2, 1,
               _, lambda x: fibonacci(x - 1) + fibonacci(x - 2)
               )

fibonacci(6)  # -> 8 


class Animal:        pass
class Hippo(Animal): pass
class Zebra(Animal): pass
class Horse(Animal): pass

def what_am_i(x):
  return match(x,
               Hippo,  'hippopotamus',
               Zebra,  'zebra',
               Animal, 'some other animal',
               _,      'not at all an animal',
               )

what_am_i(Hippo())  # -> 'hippopotamus'
what_am_i(Zebra())  # -> 'zebra'
what_am_i(Horse())  # -> 'some other animal'
what_am_i(42)       # -> 'not at all an animal'
```


## Available patterns

### `Capture(pattern, name=<str>)`

Captures a piece of the thing being matched by name.

```python
if result := match([1, 2, 3, 4], [1, 2, Capture(Remaining(InstanceOf(int)), name='tail')]):
    print(result['tail'])  ## -> [3, 4]
```

As this syntax is rather verbose, two short hand notations can be used:

```python
# using the matrix multiplication operator '@' (syntax resembles that of Haskell and Scala)
if result := match([1, 2, 3, 4], [1, 2, 'tail' @ Remaining(InstanceOf(int))]):
    print(result['tail'])  ## -> [3, 4]

# using the right shift operator
if result := match([1, 2, 3, 4], [1, 2, Remaining(InstanceOf(int)) >> 'tail']):
    print(result['tail'])  ## -> [3, 4]
```


### `Strict(pattern)`

Performs a strict pattern match. A strict pattern match also compares the type of verbatim values. That is, while
_`apm`_ would match `3` with `3.0` it would not do so when using `Strict`. Also _`apm`_ performs partial matches of
dictionaries (that is: it ignores unknown keys). It will perform an exact match for dictionaries using `Strict`.

```python
# The following will match
match({"a": 3, "b": 7}, {"a": ...})
match(3.0, 3)

# These will not match
match({"a": 3, "b": 7}, Strict({"a": ...}))
match(3.0, Strict(3))
```


### `OneOf(*pattern)`

Matches against any of the provided patterns. Equivalent to `p1 | p2 | p3 | ..`
(but operator overloading does not work with values that do not inherit from `Pattern`)

```python
match("quux", OneOf("bar", "baz", "quux"))
```

```python
match(3, OneOf(InstanceOf(int), None))
```

Patterns can also be joined using `|` to form a `OneOf` pattern:

```python
match(3, InstanceOf(int) | InstanceOf(float))
```

The above example is rather contrived, as `InstanceOf` already accepts multiple types natively:

```python
match(3, InstanceOf(int, float))
```

Since bare values do not inherit from `Pattern` they can be wrapped in `Value`:

```python
match("quux", Value("foo") | Value("quux"))
```


### `AllOf(*pattern)`

Checks whether the value matches all of the given pattern. Equivalent to `p1 & p2 & p3 & ..`
(but operator overloading does not work with values that do not inherit from `Pattern`)

```python
match("quux", AllOf(InstanceOf("str"), Regex("[a-z]+")))
```


### `NoneOf(*pattern)`

Same as `Not(OneOf(*pattern))` (also `~OneOf(*pattern)`).


### `Not(pattern)`

Matches if the given pattern does not match.

```python
match(3, Not(4))  # matches
match(5, Not(4))  # matches
match(4, Not(4))  # does not match
```

The bitflip prefix operator (`~`) can be used to express the same thing. Note that it does not work on bare values,
so they need to be wrapped in `Value`.

```python
match(3, ~Value(4))  # matches
match(5, ~Value(4))  # matches
match(4, ~Value(4))  # does not match
```

`Not` can be used do create a `NoneOf` kind of pattern:

```python
match("string", ~OneOf("foo", "bar"))  # matches everything except "foo" and "bar"
```

`Not` can be used to create a pattern that never matches:

```python
Not(...)
```


### `Each(pattern [, at_least=]`

Matches each item in an iterable.

```python
match(range(1, 10), Each(Between(1, 9)))
```


### `EachItem(key_pattern, value_pattern)`

Matches an object if each key satisfies `key_pattern` and each value satisfies `value_pattern`.

```python
match({"a": 1, "b": 2}, EachItem(Regex("[a-z]+"), InstanceOf(int)))
```


### `Some(pattern)`

Matches a sequence of items within a list:

```python
if result := match(range(1, 10), [1, 'a' @ Some(...), 4, 'b' @ Some(...), 8, 9]):
    print(result['a'])  # [2, 3]
    print(result['b'])  # [5, 6, 7]
```

Takes the optional values `exactly`, `at_least`, and `at_most` which makes `Some` match
either `exactly` _n_ items, `at_least` _n_, or `at_most` _n_ items (`at_least` and `at_most` can be given at the same
time, but not together with `exactly`).


### `Between(lower, upper)`

Matches an object if it is between `lower` and `upper` (inclusive). The optional keyword arguments
`lower_bound_exclusive` and `upper_bound_exclusive` can be set to `True` respectively to exclude the
lower/upper from the range of matching values.


### `Length(length)`

Matches an object if it has the given length. Alternatively also accepts `at_least` and `at_most` keyword arguments.

```python
match("abc", Length(3))
match("abc", Length(at_least=2))
match("abc", Length(at_most=4))
match("abc", Length(at_least=2, at_most=4))
```


### `Contains(item)`

Matches an object if it contains the given item (as per the same logic as the `in` operator).

```python
match("hello there, world", Contains("there"))
match([1, 2, 3], Contains(2) & Contains(3))
match({'foo': 1, 'bar': 2}, Contains('quux') | Contains('bar'))
```


### `Regex(regex_pattern, bind_groups: bool = True)`

Matches a string if it completely matches the given regex, as per `re.fullmatch`.
If the regular expression pattern contains named capturing groups and `bind_groups` is set to `True`,
this pattern will bind the captured results in the `MatchResult` (the default).

To mimic `re.match` or `re.search` the given regular expression `x` can be augmented as `x.*` or `.*x.*`
respectively.


### `Check(predicate)`

Matches an object if it satisfies the given predicate.

```python
match(2, Check(lambda x: x % 2 == 0))
```


### `InstanceOf(*types)`

Matches an object if it is an instance of any of the given types.

```python
match(1, InstanceOf(int, flaot))
```


### `SubclassOf(*types)`

Matches if the matched type is a subclass of any of the given types.

```python
match(int, SubclassOf(int, float))
```


### `Arguments(*types)`

Matches a callable if it's type annotations correspond to the given types. Very useful for implementing rich APIs.

```python
def f(x: int, y: float, z):
    ...


match(f, Arguments(int, float, None))
```

Arguments has an alternate form which can be used to match keyword arguments:

```python

def f(x: int, y: float, z: str):
    ...

match(f, Arguments(x=int, y=float))
```

The strictness rules are the same as for dictionaries (which is why the above example works).

```python
# given the f from above
match(f, Strict(Arguments(x=int, y=float)))  # does not match
match(f, Strict(Arguments(x=int, y=float, z=str)))  # matches
```


### `Returns(type)`

Matches a callable if it's type annotations denote the given return type.

```python
def g(x: int) -> str:
    ...


match(g, Arguments(int) & Returns(str))
```


### `Transformed(function, pattern)`

Transforms the currently looked at value by applying `function` on it and matches the result against `pattern`. In
Haskell and other languages this is known as a [_view
pattern_](https://gitlab.haskell.org/ghc/ghc/-/wikis/view-patterns).

```python
def sha256(v: str) -> str:
    import hashlib
    return hashlib.new('sha256', v.encode('utf8')).hexdigest()

match("hello", Transformed(sha256, "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"))
```

This is handy for matching data types like `datetime.date` as this pattern won't match if the transformation
function errored out with an exception.

```python
from apm import *
from datetime import date

if result := match("2020-08-27", Transformed(date.fromisoformat, 'date' @ _):
    print(repr(result['date']))  # result['date'] is a datetime.date
```


### `At(path, pattern)`

Checks whether the nested object to be matched satisfied pattern at the given path. The match fails if the given path
can not be resolved.

```python
record = {
    "foo": {
        "bar": {
            "quux": {
                "value": "deeply nested"
            }
        }
    }
}

result := match(record, At("foo.bar.quux", {"value": Capture(..., name="value")}))
result['value']  # "deeply nested"

# alternate form
result := match(record, At(['foo', 'bar', 'quux'], {"value": Capture(..., name="value")}))
```


### `Object(**kwargs))`

Mostly syntactic sugar to match a dictionary nicely.

```python
from apm import *
from datetime import datetime

request = {
    "api_version": "v1",
    "job": {
        "run_at": "2020-08-27 14:09:30",
        "command": "echo 'booya'",
    }
}

if result := match(request, Object(
    api_version="v1",
    job=Object(
        run_at=Transformed(datetime.fromisoformat, 'time' @ _),
    ) & OneOf(
        Object(command='command' @ InstanceOf(str)),
        Object(spawn='container' @ InstanceOf(str)),
    )
)):
    print(repr(result['time']))      # datetime(2020, 8, 27, 14, 9, 30)
    print('container' not in result) # True
    print(result['command'])         # "echo 'booya'"
```


## Extensible

New patterns can be added, just like the ones in `apm.patterns.*`. Simply extend the `apm.Pattern` class:

```python
class Min(Pattern):
    def __init__(self, min):
        self.min = min

    def match(self, value, *, ctx: MatchContext, strict=False) -> MatchResult:
        return ctx.match_if(value >= self.min)

match(3, Min(1))  # matches
match(3, Min(5))  # does not match
```
