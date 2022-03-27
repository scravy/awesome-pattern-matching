from __future__ import annotations

import unittest
import typing as ty

from apm import *


class Expression:
    pass


class DataFrame:
    pass


class ParametersTests(unittest.TestCase):

    def test_partly_no_annotations(self):

        def as_column(exp: Expression, pattern, ignore_case=True, *, df: ty.Optional[DataFrame] = None):
            pass

        self.assertTrue(match(as_column, Parameters(Expression, Remaining(_), df=ty.Optional[DataFrame])))
        self.assertTrue(match(as_column, Parameters(Expression, ..., ..., df=ty.Optional[DataFrame])))
        self.assertFalse(match(as_column, Parameters(Expression, ..., df=ty.Optional[DataFrame])))

    def test_any(self):
        def f(x: ty.Any, y: int, z):
            pass

        self.assertTrue(match(f, Parameters(ty.Any, int, ...)))
        self.assertFalse(match(f, Parameters(ty.Any, ty.Any, ...)))
        self.assertTrue(match(f, Parameters(ty.Any, ..., ...)))

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

        def f6(s: str, *, x: float, y: float):
            pass

        assertions = {
            Parameters(int, float): {
                f1: True,
                f2: False,
                f3: False,
                f4: False,
                f5: False,
                f6: False,
            },
            Parameters(float, float): {
                f1: False,
                f2: True,
                f3: False,
                f4: False,
                f5: False,
                f6: False,
            },
            Parameters(int, float, float): {
                f1: False,
                f2: False,
                f3: True,
                f4: False,
                f5: False,
                f6: False,
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
                f6: False,
            },
            Parameters(VarArgs(int), y=float, z=float): {
                f1: False,
                f2: False,
                f3: False,
                f4: True,
                f5: False,
                f6: False,
            },
            Parameters(x=float, y=float): {
                f1: False,
                f2: False,
                f3: False,
                f4: False,
                f5: True,
                f6: False,
            },
            Parameters(Some(_), x=float): {
                f1: False,
                f2: False,
                f3: False,
                f4: False,
                f5: True,
                f6: True,
            },
            Strict(Parameters(Some(_), x=float)): {
                f1: False,
                f2: False,
                f3: False,
                f4: False,
                f5: False,
                f6: False,
            },
            Strict(Parameters(Some(_), x=float, y=float)): {
                f1: False,
                f2: False,
                f3: False,
                f4: False,
                f5: True,
                f6: True,
            },
            Strict(Parameters(Some(_, at_least=1), x=float, y=float)): {
                f1: False,
                f2: False,
                f3: False,
                f4: False,
                f5: False,
                f6: True,
            },
        }

        for pattern, funcs in assertions.items():
            for func, assertion in funcs.items():
                result = bool(match(func, pattern))
                self.assertEqual(assertion, result,
                                 msg=f"{func.__name__} vs. {repr(pattern)} -> {result}, expected: {assertion}")
