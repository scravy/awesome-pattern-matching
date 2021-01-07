from __future__ import annotations

import unittest

from apm import *


class TryMatchTest(unittest.TestCase):

    def test_try_match(self):
        result = None
        try:
            match({
                "id": "h23ksad8",
                "name": "ObjectName"
            })
        except Case({"id": Regex("[A-Z0-9]+")}):
            result = 'upper'
        except Case({"id": Regex("[a-z0-9]+")}):
            result = 'lower'
        finally:
            self.assertEqual(result, 'lower')
