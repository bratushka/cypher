"""
Tests for `query.py`.
"""
from unittest import TestCase

from ..props import Props
from ..models import Node
from ..query import Query


class QueryTests(TestCase):
    """
    Test building queries.
    """
    def test_create(self):
        """
        The most simple `create` scenario.
        """
        class Human(Node):
            name = Props.String()

        human = Human(name='John')
        query = Query().create(human).result(no_exec=True)
        expected = (
            'CREATE'
            '    (a:Human {name: "John"})'
            'RETURN a'
        )

        self.assertEqual(query, expected)
