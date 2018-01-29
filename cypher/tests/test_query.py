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
    # def test_represent(self):
    #     class Human(Node):
    #         stuff = Props.Boolean()
    #         age = Props.Integer()
    #         height = Props.Float()
    #         nationality = Props.String(required=False)
    #
    #     human = Human(
    #         stuff=True,
    #         age=30,
    #         height=2,
    #         uid='uid',
    #     )
    #     expected = ':Human {age: 30, height: 2.0, stuff: true, uid: "uid"}'
    #
    #     self.assertEqual(Query.represent(human), expected)

    def test_match(self):
        """
        The most simple `match` scenario.
        """
        class Human(Node):
            pass

        query = Query().match(Human).result(no_exec=True)
        expected = (
            'MATCH (a:Human)'
            '\nRETURN a'
        )
        self.assertEqual(query, expected)

        query = Query().match((Human, 'a')).result(no_exec=True)
        expected = (
            'MATCH (_a:Human)'
            '\nRETURN _a'
        )
        self.assertEqual(query, expected)
