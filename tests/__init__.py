import unittest

from apm import *
from apm.patterns import *
from apm.util import get_arg_types


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


class ReadmeExamples(unittest.TestCase):

    def test_record_example(self):
        record = {
            "ID": 9340,
            "First-Name": "Jane",
            "Last-Name": "Doe",
        }

        self.assertTrue(result := match(record, {"First-Name": Capture(Regex("[A-Z][a-z]*"), name="name")}))
        self.assertEqual("Jane", result['name'])

    def test_records_example(self):
        records = [
            {
                "Foo": 1,
                "Bar": "Quux"
            },
            {
                "Foo": 2,
                "Bar": "Baz"
            }
        ]

        self.assertTrue(
            match(records, Each(Strict({"Foo": InstanceOf(int), "Bar": InstanceOf(str) & Regex("[A-Z][a-z]+")}))))

        records = [
            {
                "Foo": 1,
                "Bar": "Quux"
            },
            {
                "Foo": 2,
                "Bar": "Baz",
                "Strict": "Does not allow unknown keys"
            }
        ]

        self.assertFalse(
            match(records, Each(Strict({"Foo": InstanceOf(int), "Bar": InstanceOf(str) & Regex("[A-Z][a-z]+")}))))

        records = [
            {
                "Foo": 1,
                "Bar": "Quux"
            },
            {
                "Foo": 2,
                "Bar": "Baz",
                "No Problem": "When Not Strict"
            }
        ]

        self.assertTrue(match(records, Each({"Foo": InstanceOf(int), "Bar": InstanceOf(str) & Regex("[A-Z][a-z]+")})))

    def test_user_guide_examples(self):
        some_very_complex_object = {
            "A": 1,
            "B": 2,
            "C": 3,
        }
        self.assertTrue(match(some_very_complex_object, {"C": 3}))
        self.assertFalse(match(some_very_complex_object, Strict({"C": 3})))

        ls = [1, 2, 3]
        self.assertTrue(match(ls, [1, 2, 3]))
        self.assertFalse(match(ls, [1, 2]))
        self.assertFalse(match(ls, [1, 2, 3, 4]))
        self.assertTrue(match(ls, [1, 2, Remaining(InstanceOf(int))]))
        self.assertTrue(match(ls, Each(InstanceOf(int))))
        self.assertTrue(match(ls, Each(InstanceOf(int) & Between(1, 3))))
        self.assertTrue(match(ls, [1, Remaining(..., at_least=2)]))

        self.assertTrue(result := match([1, 2, 3, 4], [1, 2, Capture(Remaining(InstanceOf(int)), name='tail')]))
        self.assertEqual([3, 4], result['tail'])
        self.assertTrue(match(range(1, 10), Each(Between(1, 9))))
        self.assertTrue(match("quux", OneOf("bar", "baz", "quux")))

        def f(x: int, y: float, z):
            ...

        self.assertTrue(match(f, Arguments(int, float, None)))

        def g(x: int) -> str:
            ...

        self.assertTrue(match(g, Arguments(int) & Returns(str)))

        def sha256(v: str) -> str:
            import hashlib
            return hashlib.new('sha256', v.encode('utf8')).hexdigest()

        self.assertTrue(
            match("hello", Transformed(sha256, "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824")))

        self.assertTrue(match({"a": 3, "b": 7}, {"a": ...}))
        self.assertTrue(match(3.0, 3))

        self.assertFalse(match({"a": 3, "b": 7}, Strict({"a": ...})))
        self.assertFalse(match(3.0, Strict(3)))

        class Min(Pattern):
            # noinspection PyShadowingBuiltins
            def __init__(self, min):
                self.min = min

            def match(self, value, *, ctx: MatchContext, strict=False) -> MatchResult:
                return ctx.match_if(value >= self.min)

        self.assertTrue(match(3, Min(1)))
        self.assertFalse(match(3, Min(5)))


if __name__ == '__main__':
    unittest.main()
