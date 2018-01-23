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
    def test_represent(self):
        class Human(Node):
            stuff = Props.Boolean()
            age = Props.Integer()
            height = Props.Float()
            nationality = Props.String(required=False)

        human = Human(
            stuff=True,
            age=30,
            height=2,
            uid='uid',
        )
        expected = ':Human {age: 30, height: 2.0, stuff: true, uid: "uid"}'

        self.assertEqual(Query.represent(human), expected)

    # def test_create(self):
    #     """
    #     The most simple `create` scenario.
    #     """
    #     class Human(Node):
    #         name = Props.String()
    #
    #     human = Human(name='John')
    #     query = Query().create(human).result(no_exec=True)
    #     expected = (
    #         'CREATE'
    #         '    (a:Human {name: "John"})'
    #         'RETURN a'
    #     )
    #
    #     self.assertEqual(query, expected)
