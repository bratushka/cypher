"""
Tests for `query.py`.
"""
from unittest import TestCase

from ..props import Props
from ..models import Node
from ..query import Query


class MatchTests(TestCase):
    """
    Test building queries.
    """
    def test_match_by_class(self):
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

    def test_match_by_instance(self):
        """
        The most simple `match` scenario.
        """
        class Human(Node):
            pass

        human = Human(uid='human_uid')

        query = Query().match(human).result(no_exec=True)
        expected = (
            'MATCH (a:Human)'
            '\nWHERE a.uid = "human_uid"'
            '\nRETURN a'
        )
        self.assertEqual(query, expected)

    def test_combined_match_by_class(self):
        """
        The most simple `match` scenario.
        """
        class Human(Node):
            pass

        class Animal(Node):
            pass

        query = Query().match(Human).match(Animal).result(no_exec=True)
        expected = (
            'MATCH (a:Human)'
            '\nMATCH (b:Animal)'
            '\nRETURN a, b'
        )
        self.assertEqual(query, expected)

    def test_combined_match_by_class_and_instance(self):
        """
        The most simple `match` scenario.
        """
        class Human(Node):
            pass

        class Animal(Node):
            pass

        human = Human(uid='human_uid')
        query = Query().match(human).match(Animal).result(no_exec=True)
        expected = (
            'MATCH (a:Human)'
            '\nWHERE a.uid = "human_uid"'
            '\nMATCH (b:Animal)'
            '\nRETURN a, b'
        )
        self.assertEqual(query, expected)
