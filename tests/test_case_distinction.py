from __future__ import annotations

import unittest

from apm import *


class CaseDistinctionTest(unittest.TestCase):

    def test_case_distinction(self):
        @case_distinction
        def fib(n: Match(OneOf(0, 1))):
            return n

        @case_distinction
        def fib(n):
            return fib(n - 2) + fib(n - 1)

        self.assertEqual(0, fib(0))
        self.assertEqual(1, fib(1))
        self.assertEqual(1, fib(2))
        self.assertEqual(2, fib(3))
        self.assertEqual(3, fib(4))
        self.assertEqual(5, fib(5))
        self.assertEqual(8, fib(6))

    def test_readme_example(self):
        value = 7

        def check(v):
            self.assertEqual("It's between 1 and 10", v)

        @case_distinction
        def f(n: Match(Between(1, 10))):
            check("It's between 1 and 10")
            return 1

        @case_distinction
        def f(n: Match(Between(11, 20))):
            check("It's between 11 and 20")
            return 2

        @case_distinction
        def f(n):
            check("It's not between 1 and 20")
            return 3

        self.assertEqual(1, f(value))

    def test_overloading(self):
        def check(v):
            pass

        @case_distinction
        def f(a: str, b: str):
            return 0

        @case_distinction
        def f(a: int, b: int):
            return 1

        @case_distinction
        def f(a: int, b: int, c: int):
            return 2

        self.assertEqual(0, f("a", "b"))
        self.assertEqual(1, f(1, 2))
        self.assertEqual(2, f(1, 2, 3))
