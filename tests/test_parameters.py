from __future__ import annotations

import unittest

from apm import *


# noinspection PyProtectedMember


class ParametersTests(unittest.TestCase):

    def test_parameters(self):
        def f1(x: int, y: float):
            pass

        def f2(x: float, y: float):
            pass

        def f3(x: int, y: float, z: float):
            pass

        def f4(*x: int, y: float, z: float):
            pass

        def f5(*, x: float, y: float):
            pass

        assertions = {
            Parameters(int, float): {
                f1: True,
                f2: False,
                f3: False,
                f4: False,
                f5: False,
            },
            Parameters(float, float): {
                f1: False,
                f2: True,
                f3: False,
                f4: False,
                f5: False,
            },
            Parameters(int, float, float): {
                f1: False,
                f2: False,
                f3: True,
                f4: False,
                f5: False,
            },
            Parameters(int, Remaining(float)): {
                f1: True,
                f2: False,
                f3: True,
                f4: True,
                f5: False,
            },
            Parameters(VarArgs, y=float, z=float): {
                f1: False,
                f2: False,
                f3: False,
                f4: True,
                f5: False,
            },
            Parameters(VarArgs(int), y=float, z=float): {
                f1: False,
                f2: False,
                f3: False,
                f4: True,
                f5: False,
            },
            Parameters(x=float, y=float): {
                f1: False,
                f2: False,
                f3: False,
                f4: False,
                f5: True,
            }
        }

        for pattern, funcs in assertions.items():
            for func, assertion in funcs.items():
                self.assertEqual(assertion, bool(match(func, pattern)))
