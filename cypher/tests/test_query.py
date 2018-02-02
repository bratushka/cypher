"""
Tests for `query.py`.
"""
from datetime import date
from unittest import TestCase

from ..props import Props
from ..models import Edge, Node
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

    def test_match_by_none(self):
        """
        Match all the nodes.
        """
        query = Query().match(None).result(no_exec=True)
        expected = (
            'MATCH (_a)\n'
            'RETURN _a'
        )
        self.assertEqual(query, expected)

    def test_defined_result(self):
        """
        Pass variables to the `result` method.
        """
        query = Query().match((None, 'a')).match(None).result('a', no_exec=True)
        expected = (
            'MATCH (a)\n'
            'MATCH (_a)\n'
            'RETURN a'
        )
        self.assertEqual(query, expected)

    def test_match_path(self):
        """
        Match a path.
        """
        query = Query()\
            .match(None)\
            .connected_through(None)\
            .with_(None)\
            .result(no_exec=True)
        expected = (
            'MATCH _p1 = (_a)-[_b]-(_c)\n'
            'RETURN _a, _b, _c'
        )
        self.assertEqual(query, expected)

    def test_match_double_path(self):
        """
        A matching chain should split into 2 MATCH statements.
        """
        class User(Node):
            """
            Example of Node.
            """
            pass

        class Knows(Edge):
            """
            Example of Edge.
            """
            pass

        query = Query()\
            .match((None, 'b'))\
            .connected_through((Knows, 'a'))\
            .with_(User)\
            .connected_through(None)\
            .with_(User)\
            .result(no_exec=True)
        expected = (
            'MATCH _p1 = (b)-[a:Knows]-(_a:User)\n'
            'MATCH _p2 = (_a)-[_b]-(_c:User)\n'
            'RETURN b, a, _a, _b, _c'
        )
        self.assertEqual(query, expected)

    def test_connected_through_with_connection_length(self):
        """
        Pass `conn` argument to the `connected_through` method.
        """
        # pylint: disable=invalid-name
        # This suppresses error for the method name.
        # pylint: enable=no-member
        class User(Node):
            """
            Example of Node.
            """

        class Knows(Edge):
            """
            Example of edge.
            """

        query = Query()\
            .match(User)\
            .connected_through(Knows, conn=(1, 3))\
            .with_(User)\
            .result(no_exec=True)
        expected = (
            'MATCH _p1 = (_a:User)-[:Knows *1..3]-(_c:User)\n'
            # 'RETURN _a, relationships(_p1) as _b, _c'
            'RETURN _a, _b, _c'
        )
        self.assertEqual(query, expected)
