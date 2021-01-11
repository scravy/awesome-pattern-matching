from __future__ import annotations

import unittest

from apm import *


class Glob(unittest.TestCase):

    def test_empty(self):
        self.assertTrue(match(
            [1, 2, 3],
            [1, Some(...), 2, 3]
        ))

    def test_at_least(self):
        self.assertTrue(match(
            [1, 2, 3],
            [
                1,
                Some(..., at_least=2),
            ]))
        self.assertFalse(match(
            [1, 2],
            [
                1,
                Some(..., at_least=2),
            ]))

    def test_at_most(self):
        self.assertTrue(match(
            [1, 2, 3, 4],
            [
                1,
                Some(..., at_most=2),
                4,
            ]))
        self.assertFalse(match(
            [1, 2, 3],
            [
                1,
                Some(..., at_most=2),
                4,
            ]))

    def test_with_remaining(self):
        self.assertTrue(match(
            [1, 2, 3],
            [
                1,
                Some(..., at_most=2),
                Remaining(...),
            ]))

    def test_multiple(self):
        self.assertTrue(match(
            range(1, 10),
            [
                1,
                2,
                Some(...),
                6,
                Some(...),
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
                Capture(Some(...), name=1),
                6,
                Capture(Some(...), name=2),
                8,
                9,
            ]
        )
        self.assertTrue(result)
        self.assertEqual(result[1], [3, 4, 5])
        self.assertEqual(result[2], [7])
