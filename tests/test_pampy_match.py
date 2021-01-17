from __future__ import annotations

import unittest
from dataclasses import dataclass

from apm import *


class ComplexMatchTest(unittest.TestCase):

    def test_fibonacci(self):
        def fibonacci(n):
            return match(n,
                         1, 1,
                         2, 1,
                         _, lambda x: fibonacci(x - 1) + fibonacci(x - 2)
                         )

        self.assertEqual(1, fibonacci(1))
        self.assertEqual(1, fibonacci(2))
        self.assertEqual(2, fibonacci(3))
        self.assertEqual(3, fibonacci(4))
        self.assertEqual(5, fibonacci(5))
        self.assertEqual(8, fibonacci(6))

    def test_underscore_as_key(self):
        pet = {'type': 'dog', 'details': {'age': 3}}

        self.assertEqual(
            3,
            match(
                pet,
                {'details': {'age': _}}, lambda age: age
            )
        )
        self.assertEqual(
            ('details', 3),
            match(
                pet,
                {_: {'age': _}}, lambda a, b: (a, b)
            )
        )

    def test_match_class_hierarchies(self):
        class Pet:
            pass

        class Dog(Pet):
            pass

        class Cat(Pet):
            pass

        class Hamster(Pet):
            pass

        def what_is(x):
            return match(x,
                         Dog, 'dog',
                         Cat, 'cat',
                         Pet, 'any other pet',
                         _, 'this is not a pet at all',
                         )

        self.assertEqual('cat', what_is(Cat()))
        self.assertEqual('dog', what_is(Dog()))
        self.assertEqual('any other pet', what_is(Hamster()))
        self.assertEqual('any other pet', what_is(Pet()))
        self.assertEqual('this is not a pet at all', what_is(42))

    def test_dataclasses(self):
        @dataclass
        class Pet:
            name: str
            age: int

        pet = Pet('rover', 7)

        self.assertEqual(7, match(pet, Pet('rover', _), lambda age: age))
        self.assertEqual('rover', match(pet, Pet(_, 7), lambda name: name))
        self.assertEqual(('rover', 7), match(pet, Pet(_, _), lambda name, age: (name, age)))

    def test_so_many_things(self):
        expectations = [
            (3, "this matches the number 3"),
            (4, "matches any integer"),
            (("k", 2), "a tuple (a, b) you can use in a function"),
            ([1, 2, 7], "any list of 3 elements that begins with [1, 2]"),
            ({'x': 3}, "any dict with a key 'x' and any value associated"),
            ({'x': 4, 'y': 4}, "any dict with a key 'x' and any value associated"),
            ("xyz", "anything else"),
        ]

        for val, expected in expectations:
            result = match(val,
                           3, "this matches the number 3",
                           int, "matches any integer",
                           (str, int), lambda a, b: "a tuple (a, b) you can use in a function",
                           [1, 2, _], "any list of 3 elements that begins with [1, 2]",
                           {'x': _}, "any dict with a key 'x' and any value associated",
                           _, "anything else"
                           )
            self.assertEqual(expected, result)
