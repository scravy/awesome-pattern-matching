from __future__ import annotations

import unittest

from apm import *


class ExceptionsTest(unittest.TestCase):

    def test_match_error_in_terse_syntax(self):
        with self.assertRaises(MatchError):
            match(7,
                  0, "zero",
                  1, "one")

    def test_match_error_in_declarative_syntax(self):
        @case_distinction
        def f(x: Match(0)):
            pass

        @case_distinction
        def f(x: Match(1)):
            pass

        with self.assertRaises(MatchError):
            f(2)
