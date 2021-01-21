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
            Each(SubclassOf(int)),
            EachItem(InstanceOf(str), SubclassOf(type)),
            Parameters(int, k=str),
            Items(foo=17),
            Attrs(bar=117),
            At(path=["foo", "bar"], pattern=...),
            Arguments(foo=int, bar=float),
            Returns(str),
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
            expected_to_match = Not in types
            self.assertEqual(expected_to_match, bool(match(None, t)))
            # also do a check for captureall=, which is using a more fancy transform
            results = {}
            self.assertEqual(expected_to_match, bool(match(None, p, captureall=results)))
            if expected_to_match:
                self.assertTrue(bool(results))

    def test_some_transform(self):
        pt0 = (1, Many(...), 3)
        pt1 = transform(pt0, lambda x: x)
        self.assertEqual(pt0, pt1)

    def test_string_transform(self):
        pt0 = String("a", "b", "c")
        pt1 = transform(pt0, lambda x: x)
        self.assertEqual(pt0, pt1)

    def test_fancy_transform(self):
        # noinspection PyDefaultArgument
        def generate_name(static={'count': 0}):
            static['count'] += 1
            return f"n{static['count']}"

        pattern = (1, Many(...), 3)
        transformed = transform(pattern, lambda x: Capture(x, name=generate_name()))
        result = match((1, 2, 3), transformed)
        self.assertTrue(result)
        self.assertEqual({
            'n1': 1,
            'n2': 2,
            'n3': [2],
            'n4': 3,
            'n5': (1, 2, 3),
        }, result.groups())
