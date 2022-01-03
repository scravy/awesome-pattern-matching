from __future__ import annotations

import unittest
from enum import Enum, auto
from typing import Tuple

from apm import *


class Button(Enum):
    LEFT = auto()
    MIDDLE = auto()
    RIGHT = auto()


class Click:
    __match_args__ = ("position", "button")

    def __init__(self, pos: Tuple[int, int], btn: Button):
        self.position: Tuple[int, int] = pos
        self.button: Button = btn


class ObjectPatternTest(unittest.TestCase):

    def test_empty(self):
        self.assertFalse(match({}, Object(Click)))
        self.assertTrue(match(Click((1, 2), Button.LEFT), Object(Click)))

    def test_match_args(self):
        self.assertTrue(match(Click((1, 2), Button.LEFT), Object(Click, (1, 2))))
        self.assertTrue(match(Click((1, 2), Button.LEFT), Object(Click, (1, 2), Button.LEFT)))
        self.assertTrue(match(Click((1, 2), Button.LEFT), Object(Click, (1, 2), button=Button.LEFT)))
        self.assertFalse(match(Click((1, 2), Button.LEFT), Object(Click, (1, 2), button=Button.RIGHT)))
