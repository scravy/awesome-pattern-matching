from __future__ import annotations

import unittest

from apm import *
from apm.core import SomePatternCompatibilityArgumentsError


class Compat(unittest.TestCase):
    def test_some_compat(self):
        self.assertTrue(match([1, 2], [Some(Between(1, 2))]))
        self.assertTrue(match([1, 2], [Some(pattern=Between(1, 2))]))

    def test_some_compat_conflicting_args(self):
        with self.assertRaises(SomePatternCompatibilityArgumentsError):
            Some(1, 2, pattern=3)
