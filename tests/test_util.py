from __future__ import annotations

import unittest

# noinspection PyProtectedMember
from dataclasses import dataclass

import apm._util as util
from apm import *


# noinspection PyUnusedLocal
def f(a: int, b: float, c: str, d: str) -> str:
    pass


# noinspection PyUnusedLocal
def g(a: int, *, b: str) -> float:
    pass


@dataclass
class Record:
    foo: int
    bar: str


class UtilTests(unittest.TestCase):

    def test_get_arg_types(self):
        arg_types = util.get_arg_types(f)
        self.assertTrue(match(
            arg_types,
            [int, float, Remaining(str)]
        ))

    def test_get_return_type(self):
        self.assertEqual(str, util.get_return_type(f))

    def test_invoke(self):
        args = {
            "b": 3,
            "c": 4,
        }
        result = util.invoke(lambda a, b: (a, b), args)
        self.assertEqual((None, 3), result)

    def test_get_kwarg_types(self):
        self.assertEqual({"a": int, "b": float, "c": str, "d": str}, util.get_kwarg_types(f))
        self.assertEqual({"a": int, "b": str}, util.get_kwarg_types(g))

    def test_get_arg_names(self):
        self.assertEqual(["a", "b", "c", "d"], util.get_arg_names(f))

    def test_elements(self):
        self.assertEqual([1, 2, 3], [x for x in util.elements([1, 2, 3])])
        self.assertEqual([1, tuple([2]), 3], [x for x in util.elements([1, [2], 3])])
        self.assertEqual([1, 2, 3], [x for x in util.elements({"a": 1, "b": 2, "c": 3})])
        self.assertEqual([4, "qux"], [x for x in util.elements(Record(4, "qux"))])
