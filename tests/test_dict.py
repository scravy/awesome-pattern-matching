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
