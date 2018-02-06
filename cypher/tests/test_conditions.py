"""
Tests for conditions.py.
"""
import unittest

from ..conditions import Value


class ValueTests(unittest.TestCase):
    """
    Tests for `Value` class.
    """
    def test_eq(self):
        """
        Test equality condition.
        """
        actual = Value('a', 'name') == 'some"nameЖ'
        expected = 'a.name = "some\\"nameЖ"'
        self.assertEqual(actual, expected)

        actual = Value('a', 'name') == Value('b', 'email')
        expected = 'a.name = b.email'
        self.assertEqual(actual, expected)
