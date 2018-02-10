"""
Tests for `values.py`.
"""
from datetime import date, datetime
from unittest import TestCase

from .. import values


class ValuesTests(TestCase):
    """
    Tests for the Values class.
    """
    def test_validate_type(self):
        """
        Validation should not allow assigning values of wrong types.
        """
        class SomeObject:
            """
            Synthetic type.
            """

        class SomeValue(values.Value):
            """
            Example of Value.
            """
            types = (SomeObject,)

        with self.assertRaises(TypeError):
            SomeValue.validate_type('some_value')
        SomeValue.validate_type(SomeObject())

    def test_validate_constraints(self):
        """
        Validation should not allow assigning values which don't meet the
        constraints.
        """
        class SomeValue(values.Value):
            """
            Example of Value.
            """
            types = (int,)
            constraints = (lambda x: x < 0,)

        with self.assertRaises(ValueError):
            SomeValue.validate_constraints(1)
        SomeValue.validate_constraints(-1)

    def test_normalize(self):
        """
        In simple cases `normalize` should return the same value.
        """
        class SomeValue(values.Value):
            """
            Example of Value.
            """

        examples = [True, 'string']
        for example in examples:
            self.assertIs(example, SomeValue.normalize(example))

    def test_to_cypher_value(self):
        """
        In simple cases `to_cypher_value` should return the same value.
        """
        class SomeValue(values.Value):
            """
            Example of Value.
            """

        examples = [True, 1, 1., 'str"ing']
        expected_values = ['true', '1', '1.0', '"str\\"ing"']
        for example, expected in zip(examples, expected_values):
            self.assertEqual(SomeValue.to_cypher_value(example), expected)

    def test_to_python_value(self):
        """
        In simple cases `to_python_value` should return the same value.
        """
        class SomeValue(values.Value):
            """
            Example of Value.
            """
            pass

        examples = [True, 1, 1., 'string']
        for example in examples:
            self.assertIs(example, SomeValue.to_python_value(example))


class BooleanTests(TestCase):
    """
    Tests for Boolean class.
    """
    def test_normalize(self):
        """
        Should convert all the values to boolean.
        """
        for example, expected in zip(
                (True, 0, 2, 2.2, 'str', [], ['list']),
                (True, False, True, True, True, False, True),
        ):
            self.assertIs(values.Boolean.normalize(example), expected)


class IntegerTests(TestCase):
    """
    Tests for Integer class.
    """
    def test_types(self):
        """
        Should accept only integer values.
        """
        values.Integer.validate(1)

        for cls in (float, str):
            with self.assertRaises(TypeError):
                values.Integer.validate(cls(1))

    def test_constraints(self):
        """
        Should accept values smaller than 2**63 and greater or equal to 2**63.
        """
        values.Integer.validate(2**63 - 1)
        values.Integer.validate(-2**63)

        with self.assertRaises(ValueError):
            values.Integer.validate(2**63)
        with self.assertRaises(ValueError):
            values.Integer.validate(-2**63 - 1)


class FloatTests(TestCase):
    """
    Tests for Float class.
    """
    def test_types(self):
        """
        Should accept float and integer values.
        """
        values.Float.validate(1.)
        values.Float.validate(1)

        with self.assertRaises(TypeError):
            values.Float.validate('1.')

    def test_normalize(self):
        """
        `normalize` should return float.
        """
        examples = [True, 1, 1., 1.1, -1, -1.]
        expected_values = [1., 1., 1., 1.1, -1., -1.]

        for example, expected in zip(examples, expected_values):
            self.assertEqual(values.Float.normalize(example), expected)


class StringTests(TestCase):
    """
    Tests for String class.
    """
    def test_types(self):
        """
        Should accept only string values.
        """
        values.String.validate('String value')

        for cls in (int, float, bool):
            with self.assertRaises(TypeError):
                values.String.validate(cls('1'))


class DateTests(TestCase):
    """
    Tests for Date class.
    """
    def test_types(self):
        """
        Should accept date and datetime values.
        """
        values.Date.validate(date(2000, 1, 1))
        values.Date.validate(datetime(2000, 1, 1, 1, 1, 1))

        for cls in (int, float, bool):
            with self.assertRaises(TypeError):
                values.String.validate(cls('1'))

    def test_normalize(self):
        """
        `normalize` should return `date`.
        """
        examples = [date(2000, 1, 2), datetime(2000, 1, 2, 3, 4, 5)]
        expected_values = [date(2000, 1, 2), date(2000, 1, 2)]

        for example, expected in zip(examples, expected_values):
            self.assertEqual(values.Date.normalize(example), expected)

    def test_to_cypher_value(self):
        """
        `to_cypher_value` should transform `date` to `int`.
        """
        examples = [date(1, 1, 1), date(1, 2, 1)]
        expected_values = ["1", "32"]

        for example, expected in zip(examples, expected_values):
            self.assertEqual(values.Date.to_cypher_value(example), expected)

    def test_to_python_value(self):
        """
        `to_python_value` should transform `int` to `date`.
        """
        examples = [1, 32]
        expected_values = [date(1, 1, 1), date(1, 2, 1)]

        for example, expected in zip(examples, expected_values):
            self.assertEqual(values.Date.to_python_value(example), expected)


class DateTimeTests(TestCase):
    """
    Tests for DateTime class.
    """
    def test_types(self):
        """
        Should accept date and datetime values.
        """
        values.DateTime.validate(date(2000, 1, 1))
        values.DateTime.validate(datetime(2000, 1, 1, 1, 1, 1))

        for cls in (int, float, bool):
            with self.assertRaises(TypeError):
                values.String.validate(cls('1'))

    def test_normalize(self):
        """
        `normalize` should return `datetime`.
        """
        examples = [date(2000, 1, 2), datetime(2000, 1, 2, 3, 4, 5)]
        expected_values = [
            datetime(2000, 1, 2, 0, 0, 0),
            datetime(2000, 1, 2, 3, 4, 5),
        ]

        for example, expected in zip(examples, expected_values):
            self.assertEqual(values.DateTime.normalize(example), expected)

    def test_to_cypher_value(self):
        """
        `to_cypher_value` should transform `datetime` to `float` timestamp.
        """
        examples = [
            datetime(1970, 1, 1, 0, 0, 0, 1),
            datetime(1970, 1, 1, 0, 0, 1, 1),
        ]
        expected_values = [str(0.000001), str(1.000001)]

        for example, expected in zip(examples, expected_values):
            self.assertEqual(values.DateTime.to_cypher_value(example), expected)

    def test_to_python_value(self):
        """
        `to_python_value` should transform `int` microtimestamp to `datetime`.
        """
        examples = [0.000001, 1.000001]
        expected_values = [
            datetime(1970, 1, 1, 0, 0, 0, 1),
            datetime(1970, 1, 1, 0, 0, 1, 1),
        ]

        for example, expected in zip(examples, expected_values):
            self.assertEqual(values.DateTime.to_python_value(example), expected)
