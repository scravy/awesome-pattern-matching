import unittest

from apm import *


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

        # noinspection PyUnusedLocal
        def f(x: int, y: float, z):
            ...

        self.assertTrue(match(f, Arguments(int, float, None)))

        # noinspection PyUnusedLocal
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
