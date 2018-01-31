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

    def test_labels(self):
        """
        Test labels setter and getter.
        """
        class SomeModel(Model):
            """
            Synthetic model type.
            """

        instance = SomeModel()
        self.assertEqual(instance.labels, {'SomeModel'})

        instance.labels = ('Label',)
        self.assertEqual(instance.labels, {'SomeModel', 'Label'})

        instance.labels = ('Label', 'SomeModel', 'Node')
        self.assertEqual(instance.labels, {'SomeModel', 'Label', 'Node'})

        with self.assertRaises(TypeError):
            instance.labels = (1,)

    def test_props(self):
        """
        Test props setter and getter.
        """
        class SomeModel(Model):
            """
            Synthetic model type.
            """

        instance = SomeModel(name='John', age=34)
        with self.assertRaises(AttributeError):
            # pylint: disable=pointless-statement
            # noinspection PyStatementEffect,PyUnresolvedReferences
            instance.name
            # pylint: enable=pointless-statement

        self.assertEqual(instance.props, {'name': 'John', 'age': 34})

        instance.props['is_admin'] = True
        self.assertEqual(
            instance.props,
            {'name': 'John', 'age': 34, 'is_admin': True},
        )
