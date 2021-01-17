import unittest
from dataclasses import dataclass

from apm import *


class ReadmeExamples(unittest.TestCase):

    def test_first_example(self):
        # noinspection PyUnresolvedReferences
        result = match([1, 2, 3, 4, 5], [1, '2nd' @ _, '3rd' @ _, 'tail' @ Remaining(...)])
        if result:
            self.assertEqual(2, result['2nd'])
            self.assertEqual(3, result['3rd'])
            self.assertEqual([4, 5], result['tail'])

    def test_styles(self):
        value = 7

        invocations = 0

        def check(v):
            nonlocal invocations
            self.assertEqual("It's between 1 and 10", v)
            invocations += 1

        # The simple style
        if match(value, Between(1, 10)):
            check("It's between 1 and 10")
        elif match(value, Between(11, 20)):
            check("It's between 11 and 20")
        else:
            check("It's not between 1 and 20")

        # The expression style
        case(value) \
            .of(Between(1, 10), lambda: check("It's between 1 and 10")) \
            .of(Between(11, 20), lambda: check("It's between 11 and 20")) \
            .otherwise(lambda: check("It's not between 1 and 20"))

        # The statement style
        try:
            match(value)
        except Case(Between(1, 10)):
            check("It's between 1 and 10")
        except Case(Between(11, 20)):
            check("It's between 1 and 10")
        except Default:
            check("It's not between 1 and 20")

        self.assertEqual(3, invocations)

    def test_record_example(self):
        record = {
            "ID": 9340,
            "First-Name": "Jane",
            "Last-Name": "Doe",
        }

        result = match(record, {"First-Name": Capture(Regex("[A-Z][a-z]*"), name="name")})
        self.assertTrue(result)
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

        result = match([1, 2, 3, 4], [1, 2, Capture(Remaining(InstanceOf(int)), name='tail')])
        self.assertTrue(result)
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

    def test_none_of(self):
        self.assertTrue(match("string", ~OneOf("foo", "bar")))
        self.assertFalse(match("foo", ~OneOf("foo", "bar")))
        self.assertFalse(match("bar", ~OneOf("foo", "bar")))

    # noinspection PyUnresolvedReferences
    def test_multimatch(self):
        result = match([{'foo': 5}, 3, {'foo': 7}], Each(OneOf({'foo': 'item' @ _}, ...)), multimatch=True)
        if result:
            self.assertEqual([5, 7], result['item'])
        result = match([{'foo': 5}, 3, {'quux': 7, 'bar': 9}], Each(OneOf({'foo': 'item' @ _}, ...)), multimatch=True)
        if result:
            self.assertEqual([5], result['item'])
        result = match([{'foo': 5}, 3, {'foo': 7, 'bar': 9}], Each(OneOf({'foo': 'item' @ _}, ...)))
        if result:
            self.assertEqual(7, result['item'])

    def test_simple_style_example(self):
        value = {"a": 7, "b": "foo", "c": "bar"}
        result = match(value, EachItem(_, 'value' @ InstanceOf(str) | ...), multimatch=True)
        if result:
            self.assertEqual(["foo", "bar"], result['value'])

    def test_declarative_style_example(self):
        @case_distinction
        def fib(n: Match(OneOf(0, 1))):
            return n

        @case_distinction
        def fib(n):
            return fib(n - 2) + fib(n - 1)

        self.assertEqual(0, fib(0))
        self.assertEqual(1, fib(1))
        self.assertEqual(1, fib(2))
        self.assertEqual(2, fib(3))
        self.assertEqual(3, fib(4))
        self.assertEqual(5, fib(5))
        self.assertEqual(8, fib(6))

    def test_overload_example(self):
        from apm.overload import overload

        @overload
        def add(a: str, b: str):
            return "".join([a, b])

        @overload
        def add(a: int, b: int):
            return a + b

        # noinspection PyTypeChecker
        self.assertEqual("ab", add("a", "b"))
        self.assertEqual(3, add(1, 2))

    # noinspection PyUnresolvedReferences
    def test_statement_example(self):
        try:
            match({'user': 'some-user-id', 'first_name': "Jane", 'last_name': "Doe"})
        except Case({'first_name': 'first' @ _, 'last_name': 'last' @ _}) as result:
            user = f"{result['first']} {result['last']}"
        except Case({'user': 'user_id' @ _}) as result:
            user = f"#{result['user_id']}"
        except Default:
            user = "anonymous"
        # noinspection PyUnboundLocalVariable
        self.assertEqual("Jane Doe", user)

    def test_contains(self):
        self.assertTrue(match("hello there, world", Contains("there")))
        self.assertTrue(match([1, 2, 3], Contains(2) & Contains(3)))
        self.assertTrue(match({'foo': 1, 'bar': 2}, Contains('quux') | Contains('bar')))

    def test_dataclasses(self):
        @dataclass
        class User:
            first_name: str
            last_name: str

        value = User("Jane", "Doe")

        def check(v):
            self.assertEqual("Welcome, member of the Doe family!", v)

        if match(value, User(_, "Doe")):
            check("Welcome, member of the Doe family!")
        elif match(value, User(_, _)):
            check("Welcome, anyone!")
