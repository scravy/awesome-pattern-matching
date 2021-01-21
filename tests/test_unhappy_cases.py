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
            Many(..., at_least=2, at_most=1)
        with self.assertRaises(ValueError):
            Many(..., at_least=2, exactly=1)
        with self.assertRaises(ValueError):
            Many(..., at_most=2, exactly=1)

    def test_invalid_values_for_length(self):
        with self.assertRaises(ValueError):
            Length(at_least=2, exactly=1)
        with self.assertRaises(ValueError):
            Length(at_most=2, exactly=1)

    def test_string_no_match(self):
        self.assertFalse(match("http://example.org/", String(
            Capture("http://", name='protocol'),
            Arguments(),
        )))

    def test_string_one_of_no_match(self):
        self.assertFalse(match("abc", String("ab", OneOf("e", "f"))))

    def test_string_regex_match(self):
        result = match("hello world", String("hello ", Regex("[A-Z][a-z]*")))
        self.assertFalse(result)

    def test_strict_value(self):
        self.assertTrue(match(3, Value(3.0)))
        self.assertTrue(match(3, Strict(Value(3))))
        self.assertFalse(match(3, Strict(Value(3.0))))

    def test_mismatching_exception(self):
        with self.assertRaises(TypeError):
            try:
                raise ValueError
            except Case(...):
                pass

    def test_parampattern_no_match(self):
        from apm.typefoo import ParamType, KwArgs, VarArgs
        self.assertFalse(match(1, KwArgs()))
        self.assertFalse(match(1, VarArgs()))
        self.assertFalse(match(1, ParamType(int)))
