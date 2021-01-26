import numbers
import unittest

from apm import *


class ReportingTest(unittest.TestCase):
    instance_of = InstanceOf(numbers.Number)
    each = Each(instance_of)

    def test_match_stack(self):
        result = match([1, 2, "uvw", 4], self.each)
        self.assertFalse(result)
        self.assertEqual(([1, 2, 'uvw', 4], 'uvw'), tuple(k for k, _v in result._match_stack))
        self.assertEqual((
            self.each,
            self.instance_of,
        ), tuple(v for _k, v in result._match_stack))

    def test_explain(self):
        result = match([1, 2, "uvw", 4], self.each)
        self.assertEqual(
            f"[1, 2, 'uvw', 4]\n"
            f"...did not match the pattern:\n"
            f"{repr(self.each)}\n"
            f"...because:\n"
            f"uvw\n"
            f"...did not match the pattern:\n"
            f"{repr(self.instance_of)}", result.explain())


if __name__ == '__main__':
    unittest.main()
