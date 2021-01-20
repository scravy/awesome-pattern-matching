from __future__ import annotations

import unittest

from apm import *


class TryMatchTest(unittest.TestCase):

    def test_try_match(self):
        result = None
        id_ = None
        try:
            match({
                "id": "h23ksad8",
                "name": "ObjectName"
            })
        except Case({"id": Capture(Regex("[A-Z0-9]+"), name='id')}):
            result = 'upper'
        except Case({"id": Capture(Regex("[a-z0-9]+"), name='id')}) as match_result:
            result = 'lower'
            id_ = match_result['id']
        finally:
            self.assertEqual('lower', result)
            self.assertEqual('h23ksad8', id_)

    def test_try_match_default(self):
        result = None
        try:
            match({
                "id": "h23ksad8",
                "name": "ObjectName"
            })
        except Case({"id": Regex("[A-Z0-9]+")}):
            result = 'upper'
        except Default:
            result = 'unknown'
        finally:
            self.assertEqual(result, 'unknown')
