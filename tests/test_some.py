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

    def test_exactly(self):
        result = match(range(1, 10), [
            1,
            Some(..., exactly=3) >> 'a',
            Some(...) >> 'b',
            6,
            7,
            8,
            9,
        ])
        self.assertTrue(result)
        self.assertEqual([2, 3, 4], result.a)
        self.assertEqual([5], result.b)

    def test_exactly_empty_following(self):
        result = match(range(1, 10), [
            1,
            Some(..., exactly=4) >> 'a',
            Some(...) >> 'b',
            6,
            7,
            8,
            9,
        ])
        self.assertTrue(result)
        self.assertEqual([2, 3, 4, 5], result.a)
        self.assertEqual([], result.b)
        self.assertEqual("MatchResult(matches=True, groups={'a': [2, 3, 4, 5], 'b': []})", repr(result))

    def test_subsequence(self):
        result = match(range(1, 5), [
            1,
            Some(
                2,
                3,
            ),
            4,
        ])
        self.assertTrue(result)

    def test_repeating_subsequence(self):
        result = match(range(1, 7), [
            1,
            Some(
                OneOf(2, 4),
                OneOf(3, 5),
            ),
            6,
        ])
        self.assertTrue(result)

    def test_repeating_subsequence_exactly(self):
        result = match(range(1, 7), [
            1,
            Some(
                OneOf(2, 4),
                OneOf(3, 5),
                exactly=2,
            ),
            6,
        ])
        self.assertTrue(result)

    def test_repeating_subsequence_exactly_stop(self):
        result = match(range(1, 7), [
            1,
            Some(
                OneOf(2, 4),
                OneOf(3, 5),
                exactly=1,
            ),
            4,
            5,
            6,
        ])
        self.assertTrue(result)

    def test_repeating_subsequence_exactly_stop_with_captures(self):
        result = match(range(1, 7), [
            1,
            "many" @ Some(
                OneOf(2, 4),
                OneOf(3, 5),
                exactly=1,
            ),
            4,
            5,
            6,
        ])
        self.assertTrue(result)
        self.assertEqual([[2, 3]], result['many'])

    def test_repeating_subsequence_at_most_stop_with_captures(self):
        result = match(range(1, 9), [
            1,
            "many" @ Some(
                OneOf(2, 4, 6),
                OneOf(3, 5, 7),
                at_most=2,
            ),
            6,
            7,
            8,
        ])
        self.assertTrue(result)
        self.assertEqual([[2, 3], [4, 5]], result['many'])

    def test_repeating_subsequence_at_most_stop_with_captures_unhappy_path(self):
        result = match(range(1, 9), [
            1,
            "many" @ Some(
                OneOf(2, 4, 6),
                OneOf(3, 5, 7),
                at_most=2,
            ),
            6,
            7,
        ])
        self.assertFalse(result)

    def test_subsequence_with_captures(self):
        result = match(range(1, 5), [
            "quuz" @ Value(1),
            "quux" @ Some(
                "foo" @ Value(2),
                "bar" @ Value(3),
            ),
            "qux" @ Value(4),
        ])
        self.assertTrue(result)
        self.assertEqual(1, result['quuz'])
        self.assertEqual([[2, 3]], result['quux'])
        self.assertEqual(2, result['foo'])
        self.assertEqual(3, result['bar'])
        self.assertEqual(4, result['qux'])

    def test_repeating_subsequence_with_captures(self):
        result = match(range(1, 7), [
            "quuz" @ Value(1),
            "quux" @ Some(
                "foo" @ OneOf(2, 4),
                "bar" @ OneOf(3, 5),
            ),
            "qux" @ Value(6),
        ])
        self.assertTrue(result)
        self.assertEqual(1, result['quuz'])
        self.assertEqual([[2, 3], [4, 5]], result['quux'])
        self.assertEqual(4, result['foo'])
        self.assertEqual(5, result['bar'])
        self.assertEqual(6, result['qux'])

    def test_repeating_subsequence_distinction_from_list_items(self):
        subsequences = [0, 1, 2, 1, 2, 3]
        sublists = [0, [1, 2], [1, 2], 3]
        pattern_subsequences = [0, Some(1, 2), 3]
        pattern_sublists = [0, Some([1, 2]), 3]
        self.assertTrue(match(subsequences, pattern_subsequences))
        self.assertFalse(match(subsequences, pattern_sublists))
        self.assertTrue(match(sublists, pattern_sublists))
        self.assertFalse(match(sublists, pattern_subsequences))

    def test_docstring_examples(self):
        self.assertTrue(match([0, 1, 2, 1, 2, 3], [0, Some(1, 2), 3]))
        result = match(range(1, 10), ['123' @ Many(Between(0, 3)), 'xs' @ Remaining()])
        self.assertTrue(result)
        self.assertEqual([1, 2, 3], result['123'])
        self.assertEqual([4, 5, 6, 7, 8, 9], result['xs'])

    def test_subsequence_not_matching(self):
        self.assertTrue(match([0, 1, 2, 2, 1, 2, 2, 4], [0, Some(1, Some(2, 2, at_least=1), at_least=2), 4]))

    def test_subsequence_not_matching_unhappy_path(self):
        self.assertFalse(match([0, 1, 2, 2, 1, 2, 3, 4], [0, Some(1, Some(2, 2, at_least=1), at_least=2), 4]))
