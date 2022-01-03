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

    def test_get_kwarg_types(self):
        self.assertEqual({"a": int, "b": float, "c": str, "d": str}, util.get_kwarg_types(f))
        self.assertEqual({"a": int, "b": str}, util.get_kwarg_types(g))

    def test_vararg_types(self):
        self.assertEqual({"a": int}, util.get_kwarg_types(h))
        self.assertEqual([int, float], util.get_arg_types(h))

    def test_seq_iterator_list_zip(self):
        xs = [1, 2, 3]
        invocations = 0
        for a, b in zip(iter(xs), util.SeqIterator(xs)):
            invocations += 1
            self.assertEqual(a, b)
        self.assertEqual(len(xs), invocations)

    def test_seq_iterator_tuple_zip(self):
        xs = (1, 2, 3)
        invocations = 0
        for a, b in zip(iter(xs), util.SeqIterator(xs)):
            invocations += 1
            self.assertEqual(a, b)
        self.assertEqual(len(xs), invocations)

    def test_seq_iterator_list_comprehension(self):
        xs = [1, 2, 3]
        ys = [*util.SeqIterator(xs)]
        self.assertEqual(xs, ys)

    def test_seq_iterator_tuple_comprehension(self):
        xs = (1, 2, 3)
        ys = [*util.SeqIterator(xs)]
        self.assertEqual([*xs], ys)

    def test_seq_iterator_fork(self):
        xs = (1, 2, 3)
        it = util.SeqIterator(xs)
        a = next(it)
        it2 = iter(it)
        b = next(it)
        c = next(it)
        d = next(it2)
        self.assertEqual(1, a)
        self.assertEqual(2, b)
        self.assertEqual(3, c)
        self.assertEqual(2, d)

    def test_call_overlapping_args(self):
        def fn(a, b, c, *, d, e):
            return (a or 0) + (b or 0) + (c or 0) + (d or 0) + (e or 0)

        self.assertEqual(1 + 2 + 16 + 32, util.call(fn, 1, 2, 4, 8, c=16, e=32))

    def test_call_empty(self):
        def fn(a, b, c, *, d, e):
            return (a or 0) + (b or 0) + (c or 0) + (d or 0) + (e or 0)

        self.assertEqual(0, util.call(fn))

    def test_call_kwargs(self):
        def fn(a, b, c, *, d, e):
            return (a or 0) + (b or 0) + (c or 0) + (d or 0) + (e or 0)

        self.assertEqual(1 + 2 + 4 + 8 + 16, util.call(fn, a=1, b=2, c=4, d=8, e=16))
