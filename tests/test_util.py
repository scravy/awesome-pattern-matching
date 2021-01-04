import unittest

import apm._util as util
from apm import *


class TypingUtil(unittest.TestCase):

    def test_get_arg_types(self):
        # noinspection PyUnusedLocal
        def f(a: int, b: float, c: str, d: str) -> str:
            pass

        arg_types = util.get_arg_types(f)
        self.assertTrue(match(
            arg_types,
            [int, float, Remaining(str)]
        ))
