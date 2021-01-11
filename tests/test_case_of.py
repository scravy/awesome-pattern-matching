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

    def test_case_of_default(self):
        result = case({"Id": "h23ksad8", "Name": "ObjectName"}) \
            .of({"Id": Capture(Regex("[0-9]+"), name='id')}, "numeric") \
            .otherwise("non-numeric")
        self.assertEqual("non-numeric", result)
