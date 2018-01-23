"""
Tests for `props.py`.
"""
from datetime import date, datetime
from unittest import TestCase

from ..props import BaseProp, Props


class BasePropsTests(TestCase):
    """
    Tests for the BaseProp class
    """
    def test_validate_type(self):
        """
        Validation should not allow assigning values of wrong types.
        """
        class SomeValue:
            pass

        class SomeProp(BaseProp):
            types = (SomeValue,)

        with self.assertRaises(TypeError):
            SomeProp.validate_type('some_value')
        SomeProp.validate_type(SomeValue())

    def test_validate_rules(self):
        """
        Validation should not allow assigning values which don't follow the
        rules.
        """
        class SomeProp(BaseProp):
            types = (int,)
            rules = (lambda x: x < 0,)

        with self.assertRaises(ValueError):
            SomeProp.validate_rules(1)
        SomeProp.validate_type(-1)

    def test_normalize(self):
        """
        In simple cases `normalize` should return the same value.
        """
        class SomeProp(BaseProp):
            pass

        values = [True, 'string']
        for value in values:
            self.assertIs(value, SomeProp.normalize(value))

    def test_to_cypher_value(self):
        """
        In simple cases `to_cypher_value` should return the same value.
        """
        class SomeProp(BaseProp):
            pass

        values = [True, 1, 1., 'str"ing']
        expected_values = ['true', '1', '1.0', '"str\\"ing"']
        for value, expected in zip(values, expected_values):
            self.assertEqual(SomeProp.to_cypher_value(value), expected)

    def test_to_python_value(self):
        """
        In simple cases `to_python_value` should return the same value.
        """
        class SomeProp(BaseProp):
            pass

        values = [True, 1, 1., 'string']
        for value in values:
            self.assertIs(value, SomeProp.to_python_value(value))


class BooleanTests(TestCase):
    """
    Tests for Props.Boolean class.
    """
    def test_types(self):
        """
        Should accept only boolean values.
        """
        Props.Boolean.validate(True)

        for t in (int, float, str):
            with self.assertRaises(TypeError):
                Props.Boolean.validate(t(True))


class IntegerTests(TestCase):
    """
    Tests for Props.Integer class.
    """
    def test_types(self):
        """
        Should accept only integer values.
        """
        Props.Integer.validate(1)

        for t in (float, str):
            with self.assertRaises(TypeError):
                Props.Integer.validate(t(1))

    def test_rules(self):
        """
        Should accept values smaller than 2**63 and greater or equal to 2**63.
        """
        Props.Integer.validate(2**63 - 1)
        Props.Integer.validate(-2**63)

        with self.assertRaises(ValueError):
            Props.Integer.validate(2**63)
        with self.assertRaises(ValueError):
            Props.Integer.validate(-2**63 - 1)


class FloatTests(TestCase):
    """
    Tests for Props.Float class.
    """
    def test_types(self):
        """
        Should accept float and integer values.
        """
        Props.Float.validate(1.)
        Props.Float.validate(1)

        with self.assertRaises(TypeError):
            Props.Float.validate('1.')

    def test_normalize(self):
        """
        `normalize` should return float.
        """
        values = [True, 1, 1., 1.1, -1, -1.]
        expected_values = [1., 1., 1., 1.1, -1., -1.]

        for value, expected in zip(values, expected_values):
            self.assertEqual(Props.Float.normalize(value), expected)


class StringTests(TestCase):
    """
    Tests for Props.String class.
    """
    def test_types(self):
        """
        Should accept only string values.
        """
        Props.String.validate('String value')

        for t in (int, float, bool):
            with self.assertRaises(TypeError):
                Props.String.validate(t('1'))


class DateTests(TestCase):
    """
    Tests for Props.Date class.
    """
    def test_types(self):
        """
        Should accept date and datetime values.
        """
        Props.Date.validate(date(2000, 1, 1))
        Props.Date.validate(datetime(2000, 1, 1, 1, 1, 1))

        for t in (int, float, bool):
            with self.assertRaises(TypeError):
                Props.String.validate(t('1'))

    def test_normalize(self):
        """
        `normalize` should return `date`.
        """
        values = [date(2000, 1, 2), datetime(2000, 1, 2, 3, 4, 5)]
        expected_values = [date(2000, 1, 2), date(2000, 1, 2)]

        for value, expected in zip(values, expected_values):
            self.assertEqual(Props.Date.normalize(value), expected)

    def test_to_cypher_value(self):
        """
        `to_cypher_value` should transform `date` to `int`.
        """
        values = [date(1, 1, 1), date(1, 2, 1)]
        expected_values = ["1", "32"]

        for value, expected in zip(values, expected_values):
            self.assertEqual(Props.Date.to_cypher_value(value), expected)

    def test_to_python_value(self):
        """
        `to_python_value` should transform `int` to `date`.
        """
        values = [1, 32]
        expected_values = [date(1, 1, 1), date(1, 2, 1)]

        for value, expected in zip(values, expected_values):
            self.assertEqual(Props.Date.to_python_value(value), expected)


class DateTimeTests(TestCase):
    """
    Tests for Props.DateTime class.
    """
    def test_types(self):
        """
        Should accept date and datetime values.
        """
        Props.DateTime.validate(date(2000, 1, 1))
        Props.DateTime.validate(datetime(2000, 1, 1, 1, 1, 1))

        for t in (int, float, bool):
            with self.assertRaises(TypeError):
                Props.String.validate(t('1'))

    def test_normalize(self):
        """
        `normalize` should return `datetime`.
        """
        values = [date(2000, 1, 2), datetime(2000, 1, 2, 3, 4, 5)]
        expected_values = [
            datetime(2000, 1, 2, 0, 0, 0),
            datetime(2000, 1, 2, 3, 4, 5),
        ]

        for value, expected in zip(values, expected_values):
            self.assertEqual(Props.DateTime.normalize(value), expected)

    def test_to_cypher_value(self):
        """
        `to_cypher_value` should transform `datetime` to `int` microtimestamp.
        """
        values = [
            datetime(1970, 1, 1, 0, 0, 0, 1),
            datetime(1970, 1, 1, 0, 0, 1, 1),
        ]
        expected_values = ["1", "1000001"]

        for value, expected in zip(values, expected_values):
            self.assertEqual(Props.DateTime.to_cypher_value(value), expected)

    def test_to_python_value(self):
        """
        `to_python_value` should transform `int` microtimestamp to `datetime`.
        """
        values = [1, 1_000_001]
        expected_values = [
            datetime(1970, 1, 1, 0, 0, 0, 1),
            datetime(1970, 1, 1, 0, 0, 1, 1),
        ]

        for value, expected in zip(values, expected_values):
            self.assertEqual(Props.DateTime.to_python_value(value), expected)
