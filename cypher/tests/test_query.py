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

    def test_match_path_no_direction(self):
        """
        Match a path with front or back direction.
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

    def test_match_path_back_direction(self):
        """
        Match a path with back direction.
        """
        query = Query()\
            .match(None)\
            .connected_through(None)\
            .by(None)\
            .result(no_exec=True)
        expected = (
            'MATCH _p1 = (_a)<-[_b]-(_c)\n'
            'RETURN _a, _b, _c'
        )
        self.assertEqual(query, expected)

    def test_match_path_front_direction(self):
        """
        Match a path with front direction.
        """
        query = Query()\
            .match(None)\
            .connected_through(None)\
            .to(None)\
            .result(no_exec=True)
        expected = (
            'MATCH _p1 = (_a)-[_b]->(_c)\n'
            'RETURN _a, _b, _c'
        )
        self.assertEqual(query, expected)

    def test_path_with_edge_instance(self):
        """
        Match a path with edge instance instead of edge model.
        """
        class Knows(Edge):
            """
            Example of Edge.
            """
            pass

        instance = Knows(uid='instance_uid')
        query = Query()\
            .match(None)\
            .connected_through(instance)\
            .to(None)\
            .result(no_exec=True)
        expected = (
            'MATCH _p1 = (_a)-[_b:Knows]->(_c)\n'
            'WHERE _b.uid = "instance_uid"\n'
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
            'RETURN _a, relationships(_p1) as _b, _c'
        )
        self.assertEqual(query, expected)


class MegaTests(TestCase):
    """
    Complex tests to cover everything.
    """
    def test_match(self):
        """
        Test `match` query.
        """
        class User(Node):
            """
            Example of Node.
            """
            name = Props.String()

        class Knows(Edge):
            """
            Example of edge.
            """
            since = Props.Date()

        user = User(name='John', uid='john')
        knows = Knows(since=date(1, 2, 3), uid='knows')

        query = Query()\
            .match(None)\
            \
            .match(User, User.uid == 'some_uid', User.name == 'Kate')\
            \
            .match(user)\
            \
            .match(User)\
            .connected_through(Knows, conn=(1, 3))\
            .with_(None)\
            \
            .match(None)\
            .connected_through(None)\
            .with_(User)\
            \
            .match(user)\
            .connected_through(knows)\
            .with_((None, 'blah'))\
            \
            .result(no_exec=True)
        expected = (
            'MATCH (_a)\n'
            'MATCH (_b:User)\n'
            'WHERE _b.uid = "some_uid"\n'
            '  AND _b.name = "Kate"\n'
            'MATCH (_c:User)\n'
            'WHERE _c.uid = "john"\n'
            'MATCH _p1 = (_d:User)-[:Knows *1..3]-(_f)\n'
            'MATCH _p2 = (_g)-[_h]-(_i:User)\n'
            'MATCH _p3 = (_j:User)-[_k:Knows]-(blah)\n'
            'WHERE _j.uid = "john"\n'
            '  AND _k.uid = "knows"\n'
            'RETURN _a, _b, _c, _d, relationships(_p1) as _e,'  # no new line
            ' _f, _g, _h, _i, _j, _k, blah'
        )

        self.assertEqual(query, expected)

# @TODO: ^ should be like below
# MATCH (_a)
# MATCH (_b:User)
# WHERE _b.uid = "some_uid"
#   AND _b.name = "Kate"
# MATCH (_c:User)
# WHERE _c.uid = "john"
# MATCH _p1 = (_d:User)-[:Knows *1..3]-(_f)
# WITH *, relationships(_p1) as _e
# WHERE all(el in _e WHERE el.since > 34)
# MATCH _p2 = (_g)-[_h]-(_i:User)
# MATCH _p3 = (_j:User)-[_k:Knows]-(blah)
# WHERE _j.uid = "john"
#   AND _k.uid = "knows"
# RETURN _a, _b, _c, _d, _e, _f, _g, _h, _i, _j, _k, blah
