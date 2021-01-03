import unittest

from apm import *
from apm.patterns import *


class BasicUseCases(unittest.TestCase):

    def test_regex(self):
        pass

    def test_remaining(self):
        match([1, 2, 3, 4],
              [1, 2, 3, Remaining(InstanceOf(int), at_least=1)])
        pass


if __name__ == '__main__':
    unittest.main()
