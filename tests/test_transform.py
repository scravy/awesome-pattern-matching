from __future__ import annotations

import unittest
from itertools import chain, combinations, permutations

from apm import *
from apm.core import transform


def powerset(it):
    s = list(it)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def identity(x):
    return x


def record_type(s):
    def f(x):
        s.add(type(x))
        return x
    return f


class TransformTest(unittest.TestCase):

    def test_transform(self):
        ps0 = (
            Regex(r".+"),
            OneOf("foo", "bar"),
            AllOf("foo", "bar"),
            Either("foo", "bar"),
            [1, 2, 3],
            "foo",
            1.0,
        )
        ts = (
            Not,
            Strict,
            lambda pat: Transformed(identity, pat),
            lambda pat: Capture(pat, name="qux"),
        )
        ps = [
            AllOf(*ps0),
            OneOf(*ps0),
            NoneOf(*ps0),
        ]
        for p in ps0:
            for fs in powerset(ts):
                for fsp in permutations(fs):
                    pp = p
                    for f in fsp:
                        pp = f(pp)
                    ps.append(pp)

        for p in ps:
            types = set()
            t = transform(p, record_type(types))
            self.assertEqual(p, t)
            self.assertNotEqual(p, transform(p, lambda x: Not(x)))
            # since we already invested so much time into building combinations of patterns,
            # check that match does not error out (this will sometimes even match due to Not(...))
            self.assertEqual(Not in types, bool(match(None, t)))
