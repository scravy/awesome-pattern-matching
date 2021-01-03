# Awesome Pattern Matching (_amp_) for Python

- Simple
- Powerful
- Extensible
- Python 3.8+
- Typed (IDE friendly)

There's a ton of pattern matching libraries available for python, all with varying degrees of maintenance and usability; also there's a PEP on it's way for a match construct. However, I wanted something which works well and works now, so here we are.

_`amp`_ defines patterns as objects which are composable and reusable. Patterns can be matched and captured into variables, must like pattern matching in Haskell or Scala (a feature which most libraries actually lack, but which also makes pattern matching useful in the first place - the capability to easily extract data). Capturing pieces of the input is very similar to the way capturing groups work in regular expressions, just a bit more noisy. Here is an example:

```python
match(value, [Capture(..., name="fst"), Capture(..., name="snd")])
```

The above example matches a list of exactly two elements and captures the first and second element as `fst` and `snd`. `match` returns a `MatchResult` which can be used to access `fst` and `snd`:

```python
if result := match(value, [Capture(..., name="fst"), Capture(..., name="snd")]):
    result['fst']  # first element
    result['snd']  # second element
```

Patterns can be composed using `&`, `|`, and `^`, or via their more explicit counterparts `AllOf`, `OneOf`, and `Either`. Since patterns are objects, they can be stored in variables and be reused.

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
from apm.patterns import Regex

record = {
    "ID": 9340,
    "First-Name": "Jane",
    "Last-Name": "Doe",
}

if result := match(record, {"First-Name": Capture(Regex("[A-Z][a-z]*"), name="name")}):
    print(result['name'])
```

## Some Features

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

### `Capture(pattern, name=<str>)` (`apm.*`)

Captures a piece of the thing being matched by name.

```python
if result := match([1, 2, 3, 4], [1, 2, Capture(Remaining(InstanceOf(int)), name='tail')]):
    print(result['tail'])  ## -> [3, 4]
```

### `Each(pattern [, at_least=]` (`apm.*`)

Matches each item in an iterable.

```python
match(range(1, 10), Each(Between(1, 9)))
```

### `OneOf(pattern1, pattern2, ...)` (`apm.*`)

Matches against any of the provided patterns. Equivalent to `p1 | p2 | p3`
(but operator overloading does not work with values that do not inherit from `Pattern`)

```python
match("quux", OneOf("bar", "baz", "quux"))
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
