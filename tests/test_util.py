from __future__ import annotations

import unittest

# noinspection PyProtectedMember
import apm._util as util
from apm import *


# noinspection PyUnusedLocal
def f(a: int, b: float, c: str, d: str) -> str:
    pass


# noinspection PyUnusedLocal
def g(a: int, *, b: str) -> float:
    pass


# noinspection PyUnusedLocal
def h(a: int, *xs: float):
    pass


class UtilTests(unittest.TestCase):

    def test_get_arg_types(self):
        arg_types = util.get_arg_types(f)
        self.assertTrue(match(
            arg_types,
            [int, float, Remaining(str)]
        ))

    def test_get_return_type(self):
        self.assertEqual(str, util.get_return_type(f))

    def test_get_return_type_none(self):
        self.assertEqual(None, util.get_return_type(lambda: None))

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

    def test_vararg_types(self):
        self.assertEqual({"a": int}, util.get_kwarg_types(h))
        self.assertEqual([int, float], util.get_arg_types(h))
