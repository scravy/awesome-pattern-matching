import unittest

from apm import *


# noinspection PyUnusedLocal
def f(x: int, *xs: int, z: str = None, **kwargs):
    pass


# noinspection PyUnusedLocal
def g(a: str, m: float, n: float, z: int):
    pass


class TypeFooTest(unittest.TestCase):
    def test_parameters(self):
        self.assertTrue(match(f, Parameters(_, _, _, z=_)))
        self.assertFalse(match(f, Parameters(_, _, _, x=_)))

    def test_parameter_patterns(self):
        self.assertTrue(match(f, Parameters(int, VarArgs, KwArgs)))
        self.assertFalse(match(f, Parameters(int, KwArgs)))
        self.assertTrue(match(f, Parameters(int, VarArgs(int), KwArgs)))
        self.assertFalse(match(f, Parameters(int, VarArgs(float), KwArgs)))
        self.assertFalse(match(g, Parameters(str, float, float, VarArgs(int))))

    def test_some(self):
        pat = Parameters(str, Many(float), int)
        self.assertTrue(match(g, pat))
        self.assertFalse(match(f, pat))


if __name__ == '__main__':
    unittest.main()
