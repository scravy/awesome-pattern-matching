from __future__ import annotations

import unittest

from apm import *


class CaseOfTest(unittest.TestCase):

    # noinspection PyShadowingBuiltins
    def test_case_of(self):
        result = case({"Id": "h23ksad8", "Name": "ObjectName"}) \
            .of({"Id": Capture(Regex("[A-Z0-9]+"), name='id')}, lambda id: id) \
            .of({"Id": Capture(Regex("[a-z0-9]+"), name='id')}, lambda id: id.upper()) \
            .otherwise("_")
        self.assertEqual("H23KSAD8", result)

    # noinspection PyShadowingBuiltins
    def test_case_of_constant(self):
        result = case({"Id": "h23ksad8", "Name": "ObjectName"}) \
            .of({"Id": Capture(Regex("[A-Z0-9]+"), name='id')}, "upper") \
            .of({"Id": Capture(Regex("[a-z0-9]+"), name='id')}, "lower") \
            .otherwise("non")
        self.assertEqual("lower", result)

    # noinspection PyShadowingBuiltins
    def test_case_of_default_action(self):
        result = case({"Id": "23892", "Name": "ObjectName"}) \
            .of({"Id": Regex("[A-Z][a-z0-9]*")}, "upper") \
            .of({"Id": Regex("[a-z][a-z0-9]*")}, "lower") \
            .otherwise(lambda: "something else")
        self.assertEqual("something else", result)

    def test_case_of_default(self):
        result = case({"Id": "h23ksad8", "Name": "ObjectName"}) \
            .of({"Id": Capture(Regex("[0-9]+"), name='id')}, "numeric") \
            .otherwise("non-numeric")
        self.assertEqual("non-numeric", result)
