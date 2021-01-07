from __future__ import annotations

import unittest

from apm import *


class BasicUseCases(unittest.TestCase):

    def test_dict(self):
        self.assertTrue(match(
            {"foo": 1, "bar": 2, "baz": 3, "quux": 4},
            {"foo": 1}
        ))
        self.assertFalse(match(
            {"foo": 1, "bar": 2, "baz": 3, "quux": 4},
            Strict({"foo": 1})
        ))
        positive_number = InstanceOf(int) & Check(lambda v: v >= 0)
        self.assertTrue(match(
            {"foo": 1, "bar": 2},
            Strict({"foo": positive_number, "bar": positive_number})
        ))

    def test_tuple(self):
        self.assertTrue(match(
            (1, 2),
            (..., ...)
        ))

    def test_strict(self):
        self.assertTrue(match(1, 1.0))
        self.assertTrue(match(1.0, Strict(1.0)))
        self.assertTrue(match(1, Strict(1)))
        self.assertFalse(match(1, Strict(1.0)))

    def test_truish(self):
        self.assertTrue(match(1, Truish()))
        self.assertTrue(match(2.9, Truish()))
        self.assertFalse(match("", Truish()))

    def test_length(self):
        self.assertTrue(match([], Length(0)))
        self.assertTrue(match(('abc',), Length(1)))
        self.assertTrue(match('abc', Length(3)))

    def test_contains(self):
        self.assertTrue(match([1, 2, 3], Contains(2) & Contains(3)))
        self.assertTrue(match((1, 2, 3), Contains(2) & Contains(3)))
        self.assertTrue(match({1, 2, 3}, Contains(2) & Contains(3)))
        self.assertTrue(match({1: 'a', 2: 'b', 3: 'c'}, Contains(2) & Contains(3)))
        self.assertTrue(match("quux", Contains('uu')))

    def test_regex(self):
        self.assertTrue(match(
            "Hello, World!",
            Regex("[A-Z][a-z]+, [A-Z][a-z]+!")
        ))
        self.assertFalse(match(
            "Hello, World! How are you today?",
            Regex("[A-Z][a-z]+, [A-Z][a-z]+!")
        ))
        self.assertTrue(match(
            "Hello, World! How are you today?",
            Regex("[A-Z][a-z]+, [A-Z][a-z]+!.*")
        ))

    def test_remaining(self):
        self.assertTrue(match(
            [1, 2, 3, 4],
            [1, 2, 3, Remaining(InstanceOf(int), at_least=1)]))
        self.assertTrue(match(
            [1, 2, 3],
            [1, 2, 3, Remaining(InstanceOf(int))]))
        self.assertTrue(match(
            [1, 2, 3, 4, 5],
            [1, 2, 3, Remaining(InstanceOf(int) & Between(1, 10))]))
        self.assertFalse(match(
            [1, 2, 3, 4, 5],
            [1, 2, 3, Remaining(InstanceOf(int) & Between(1, 3))]))
        self.assertFalse(match(
            [1, 2, 3, 4],
            [1, 2, 3, Remaining(InstanceOf(int), at_least=2)]))

    def test_remaining_with_range(self):
        self.assertTrue(match(
            range(1, 5),
            [1, 2, 3, Remaining(InstanceOf(int), at_least=1)]))
        self.assertTrue(match(
            range(1, 4),
            [1, 2, 3, Remaining(InstanceOf(int))]))
        self.assertTrue(match(
            range(1, 5),
            [1, 2, 3, Remaining(InstanceOf(int) & Between(1, 10))]))
        self.assertFalse(match(
            range(1, 5),
            [1, 2, 3, Remaining(InstanceOf(int) & Between(1, 3))]))
        self.assertFalse(match(
            range(1, 5),
            [1, 2, 3, Remaining(InstanceOf(int), at_least=2)]))

    def test_capture(self):
        self.assertTrue(result := match(
            {
                "This": "Is A Rather Complex Beast",
                "Created-At": "Sun Jan  3 04:08:57 CET 2021",
                "User": {
                    "UserId": 102384,
                    "FirstName": "Jane",
                    "LastName": "Doe",
                }
            },
            {
                "User": Capture({
                    "FirstName": Capture(..., name="first_name"),
                    "LastName": Capture(..., name="last_name"),
                }, name="user")
            }
        ))
        self.assertEqual("Jane", result['first_name'])
        self.assertEqual("Doe", result['last_name'])
        self.assertEqual(102384, result['user']['UserId'])

    def test_remaining_with_capture(self):
        self.assertTrue(result := match(
            [1, 2, 3, 4],
            [1, 2, Capture(Remaining(...), name="tail")]
        ))
        self.assertEqual([3, 4], result['tail'])

    def test_and(self):
        self.assertFalse(match(
            0,
            Between(0, 1) & Between(1, 2)
        ))
        self.assertTrue(match(
            1,
            Between(0, 1) & Between(1, 2)
        ))
        self.assertFalse(match(
            2,
            Between(0, 1) & Between(1, 2)
        ))

    def test_or(self):
        self.assertTrue(match(
            0,
            Between(0, 1) | Between(1, 2)
        ))
        self.assertTrue(match(
            1,
            Between(0, 1) | Between(1, 2)
        ))
        self.assertTrue(match(
            2,
            Between(0, 1) | Between(1, 2)
        ))

    def test_xor(self):
        self.assertTrue(match(
            0,
            Between(0, 1) ^ Between(1, 2)
        ))
        self.assertFalse(match(
            1,
            Between(0, 1) ^ Between(1, 2)
        ))
        self.assertTrue(match(
            2,
            Between(0, 1) ^ Between(1, 2)
        ))

    def test_each(self):
        self.assertTrue(match([1, 2, 3], Each(InstanceOf(int))))
        self.assertFalse(match([1, 2.0, 3], Each(InstanceOf(int))))

    def test_each_item(self):
        pattern = EachItem(Regex("[a-z]+"), InstanceOf(int))
        self.assertTrue(match({"a": 1, "b": 2}, pattern))
        self.assertFalse(match({"_a": 1, "b": 2}, pattern))

    def test_transformed(self):
        self.assertTrue(match("value", Transformed(len, 5)))

    def test_arguments(self):
        # noinspection PyUnusedLocal
        def f(x: int, y: str):
            pass

        # noinspection PyUnusedLocal
        def g(x):
            pass

        # noinspection PyUnusedLocal
        def h(x, y: int, m: str, n: str):
            pass

        self.assertTrue(match(f, Arguments(int, str)))
        self.assertFalse(match(g, Arguments(int)))
        self.assertTrue(match(h, Arguments(None, int, Remaining(str))))

    def test_returns(self):
        def f() -> int:
            pass

        self.assertTrue(match(f, Returns(int)))
        self.assertFalse(match(f, Returns(float)))

    def test_at(self):
        record = {
            "foo": {
                "bar": {
                    "quux": {
                        "value": "deeply nested"
                    }
                }
            }
        }

        self.assertTrue(result := match(record, At("foo.bar.quux", {"value": Capture(..., name="value")})))
        self.assertEqual("deeply nested", result['value'])

        self.assertTrue(result := match(record, At(['foo', 'bar', 'quux'], {"value": Capture(..., name="value")})))
        self.assertEqual("deeply nested", result['value'])

        self.assertFalse(match(record, At("foo.bar.quux.baz", InstanceOf(int))))

    def test_string(self):
        path = "https://somehost/foo=1/bar=2/"

        self.assertTrue(result := match(path, String(
            Capture(OneOf("https", "http"), name="protocol"),
            "://",
            Capture(Regex("[a-zA-Z_-]+"), name="host"),
            Regex("/+"),
            "foo=",
            Capture(Regex("[^=/]+"), name="foo"),
            "/",
            "bar=",
            Capture(Regex("[^=/]+"), name="bar"),
            Regex("/*"),
        )))
        self.assertEqual("https", result['protocol'])
        self.assertEqual("somehost", result['host'])
        self.assertEqual("1", result['foo'])
        self.assertEqual("2", result['bar'])

    # noinspection PyUnresolvedReferences
    def test_string_argresult(self):
        path = "https://somehost/foo=1/bar=2/"

        self.assertTrue(result := match(path, String(
            Capture(OneOf("https", "http"), name="protocol"),
            "://",
            Capture(Regex("[a-zA-Z_-]+"), name="host"),
            Regex("/+"),
            "foo=",
            Capture(Regex("[^=/]+"), name="foo"),
            "/",
            "bar=",
            Capture(Regex("[^=/]+"), name="bar"),
            Regex("/*"),
        ), argresult=True))
        self.assertEqual("https", result.protocol)
        self.assertEqual("somehost", result.host)
        self.assertEqual("1", result.foo)
        self.assertEqual("2", result.bar)
