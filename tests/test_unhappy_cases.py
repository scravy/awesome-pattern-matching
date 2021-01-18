from __future__ import annotations

import unittest
from dataclasses import dataclass

from apm import *


@dataclass
class Record:
    foo: str
    bar: str


@dataclass
class User:
    foo: str
    bar: str


class UnhappyCasesTest(unittest.TestCase):

    def test_dataclass_no_match(self):
        self.assertFalse(match(Record("qux", "quuz"), 7))

    def test_dataclass_type_mismatch(self):
        self.assertFalse(match(Record("qux", "quuz"), User("qux", "quuz")))

    def test_strict_list_mismatch(self):
        xs = [0, 1, 2]
        vs = range(0, 3)
        self.assertTrue(match(vs, xs))
        self.assertFalse(match(vs, Strict(xs)))

    def test_simple_no_match(self):
        self.assertFalse(match(1, 2))

    def test_value_no_match(self):
        self.assertTrue(match(1, Value(1)))
        self.assertFalse(match(1, Value(2)))

    def test_strict_value_no_match(self):
        self.assertTrue(match(1, Value(1.0)))
        self.assertFalse(match(1, Strict(Value(1.0))))

    def test_invalid_values_for_some(self):
        with self.assertRaises(ValueError):
            Some(..., at_least=2, at_most=1)
        with self.assertRaises(ValueError):
            Some(..., at_least=2, exactly=1)
        with self.assertRaises(ValueError):
            Some(..., at_most=2, exactly=1)
