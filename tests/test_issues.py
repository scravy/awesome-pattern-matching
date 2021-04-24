from __future__ import annotations

import unittest
# noinspection PyProtectedMember
from dataclasses import dataclass

from apm import *


@dataclass
class Foo:
    x: int


class UtilTests(unittest.TestCase):

    def test_issue_2(self):
        """https://github.com/scravy/awesome-pattern-matching/issues/2"""

        result = match(Foo(1), Foo, 'this matches', 'no match unfortunately')
        self.assertEqual('this matches', result)
