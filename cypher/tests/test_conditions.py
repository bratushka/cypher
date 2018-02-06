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
        actual = (Value('name') == 'some"nameЖ')('a')
        expected = 'a.name = "some\\"nameЖ"'
        self.assertEqual(actual, expected)

        actual = (Value('a.name') > Value('b.email'))('c')
        expected = 'a.name > b.email'
        self.assertEqual(actual, expected)

    def test_to_bool(self):
        """
        Test `to_bool` transformation.
        """
        actual = (Value('name').to_bool() == 'some"nameЖ')('a')
        expected = 'toBoolean(a.name) = true'
        self.assertEqual(actual, expected)
