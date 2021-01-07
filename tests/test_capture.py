from __future__ import annotations

import unittest

from apm import *


class CaptureTest(unittest.TestCase):

    def test_multi_capture(self):
        self.assertTrue(result := match(
            value=[{
                "first-name": "Jane",
                "last-name": "Doe",
            }, {
                "first-name": "John",
                "last-name": "Doe",
            }],
            pattern=Each({"first-name": Capture(..., name="first_names")})
        ))
        self.assertEqual(["Jane", "John"], result['first_names'])

    def test_last_capture(self):
        self.assertTrue(result := match(
            multimatch=False,
            value=[{
                "first-name": "Jane",
                "last-name": "Doe",
            }, {
                "first-name": "John",
                "last-name": "Doe",
            }],
            pattern=Each({"first-name": Capture(..., name="first_name")})
        ))
        self.assertEqual("John", result['first_name'])
