"""
Tests for `models.py`.
"""
from unittest import TestCase

from ..props import Props
from ..models import Model


class ModelTests(TestCase):
    """
    Test common functionality of Node and Edge.
    """
    def test_init(self):
        """
        Test the model instantiation.
        """
        class SomeModel(Model):
            string = Props.String()
            integer = Props.Integer(default=2)

        with self.assertRaises(ValueError):
            SomeModel()

        instance = SomeModel(string='string')
        self.assertEqual(instance.string, 'string')
        self.assertEqual(instance.integer, 2)

        with self.assertRaises(TypeError):
            SomeModel(string=2)

        instance = SomeModel(string='string', integer=3)
        self.assertEqual(instance.string, 'string')
        self.assertEqual(instance.integer, 3)
