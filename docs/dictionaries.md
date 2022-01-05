# Matching dictionaries

Dictionaries can be matched like other native datastructures:

```python
match(value={"key": "value"}, pattern={"key": "value"})
match(value={"key": "value"}, pattern={"key": _})
match(value={"key": "value"}, pattern={"key": InstanceOf(str)})
```

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Key patterns](#key-patterns)
- [Special key pattern `_`](#special-key-pattern-_)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Key patterns

Keys can be patterns too. The following example expresses that every key that is a str must have a value of type int:

```python
match({InstanceOf(str): InstanceOf(int)})
```

Here is a bigger example – it matches a dictionary only if each key that starts with `foo-` has a value that
satisfies `InstanceOf(int)`, each key starting with `bar-` must have a value which matches `InstanceOf(float)`, and the
remainder must satisfy `EachItem(_, InstanceOf(str))`.

```python
match({"foo-one": 1,
       "foo-two": 2,
       "bar-one": 1.0,
       "bar-two": 2.0,
       "qux-one": "one",
       "qux-two": "two",
       }, {
          Regex(r'^foo-.+$'): InstanceOf(int),
          Regex(r'^bar-.+$'): InstanceOf(float),
      } ** Remainder('rest' @ EachItem(_, InstanceOf(str)))
      )
```

## Special key pattern `_`

The underscore is a special pattern. It allows descending into any object and will match if one of the objects matches
the associated pattern:

```python
value = {
    'foo': {
        'quuz': 3
    },
    'bar': {
        'qux': 10
    }
}
match(value, {
    _: {
        'qux': InstanceOf(int)
    }
})
```

The above example will match because there is some key in `value` for which it's value matches the
pattern `{ 'qux': InstanceOf(int) }`.

When using [key patterns (see above)](#key-patterns) one might be tempted to use the `_` (underscore) pattern as a
fallback. The `** Remainder` should be used for that, as the `_` has the special meaning presented here.
