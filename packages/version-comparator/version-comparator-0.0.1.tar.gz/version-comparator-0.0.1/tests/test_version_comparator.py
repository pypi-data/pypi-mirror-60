import unittest

from src.version_comparator.comparator import compare_versions


class TestVersionComparator(unittest.TestCase):
    def test_error_not_a_string(self):
        with self.assertRaises(ValueError):
            compare_versions('1.2.4', (1, 2))

    def test_error_none_input(self):
        with self.assertRaises(ValueError):
            compare_versions(None, '1.2.3')

    def test_equal_version_same_length(self):
        self.assertEqual(compare_versions('1.2.1', '1.2.1'), 0)

    def test_equal_version_bigger_versions(self):
        self.assertEqual(compare_versions('1.2.1.0.1', '1.2.1.0.1'), 0)

    def test_equal_version_special_versions(self):
        self.assertEqual(compare_versions('3.0.1.b0', '3.0.1.b0'), 0)

    def test_equal_version_same_length_all_zero(self):
        self.assertEqual(compare_versions('0.0.0', '0.0.0'), 0)

    def test_equal_version_bigger_versions_length_all_zero(self):
        self.assertEqual(compare_versions('0.0.0.0.0', '0.0.0.0.0'), 0)

    def test_equal_version_special_versions_length_all_zero(self):
        self.assertEqual(compare_versions('0.0.0a', '0.0.0a'), 0)

    def test_greater_version_same_length(self):
        self.assertGreater(compare_versions('1.2.3', '1.2.1'), 0)

    def test_greater_version_bigger_versions(self):
        self.assertGreater(compare_versions('1.2.1.0.2', '1.2.1.0.1'), 0)

    def test_greater_version_special_versions(self):
        self.assertGreater(compare_versions('3.0.1.rc0', '3.0.1.b0'), 0)

    def test_less_version_same_length(self):
        self.assertLess(compare_versions('5.5.1', '5.5.3'), 0)

    def test_less_version_bigger_versions(self):
        self.assertLess(compare_versions('1.1.1.0.1', '1.2.1.0.1'), 0)

    def test_less_version_special_versions(self):
        self.assertLess(compare_versions('1.0.1.a0', '1.0.1.b0'), 0)

    def test_less_version_special_versions_mixed(self):
        self.assertLess(compare_versions('1  .0.0.0. 0', ' 5',), 0)

    def test_less_version_mixed_length(self):
        self.assertLess(compare_versions('5.5.1.0.b', '5.5.3'), 0)


if __name__ == "__main__":
    unittest.main()
