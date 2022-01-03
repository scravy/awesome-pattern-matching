from __future__ import annotations

import unittest
from dataclasses import dataclass

from apm import *


@dataclass
class Point:
    x: float
    y: float


class GuardedTest(unittest.TestCase):

    def test_guarded_expression(self):
        def characterize(point):
            return case(point) \
                .of(Point('x' @ _, 'y' @ _),
                    guarded(lambda x, y: x > y, lambda x, y: f"interesting case ({x}, {y})",
                            lambda x, y: x == y, "equal coordinates")) \
                .of(Point(3, 7), "that one point") \
                .otherwise("uninteresting")

        self.assertEqual(characterize(Point(3, 0)), "interesting case (3, 0)")
        self.assertEqual(characterize(Point(4, 4)), "equal coordinates")
        self.assertEqual(characterize(Point(3, 7)), "that one point")
        self.assertEqual(characterize(Point(2, 5)), "uninteresting")

    def test_guarded_terse_expression(self):
        def characterize(point):
            return match(
                point,
                Point('x' @ _, 'y' @ _), guarded(lambda x, y: x > y, lambda x, y: f"interesting case ({x}, {y})",
                                                 lambda x, y: x == y, "equal coordinates"),
                Point(3, 7), "that one point",
                "uninteresting")

        self.assertEqual(characterize(Point(3, 0)), "interesting case (3, 0)")
        self.assertEqual(characterize(Point(4, 4)), "equal coordinates")
        self.assertEqual(characterize(Point(3, 7)), "that one point")
        self.assertEqual(characterize(Point(2, 5)), "uninteresting")

    def test_guarded_expression_with_default(self):
        def characterize(point):
            return case(point) \
                .of(Point('x' @ _, 'y' @ _),
                    guarded(lambda x, y: x > y, lambda x, y: f"interesting case ({x}, {y})",
                            lambda x, y: x == y, "equal coordinates",
                            True, "uninteresting")) \
                .otherwise("no match")

        self.assertEqual(characterize(Point(3, 0)), "interesting case (3, 0)")
        self.assertEqual(characterize(Point(4, 4)), "equal coordinates")
        self.assertEqual(characterize(Point(3, 7)), "uninteresting")
        self.assertEqual(characterize((2, 5)), "no match")

    def test_guarded_terse_expression_with_default(self):
        def characterize(point):
            return match(
                point,
                Point('x' @ _, 'y' @ _), guarded(lambda x, y: x > y, lambda x, y: f"interesting case ({x}, {y})",
                                                 lambda x, y: x == y, "equal coordinates",
                                                 True, "uninteresting"),
                "no match")

        self.assertEqual(characterize(Point(3, 0)), "interesting case (3, 0)")
        self.assertEqual(characterize(Point(4, 4)), "equal coordinates")
        self.assertEqual(characterize(Point(3, 7)), "uninteresting")
        self.assertEqual(characterize((2, 5)), "no match")
