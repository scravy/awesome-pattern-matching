from __future__ import annotations

import unittest

from apm import *


class DictionaryMatchingTests(unittest.TestCase):

    def test_empty_dict(self):
        self.assertTrue(match({}, {}))

    def test_empty_subdict(self):
        self.assertTrue(match({"a": 3}, {}))

    def test_empty_dict_strict(self):
        self.assertTrue(match({}, Strict({})))

    def test_empty_subdict_strict(self):
        self.assertFalse(match({"a": 3}, Strict({})))

    def test_mismatching_types(self):
        self.assertFalse(match(3, {}))

    def test_pattern_dict_wildcard(self):
        self.assertTrue(match({"user": "id"}, {_: "id"}))

    def test_pattern_dict(self):
        self.assertTrue(match({
            "i9": 17,
            "f17": 3.0,
        }, {
            Regex(r"i[0-9]+"): InstanceOf(int),
            Regex(r"f[0-9]+"): InstanceOf(float),
        }))

    def test_pattern_dict_unknown_key(self):
        value = {
            "i9": 17,
            "f17": 3.0,
            "unknown": True,
        }
        pattern = {
            Regex(r"i[0-9]+"): InstanceOf(int),
            Regex(r"f[0-9]+"): InstanceOf(float),
        }
        self.assertTrue(match(value, pattern))
        self.assertFalse(match(value, Strict(pattern)))

    def test_pattern_dict_mismatching_value_for_pattern_key(self):
        self.assertFalse(match({
            "i9": 17,
            "i81": 9.8,
        }, {
            Regex(r"i[0-9]+"): InstanceOf(int),
            Regex(r"f[0-9]+"): InstanceOf(float),
        }))

    def test_pattern_dict_mismatching_value_for_pattern_key_with_more_general_match(self):
        self.assertTrue(match({
            "i9": 17,
            "i81": "9.8",
        }, {
            Regex(r"i[0-9]+"): InstanceOf(int),
            Regex(r"f[0-9]+"): InstanceOf(float),
            _: InstanceOf(str),
        }))

    def test_pattern_dict_mismatching_value_for_pattern_key_with_mismatching_more_general_match(self):
        self.assertFalse(match({
            "i9": 17,
            "i81": "9.8",
        }, {
            Regex(r"i[0-9]+"): InstanceOf(int),
            Regex(r"f[0-9]+"): InstanceOf(float),
            _: InstanceOf(bool),
        }))

    def test_remainder(self):
        result = match({
            "foo": 1,
            "bar": 2,
            "qux": 4,
            "quuz": 8,
        }, {"foo": 'foo' @ _, "bar": 'bar' @ _} ** Remainder('rs' @ _))
        self.assertTrue(result)
        self.assertEqual(1, result.foo)
        self.assertEqual(2, result.bar)
        self.assertEqual(4, result.rs['qux'])
        self.assertEqual(8, result.rs['quuz'])

    def test_remainder_check(self):
        result = match({
            "foo": 1,
            "bar": 2,
            "qux": 4,
            "quuz": 8,
        }, {"foo": 'foo' @ _, "bar": 'bar' @ _} ** Remainder(Check(lambda x: not x)))
        self.assertFalse(result)

        result = match({
            "foo": 1,
            "bar": 2,
        }, {"foo": 'foo' @ _, "bar": 'bar' @ _} ** Remainder(Check(lambda x: not x)))
        self.assertTrue(result)

    def test_dict_key_patterns(self):
        pattern = {
                      Regex(r'^foo-.+$'): InstanceOf(int),
                      Regex(r'^bar-.+$'): InstanceOf(float),
                  } ** Remainder('rest' @ EachItem(_, InstanceOf(str)))
        value = {
            "foo-one": 1,
            "foo-two": 2,
            "bar-one": 1.0,
            "bar-two": 2.0,
            "qux-one": "one",
            "qux-two": "two",
        }
        result = match(value, pattern)
        self.assertTrue(result)
        self.assertEqual({"qux-one": "one", "qux-two": "two"}, result['rest'])
        self.assertFalse(match({**value, 'qux-one': 7}, pattern))
        self.assertFalse(match({**value, 'foo-one': 'one'}, pattern))
        self.assertFalse(match({**value, 'bar-one': False}, pattern))

    def test_dict_underscore_pattern(self):
        result = match({
            1: {2: 3},
            2: {3: 4},
        }, {_: {2: _}})
        self.assertTrue(result)

        result = match({
            1: {2: 3},
            2: {3: 4},
        }, {_: {4: _}})
        self.assertFalse(result)
