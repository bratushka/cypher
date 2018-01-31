"""
Tests for `query.py`.
"""
from datetime import date
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
            """
            Example of Node.
            """
            pass

        query = Query().match(Human).result(no_exec=True)
        expected = (
            'MATCH (_a:Human)\n'
            'RETURN _a'
        )
        self.assertEqual(query, expected)

    def test_match_by_instance(self):
        """
        Match by class + add condition by instance.
        """
        class Human(Node):
            """
            Example of Node.
            """
            pass

        human = Human(uid='human_uid')

        query = Query().match(human).result(no_exec=True)
        expected = (
            'MATCH (_a:Human)\n'
            'WHERE _a.uid = "human_uid"\n'
            'RETURN _a'
        )
        self.assertEqual(query, expected)

    def test_combined_match_by_class(self):
        """
        Combination of 2 most simple `match` scenarios.
        """
        class Human(Node):
            """
            Example of Node.
            """
            pass

        class Animal(Node):
            """
            Example of Node.
            """
            pass

        query = Query().match(Human).match(Animal).result(no_exec=True)
        expected = (
            'MATCH (_a:Human)\n'
            'MATCH (_b:Animal)\n'
            'RETURN _a, _b'
        )
        self.assertEqual(query, expected)

    def test_combined_match_by_class_and_instance(self):
        """
        Combination of matching by class and instance.
        """
        # pylint: disable=invalid-name
        # This suppresses error for the method name.
        # pylint: enable=no-member
        class Human(Node):
            """
            Example of Node.
            """
            pass

        class Animal(Node):
            """
            Example of Node.
            """
            pass

        human = Human(uid='human_uid')
        query = Query()\
            .match(human)\
            .match(Animal)\
            .result(no_exec=True)
        expected = (
            'MATCH (_a:Human)\n'
            'WHERE _a.uid = "human_uid"\n'
            'MATCH (_b:Animal)\n'
            'RETURN _a, _b'
        )
        self.assertEqual(query, expected)

    def test_match_by_class_with_comparison(self):
        """
        Add a `where` to the most simple `match` scenario.
        """
        # pylint: disable=invalid-name
        # This suppresses error for the method name.
        # pylint: enable=no-member
        class Human(Node):
            """
            Example of Node.
            """
            admin = Props.Boolean()
            dob = Props.Date()
            name = Props.String()

        query = Query()\
            .match(
                Human,
                # pylint: disable=singleton-comparison
                Human.admin == True,
                # pylint: enable=singleton-comparison
                Human.dob > date(1, 2, 3),
                Human.name @ ['q', 'w', 'e'],
            )\
            .result(no_exec=True)
        expected = (
            'MATCH (_a:Human)\n'
            'WHERE _a.admin = true\n'
            '  AND _a.dob > 34\n'
            '  AND _a.name IN ["q", "w", "e"]\n'
            'RETURN _a'
        )
        self.assertEqual(query, expected)
