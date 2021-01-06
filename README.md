# Awesome Pattern Matching (_apm_) for Python

[![Github Actions](https://github.com/scravy/awesome-pattern-matching/workflows/Python%20application/badge.svg)](https://github.com/scravy/awesome-pattern-matching/actions) [![Downloads](https://static.pepy.tech/personalized-badge/awesome-pattern-matching?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads)](https://pepy.tech/project/awesome-pattern-matching)

- Simple
- Powerful
- Extensible
- Python 3.8+
- Typed (IDE friendly)

There's a ton of pattern matching libraries available for python, all with varying degrees of maintenance and usability;
also [there's a PEP on it's way for a match construct](https://www.python.org/dev/peps/pep-0634/).
However, I wanted something which works well and works now, so here we are.

_`apm`_ defines patterns as objects which are _composable_ and _reusable_. Pieces can be matched and captured into
variables, much like pattern matching in Haskell or Scala (a feature which most libraries actually lack,
but which also makes pattern matching useful in the first place - the capability to easily extract data).
Capturing pieces of the input is very similar to the way capturing groups work in regular expressions,
just a bit more noisy. Here is an example:

```python
match(value, ["first", Capture(..., name="2nd"), Capture(..., name="3rd")])
```

The above example matches a list of exactly three elements, the first element being exactly `"first"`, the seconds
and third being anything (`...` – the ellipsis is actual syntax and performs a wildcard match).
It captures the seconds and third elements as `2nd` and `3rd` respectively. `match` returns a `MatchResult` which
can be used to access `2nd` and `3rd`:

```python
if result := match(value, ["first", Capture(..., name="2nd"), Capture(..., name="3rd")]):
    result['2nd']  # first element
    result['3rd']  # second element
```

Patterns can be composed using `&`, `|`, and `^`, or via their more explicit counterparts `AllOf`, `OneOf`, and `Either`.
Since patterns are objects, they can be stored in variables and be reused.

```python
positive_number = InstanceOf(int) & Check(lambda x: x >= 0)
```

## Installation

```python
pip install awesome-pattern-matching
```

## Usage

```python
from apm import *

record = {
    "ID": 9340,
    "First-Name": "Jane",
    "Last-Name": "Doe",
}

if result := match(record, {"First-Name": Capture(Regex("[A-Z][a-z]*"), name="name")}):
    print(result['name'])
```

## Very slim User Guide

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

### `Capture(pattern, name=<str>)`

Captures a piece of the thing being matched by name.

```python
if result := match([1, 2, 3, 4], [1, 2, Capture(Remaining(InstanceOf(int)), name='tail')]):
    print(result['tail'])  ## -> [3, 4]
```

### `Strict(pattern)`

Performs a strict pattern match. A strict pattern match also compares the type of verbatim values. That is, while
_`apm`_ would match `3` with `3.0` it would not do so when using `Strict`. Also _`apm`_ performs partial matches
of dictionaries (that is: it ignores unknown keys). It will perform an exact match for dictionaries using `Strict`.

```python
# The following will match
match({"a": 3, "b": 7}, {"a": ...})
match(3.0, 3)

# These will not match
match({"a": 3, "b": 7}, Strict({"a": ...}))
match(3.0, Strict(3))
```

### `OneOf(pattern1, pattern2, ..)`

Matches against any of the provided patterns. Equivalent to `p1 | p2 | p3 | ..`
(but operator overloading does not work with values that do not inherit from `Pattern`)

```python
match("quux", OneOf("bar", "baz", "quux"))
```

```python
match(3, OneOf(InstanceOf(int), None))
```

### `AllOf(pattern1, pattern2, ..)`

Checks whether the value matches all of the given pattern. Equivalent to `p1 & p2 & p3 & ..`
(but operator overloading does not work with values that do not inherit from `Pattern`)

```python
match("quux", AllOf(InstanceOf("str"), Regex("[a-z]+")))
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

### `Check(predicate)`

Matches an object if it satisfies the given predicate.

```python
match(2, Check(lambda x: x % 2 == 0))
```

### `InstanceOf(type1 [, type2 [, ..]])`

Matches an object if it is an instance of any of the given types.

```python
match(1, InstanceOf(int, flaot))
```

### `Arguments(type1 [, type2 [, ..]])`

Matches a callable if it's type annotations correspond to the given types.
Very useful for implementing rich APIs.

```python
def f(x: int, y: float, z):
    ...

match(f, Arguments(int, float, None))
```

### `Returns(type)`

Matches a callable if it's type annotations denote the given return type.

```python
def g(x: int) -> str:
    ...

match(g, Arguments(int) & Returns(str))
```

### `Transformed(function, pattern)`

Transforms the currently looked at value by applying `function` on it and matches the result against `pattern`.
In Haskell and other languages this is known as a [_view pattern_](https://gitlab.haskell.org/ghc/ghc/-/wikis/view-patterns).

```python
def sha256(v: str) -> str:
    import hashlib
    return hashlib.new('sha256', v.encode('utf8')).hexdigest()

match("hello", Transformed(sha256, "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"))
```

### `At(path, pattern)`

Checks whether the nested object to be matched satisfied pattern at the given path.
The match fails if the given path can not be resolved.

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

## More Examples

Demonstrated below: Junction of Patterns using `&`, `Strict` dictionary matching, `Each`.

```python
records = [
    {
        "Foo": 1,
        "Bar": "Quux"
    },
    {
        "Foo": 2,
        "Bar": "Baz"
    }
]

assertTrue(
    match(records, Each(Strict({"Foo": InstanceOf(int), "Bar": InstanceOf(str) & Regex("[A-Z][a-z]+")}))))

records = [
    {
        "Foo": 1,
        "Bar": "Quux"
    },
    {
        "Foo": 2,
        "Bar": "Baz",
        "Strict": "Does not allow unknown keys"
    }
]

assertFalse(
    match(records, Each(Strict({"Foo": InstanceOf(int), "Bar": InstanceOf(str) & Regex("[A-Z][a-z]+")}))))

records = [
    {
        "Foo": 1,
        "Bar": "Quux"
    },
    {
        "Foo": 2,
        "Bar": "Baz",
        "No Problem": "When Not Strict"
    }
]

assertTrue(  # Note how this pattern is the same as above but without `Strict`
    match(records, Each({"Foo": InstanceOf(int), "Bar": InstanceOf(str) & Regex("[A-Z][a-z]+")})))
```
