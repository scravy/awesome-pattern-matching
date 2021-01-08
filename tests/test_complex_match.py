from __future__ import annotations

import unittest

from apm import *


class ComplexMatchTest(unittest.TestCase):

    def test_fibonacci(self):
        def fibonacci(n):
            return match(n,
                         1, 1,
                         2, 1,
                         _, lambda x: fibonacci(x-1) + fibonacci(x-2)
                         )
        self.assertEqual(1, fibonacci(1))
        self.assertEqual(1, fibonacci(2))
        self.assertEqual(2, fibonacci(3))
        self.assertEqual(3, fibonacci(4))
        self.assertEqual(5, fibonacci(5))
        self.assertEqual(8, fibonacci(6))
