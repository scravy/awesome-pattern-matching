from __future__ import annotations

import unittest
from typing import Callable

from apm import *


class AggregationsTest(unittest.TestCase):

    def test_agg_set(self):
        result = match([
            'foo',
            3,
            'bar',
            10,
            -4,
            'foo',
            'bar',
            17,
        ], Each(OneOf(InstanceOf(str) >> agg.Set('strings'), ...)))
        self.assertTrue(result)
        self.assertEqual(result.strings, {'foo', 'bar'})

    def test_agg_list(self):
        result = match([
            'foo',
            3,
            'bar',
            10,
            -4,
            'foo',
            'bar',
            17,
        ], Each(OneOf(InstanceOf(str) >> agg.List('strings'), ...)))
        self.assertTrue(result)
        self.assertEqual(result.strings, ['foo', 'bar', 'foo', 'bar'])

    def test_agg_count(self):
        result = match([
            1,
            2,
            3.0,
            4,
            5.0,
        ], Each(OneOf(
            InstanceOf(int) >> agg.Count('integers'),
            InstanceOf(float) >> agg.Count('floats'),
        )))
        self.assertTrue(result)
        self.assertEqual(3, result.integers)
        self.assertEqual(2, result.floats)

    def test_agg_histogram(self):
        result = match([
            'a', 'b', 'c', 'b', 'd', 'c', 'a', 'a', 'c', 'a'
        ], Each(_ >> agg.Histogram('histo')))
        self.assertTrue(result)
        self.assertEqual({
            'a': 4,
            'b': 2,
            'c': 3,
            'd': 1,
        }, result.histo)

    def test_agg_sum(self):
        lower = 1
        upper = 10
        result = match(range(lower, upper), Each(_ >> agg.Sum('sum')))
        length = upper - lower
        self.assertTrue(result)
        self.assertEqual(length * (length + 1) // 2, result.sum)

    def test_agg_float_sum(self):
        result = match(['1', '10.3'], Each(_ >> agg.Sum('sum')))
        self.assertTrue(result)
        self.assertEqual(11.3, result.sum)

    def test_some_more_complicated_pattern(self):
        class Recursive(Pattern):
            def __init__(self, p: Callable):
                self._pattern = p

            def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
                return ctx.match(value, self._pattern())

        numbers = agg.Set()
        pattern = OneOf(InstanceOf(int) >> numbers, EachItem(..., Recursive(lambda: pattern)))

        result = match({
            'a': {'b': 3},
            'c': 7,
            'd': {'e': {}},
            'f': {'g': {'h': 10, 'i': 7}},
        }, pattern)
        self.assertTrue(result)
        self.assertEqual({3, 7, 10}, numbers.value)

    def test_some_more_complicated_pattern_with_nothing_in_it(self):
        class Recursive(Pattern):
            def __init__(self, p: Callable):
                self._pattern = p

            def match(self, value, *, ctx: MatchContext, strict: bool) -> MatchResult:
                return ctx.match(value, self._pattern())

        numbers = agg.Set()
        pattern = OneOf(InstanceOf(float) >> numbers, InstanceOf(int), EachItem(..., Recursive(lambda: pattern)))

        result = match({
            'a': {'b': 3},
            'c': 7,
            'd': {'e': {}},
            'f': {'g': {'h': 10, 'i': 7}},
        }, pattern)
        self.assertTrue(result)
        self.assertEqual(set(), numbers.value)
