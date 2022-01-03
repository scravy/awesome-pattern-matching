from __future__ import annotations

import unittest

# noinspection PyProtectedMember
from apm.core import Capture, Some, _is_a, _get_as
from apm import match, InstanceOf


class CoreTest(unittest.TestCase):

    def test_get_as(self):
        self.assertIsInstance(_get_as(Some(), Some), Some)

    def test_get_as_assertion_error(self):
        with self.assertRaises(AssertionError):
            _get_as(Some(), str)
        with self.assertRaises(AssertionError):
            _get_as(Capture(str, name='foo'), Some)

    def test_is_a(self):
        self.assertTrue(_is_a(Some(), Some))

    def test_match_result(self):
        self.assertEqual(3, match(3, 'x' @ InstanceOf(int)).get('x'))
        self.assertEqual(None, match(3, 'x' @ InstanceOf(int)).get('y'))
