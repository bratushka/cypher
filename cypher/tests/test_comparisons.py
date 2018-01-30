"""
Tests for `comparisons.py`.
"""
from datetime import date
from unittest import TestCase

from ..comparisons import Comparison
from ..models import Node
from ..props import Props


class ComparisonTests(TestCase):
    """
    Tests for `Comparison` comparisons.
    """
    def test_stringify(self):
        """
        An equality should be stringified correctly.
        """
        class Frobnicates(Comparison):
            """
            Example of comparison.
            """
            operator = 'FROBNICATES'

        class Person(Node):
            """
            Example of Node.
            """
            age = Props.Integer()
            date = Props.Date()

        instances = (
            Frobnicates(Person, 'a', 'uid', 'c"'),
            Frobnicates(Person, 'a', 'age', 55),
            Frobnicates(Person, 'a', 'date', date(1, 2, 3)),
        )
        strings = (
            'a.uid FROBNICATES "c\\""',
            'a.age FROBNICATES 55',
            'a.date FROBNICATES 34',
        )

        for actual, expected in zip(instances, strings):
            self.assertEqual(actual.stringify(), expected)
