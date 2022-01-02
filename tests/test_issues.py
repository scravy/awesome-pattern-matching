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

        self.assertTrue(match(Foo(1), Foo, True, False))
        self.assertTrue(match(Foo(1), Foo(1), True, False))
        self.assertFalse(match(Foo(1), Foo(2), True, False))

    # noinspection PyPep8Naming
    def test_issue_8(self):
        """https://github.com/scravy/awesome-pattern-matching/issues/8"""

        class sp:
            is_keyword = lambda keyword: lambda thing: thing.lower() == keyword.lower()

        case_dog = [
            "WHEN",
            "species",
            "=",
            "'Dog'",
            "THEN",
            "'Woof'",
        ]

        case_mouse = [
            "WHEN",
            "species",
            "=",
            "'Mouse'",
            "THEN",
            "'Squeak'",
        ]

        case_cat = [
            "WHEN",
            "species",
            "=",
            "'Cat'",
            "THEN",
            "'Meow'",
        ]

        s1 = [
            "case",
            *case_dog,
            "end",
        ]
        r1 = match(
            s1,
            [
                Some(...),
                "when1" @ Check(sp.is_keyword("when")),
                Some(...),
            ]
        )
        self.assertTrue(r1)
        self.assertEqual("WHEN", r1['when1'])

        s2 = [
            "case",
            *case_dog,
            *case_mouse,
            "end",
        ]
        r2 = match(
            s2,
            [
                Some(...),
                "when1" @ Check(sp.is_keyword("when")),
                Some(...),
                "when2" @ Check(sp.is_keyword("when")),
                Some(...),
            ]
        )
        self.assertTrue(r2)
        self.assertEqual("WHEN", r2['when1'])
        self.assertEqual("WHEN", r2['when2'])

        s3 = [
            "CASE",
            *case_dog,
            *case_mouse,
            *case_cat,
            "END",
        ]
        r3 = match(
            s3,
            [
                Check(sp.is_keyword("case")),
                "cases" @ Some(
                    Check(sp.is_keyword("when")),
                    Some(...),
                    Check(sp.is_keyword("then")),
                    Some(...),
                ),
                Check(sp.is_keyword("end")),
            ]
        )
        self.assertTrue(r3)
        self.assertEqual([
            ['WHEN', 'species', '=', "'Dog'", 'THEN', "'Woof'"],
            ['WHEN', 'species', '=', "'Mouse'", 'THEN', "'Squeak'"],
            ['WHEN', 'species', '=', "'Cat'", 'THEN', "'Meow'"],
        ], r3['cases'])
