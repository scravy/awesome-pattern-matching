from __future__ import annotations

import typing as ty
import unittest

from apm import *


# noinspection PyProtectedMember


class UtilTests(unittest.TestCase):

    def test_some(self):
        self.assertTrue(isinstance(Some(), ty.Hashable))
