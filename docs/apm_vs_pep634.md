# Comparison of _`apm`_ and PEP-634 `match`

Python 3.10 introduced the
[`match` statement defined by PEP-634](https://www.python.org/dev/peps/pep-0634/)
which implements Structural Pattern Matching. `match` is also gives us an
equivalent for the less powerful `switch`, as found in many programming languages.

As a general rule of thumb PEP-634 is generally both faster and more readable,
as it uses native python syntax.
Every kind of matching that PEP-634 supports is also supported by _`apm`_, but _`apm`_
has more features than PEP-634 and works on older Python versions.

A very superficial comparison of the two:

| PEP-634            | Awesome Pattern Matching       |
| ------------------ | -------------------------------|
| fast               | less fast<sup>1</sup>          |
| good functionality | even more features             |
| native syntax      | different styles<sup>2</sup>   |
| fixed              | extensible<sup>3</sup>         |
| ≥ Python 3.10      | ≥ Python 3.7, pypy3.7, pypy3.8 |

**<sup>1</sup>A word on execution speed**: While it is the authors firm believe that if you're
interested in raw speed only Python should not be your choice of language, _`apm`_
is actually between 50x to 100x slower than native PEP-634 pattern matching. It is still reasonably fast though. For example the whole test suite runs in 20ms, so we're
talking about the difference from a few nano seconds to a hundred nano seconds.

**<sup>2</sup>Native syntax vs. different styles**: Since _`apm`_ can not alter the
grammar of the python language it has to use
existing language constructs. It offers various styles which use (or absue) existing
constructs to different degrees. The author of this library leaves it up to the users
of the library to decide which style suits them best, but you should stick to one.
The [in-depth comparison of PEP-636 and _`apm`_](https://github.com/scravy/awesome-pattern-matching/blob/main/docs/pep634_vs_different_apm_styles.py)
also compares different _`apm`_ styles. Note also that the shape of the patterns matched
themselves does not change and can be shared between the different styles as well.
See below for examples.

**<sup>3</sup>Extensibility**: The way _`apm`_ is built automatically makes patterns a
[first-class citizen](https://en.wikipedia.org/wiki/First-class_citizen)
(unlike patterns in PEP-634). This means that patterns can be stored in variables,
dynamically built, shared, and so on. It also allows _`apm`_ to be extended. In fact,
a lot of the pre-built patterns in _`apm`_ 
[could equally well be defined by users of the library](https://github.com/scravy/awesome-pattern-matching/blob/main/apm/patterns.py).

## Similarities and Differences

Both PEP-634  and _`apm`_ can match all kinds of patterns:

| PEP-634 | _`apm`_ |
| ------- | ------- |
| `3` | `3`|
| `"string value"` | `"string value"` |
| `[action]` | `['action' @ _]` |
| `[action, obj]` | `['action' @ _, 'obj' @ _]` |
| `["go", direction]` | `["go", 'direction' @ _]` |
| `["drop", *objects]` | `["drop", 'objects' @ Remaining()]` |
| _ | _ |
| `["north"] | ["go", "north"]` | `OneOf(["north"], ["go", "north"])` |
| `["get", obj] | ["pick", "up", obj] | ["pick", obj, "up"]` | `OneOf(["get", 'obj' @ _], ["pick", "up", 'obj' @ _], ["pick", 'obj' @ _, "up"])` |
| `["go", ("north" | "south" | "east" | "west") as direction]` | `["go", 'direction' @ OneOf("north", "south", "east", "west")]` |


### Matching data classes

Both PEP-634 and _`apm`_ can match dataclasses:

```python
from dataclasses import dataclass
from uuid import UUID
from apm import *

@dataclass
class Record:
    key: UUID
    title: str
    value: float

given = Record(key=UUID("25982462-1118-43FF-B9A3-1A19D46AF8B2"),
               title="An object",
               value=187.27)
    
result = match(given, Record(_, "An object", 'value' @ Between(100, 200)))
print(result.result)  # prints 187.27

match given:
    case Record(_, "An object", value) if 100 <= value <= 200:  # matches
        print(value)  # prints 187.27
```

The above example also highlights a difference in the general design of _`apm`_. While _`apm`_ does support case
guards (the `if 100 <= x <= 200`) such checks are better expressed by using existing patterns (`Between` in this case).
There is also a general `Check` pattern that takes a lambda and will only match if that yields true on the value
being matched.

Another visible difference is that _`apm`_'s match function can also be used as an inline-expression and be used to
just extract data. The returned match-result works like a dictionary and also offers `.get(key, default=None)`:

```python
extracted_value = match(given, Record(_, "An object", 'value' @ Between(100, 200))).get('result', 0)
```


## In-Depth comparison

An in-depth comparison of the two can be found in this python script that compares the [PEP-636](https://www.python.org/dev/peps/pep-0636/) examples with the different _`apm`_
styles: **[`docs/pep634_vs_different_apm_styles.py`](https://github.com/scravy/awesome-pattern-matching/blob/main/docs/pep634_vs_different_apm_styles.py)**.
It is like the [Rosetta Stone](https://en.wikipedia.org/wiki/Rosetta_Stone) for PEP-634 and _`apm`_.

