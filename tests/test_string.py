from __future__ import annotations

import unittest

from apm import *


class StringTests(unittest.TestCase):

    def test_regex_named_capturing_groups(self):
        result = match("Hello, Jane Doe!", String(
            "Hello, ",
            Regex(r"(?P<first_name>[A-Z][a-z]*) (?P<last_name>[A-Z][a-z]*)"),
            "!"
        ))
        self.assertTrue(result)
        self.assertEqual(2, len(result))
        self.assertEqual("Jane", result.first_name)
        self.assertEqual("Doe", result.last_name)

    def test_regex_dont_bind_named_capturing_groups(self):
        result = match("Hello, Jane Doe!", String(
            "Hello, ",
            Regex(r"(?P<first_name>[A-Z][a-z]*) (?P<last_name>[A-Z][a-z]*)", bind_groups=False),
            "!"
        ))
        self.assertTrue(result)
        self.assertEqual(0, len(result))
