"""
Tests for `props.py`.
"""
from datetime import date, datetime
from unittest import TestCase

from cypher.props import BaseProp, Props


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
