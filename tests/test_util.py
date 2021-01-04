import unittest

from apm import *
from apm.patterns import *


class TypingUtil(unittest.TestCase):

    def test_get_arg_types(self):
        # noinspection PyUnusedLocal
        def f(a: int, b: float, c: str, d: str) -> str:
            pass

        arg_types = get_arg_types(f)
        self.assertTrue(match(
            arg_types,
            [int, float, Remaining(str)]
        ))
