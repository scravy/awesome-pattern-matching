from __future__ import annotations

import unittest
from dataclasses import dataclass

# noinspection PyProtectedMember
from apm.generic import elements, AutoRepr, AutoEqHash, _repr


@dataclass
class Record:
    foo: int
    bar: str


class GenericTests(unittest.TestCase):

    def test_elements(self):
        self.assertEqual([1, 2, 3], [x for x in elements([1, 2, 3])])
        self.assertEqual([1, tuple([2]), 3], [x for x in elements([1, [2], 3])])
        self.assertEqual([1, 2, 3], [x for x in elements({"a": 1, "b": 2, "c": 3})])
        self.assertEqual([4, "qux"], [x for x in elements(Record(4, "qux"))])
        self.assertEqual([1], [x for x in elements(1)])

    def test_auto_eq(self):

        class X(AutoEqHash):
            def __init__(self, a, b):
                self.a = a
                self.b = b

        x1 = X(1, 2)
        x2 = X(1, 2)
        x3 = X(2, 0)

        self.assertEqual(x1, x2)
        self.assertEqual(x2, x1)
        self.assertNotEqual(x2, x3)
        self.assertNotEqual(x3, x2)
        self.assertNotEqual(x1, x3)
        self.assertNotEqual(x3, x1)

    def test_auto_repr(self):
        class X(AutoRepr):
            def __init__(self, a, b):
                self.a = a
                self.b = b

        x = X(1, 2)

        self.assertEqual("X({a=1, b=2})", repr(x))

    def test_repr(self):
        self.assertEqual("{0='a', 1='b'}", _repr({0: "a", 1: "b"}))
