from __future__ import annotations

import unittest

from apm import *


class Glob(unittest.TestCase):

    def test_empty(self):
        self.assertTrue(match(
            [1, 2, 3],
            [1, Many(...), 2, 3]
        ))

    def test_at_least(self):
        self.assertTrue(match(
            [1, 2, 3],
            [
                1,
                Many(..., at_least=2),
            ]))
        self.assertFalse(match(
            [1, 2],
            [
                1,
                Many(..., at_least=2),
            ]))

    def test_at_most(self):
        self.assertTrue(match(
            [1, 2, 3, 4],
            [
                1,
                Many(..., at_most=2),
                4,
            ]))
        self.assertFalse(match(
            [1, 2, 3],
            [
                1,
                Many(..., at_most=2),
                4,
            ]))

    def test_with_remaining(self):
        self.assertTrue(match(
            [1, 2, 3],
            [
                1,
                Many(..., at_most=2),
                Remaining(...),
            ]))

    def test_multiple(self):
        self.assertTrue(match(
            range(1, 10),
            [
                1,
                2,
                Many(...),
                6,
                Many(...),
                8,
                9,
            ]
        ))

    def test_capture(self):
        result = match(
            range(1, 10),
            [
                1,
                2,
                Capture(Many(...), name=1),
                6,
                Capture(Many(...), name=2),
                8,
                9,
            ]
        )
        self.assertTrue(result)
        self.assertEqual(result[1], [3, 4, 5])
        self.assertEqual(result[2], [7])

    def test_exactly(self):
        result = match(range(1, 10), [
            1,
            Many(..., exactly=3) >> 'a',
            Many(...) >> 'b',
            6,
            7,
            8,
            9
        ])
        self.assertTrue(result)
        self.assertEqual([2, 3, 4], result.a)
        self.assertEqual([5], result.b)

    def test_exactly_empty_following(self):
        result = match(range(1, 10), [
            1,
            Many(..., exactly=4) >> 'a',
            Many(...) >> 'b',
            6,
            7,
            8,
            9
        ])
        self.assertTrue(result)
        self.assertEqual([2, 3, 4, 5], result.a)
        self.assertEqual([], result.b)
        self.assertEqual("MatchResult(matches=True, groups={'a': [2, 3, 4, 5], 'b': []})", repr(result))
