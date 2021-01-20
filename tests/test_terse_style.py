from __future__ import annotations

import re
import unittest
from dataclasses import dataclass

from apm import *


class TerseStyleTest(unittest.TestCase):

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
        self.assertEqual(
            ('details', 3),
            match(
                pet,
                {_ >> 'key': {'age': _}}, lambda a, b: (a, b)
            )
        )

    def test_match_class_hierarchies(self):
        class Animal:
            pass

        class Hippo(Animal):
            pass

        class Zebra(Animal):
            pass

        class Horse(Animal):
            pass

        def what_is(x):
            return match(x,
                         Hippo, 'hippo',
                         Zebra, 'zebra',
                         Animal, 'some other animal',
                         _, 'not at all an animal',
                         )

        self.assertEqual('zebra', what_is(Zebra()))
        self.assertEqual('hippo', what_is(Hippo()))
        self.assertEqual('some other animal', what_is(Horse()))
        self.assertEqual('some other animal', what_is(Animal()))
        self.assertEqual('not at all an animal', what_is(42))

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

    def test_regex(self):
        def what_is(pet):
            return match(pet,
                         re.compile(r'(\w+)-(\w+)-cat$'), lambda name, my: 'cat ' + name,
                         re.compile(r'(\w+)-(\w+)-dog$'), lambda name, my: 'dog ' + name,
                         _, "something else"
                         )

        self.assertEqual('dog fuffy', what_is('fuffy-my-dog'))
        self.assertEqual('dog puffy', what_is('puffy-her-dog'))
        self.assertEqual('cat carla', what_is('carla-your-cat'))
        self.assertEqual('something else', what_is('roger-my-hamster'))

    def test_lambda_with_too_little_parameters(self):
        self.assertEqual("anything", match(1, _, lambda: "anything"))

    def test_lambda_with_too_many_parameters(self):
        self.assertEqual("anything(1, None, None)", match(1, _, lambda a, b, c: f"anything({a}, {b}, {c})"))

    def test_default_value(self):
        self.assertEqual("fallback", match(1, 2, lambda: "something", "fallback"))

    def test_default_action(self):
        self.assertEqual("fallback", match(1, 2, lambda: "something", lambda: "fallback"))
