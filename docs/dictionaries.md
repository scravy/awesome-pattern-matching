# Matching dictionaries

Dictionaries can be matched like other native datastructures:

```python
match(value={"key": "value"}, pattern={"key": "value"})
match(value={"key": "value"}, pattern={"key": _})
match(value={"key": "value"}, pattern={"key": InstanceOf(str)})
```

Keys can be patterns too. The following example expresses that every key that is a str must have a value of type int:

```python
match({InstanceOf(str): InstanceOf(int)})
```

Here is a bigger example – it matches a dictionary only if each key that starts with `foo-` has a value that
satisfies `InstanceOf(int)`, each key starting with `bar-` must have a value which matches `InstanceOf(float)`,
and the remainder must satisfy `EachItem(_, InstanceOf(str))`.

```python
match({ "foo-one": 1,
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

The underscore is a special pattern.
