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
            """
            Synthetic model type.
            """
            boolean = Props.Boolean(required=False)
            string = Props.String()
            partial = Props.Float(default=2)

        with self.assertRaises(ValueError):
            SomeModel()

        instance = SomeModel(string='string')
        self.assertEqual(instance.boolean, None)
        self.assertEqual(instance.string, 'string')
        self.assertEqual(instance.partial, 2.)

        with self.assertRaises(TypeError):
            SomeModel(string=2)

        instance = SomeModel(boolean=False, string='string', partial=3)
        self.assertEqual(instance.boolean, False)
        self.assertEqual(instance.string, 'string')
        self.assertEqual(instance.partial, 3.)
